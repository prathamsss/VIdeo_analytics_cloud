""" Video Analytics Pipeline App- All modules running in parallel with Multithreading,
using data coming from KVS and consuming to KDS
"""

import concurrent.futures
from threading import Thread
import os
from time import sleep
from pprint import pprint
import cv2
import json
from model_detections import ModelDetections
from static_object_detection import StaticObjectDetection
from kinesisUtils.KVS.KVSConsumer import Consume
from kinesisUtils.KDS.KDSProduce import Produce

KVS_STREAM = os.environ["KVS_STREAM"]
KDS_STREAM = os.environ["KDS_STREAM"]

# QUIT flag - to stop producer, consumer and inference
# thread safely, whe, there is Keyboard interrupt
QUIT = False

detect = ModelDetections()

consumer = Consume(KVS_STREAM)
producer = Produce(KDS_STREAM)


# Dictionary - To catch data coming from each VA module.
return_response = {}
# List - To catch incoming response from kvs stream.
return_response_kvs = []
# List  - To store & send entire VA metadata per frame.
inference_list = []

static_object = StaticObjectDetection(consumer,
                                      float(os.environ
                                            ["INTERSECTION_THRESHOLD"]),
                                      int(os.environ["THRESHOLD_TIME"]))


def loop_kvs_consume():
    """
    KVS Consumer Loop: This method populates the response
    by consuming frames coming from stream.
    :return:
    """
    global WAIT_FLAG
    WAIT_FLAG = False
    while True:
        try:
            consumer.run(return_response_kvs)
            if WAIT_FLAG:
                WAIT_FLAG = False
        except ValueError as value_error:
            if str(value_error) == "Tags not found":
                # Waiting for 5 secs if producer not producing anything
                WAIT_FLAG = True
                print("kvs loop sleeping")
                sleep(5)
                continue
        except Exception as kvs_error:
            print(str(kvs_error))
            continue
        if QUIT:
            break


def inference_loop():
    """
    Method to do inference on KVS
    stream with all VA Modules.
    :return: Creates metadata of response
    from respective VA Modules
    """
    # last_tag - used to parse timestamp.
    last_tag = ""
    # id_count - used been used for static object detection as frame count.
    id_count = 0
    while True:
        if WAIT_FLAG:
            print("inference loop sleeping")
            sleep(5)
        elif QUIT:
            break
        # Here we get a frame w.r.t time associated with it.
        # tags is timestamp of that frame.
        try:
            tags, frame = return_response_kvs.pop(0)
            if last_tag == "":
                last_tag = tags[0]
        except IndexError:
            continue
        except Exception as frame_error:
            print(str(frame_error))
            continue

        if last_tag == tags[0]:
            continue

        # Here we convert numpy image into bytes
        _, image_bytes = cv2.imencode(".jpg", frame)

        # Threading  AWS rekognition tasks together
        #     1) Object detection
        #     2) Face detection
        #     3) PPE detection
        #     4) Face Search
        #     5) Static Object Detection
        #     6) YOLO Object detection

        # Incoming list from USER (from producer metadata)
        modules_list =[]
        # modules_list = ["ppe_detection","face_detection"]

        # Dictionary of all VA modules, where -
        # keys: "name_of_va_module" &
        # values:  List of va function & it's params.
        modules_dict = {
            "object_detection": [detect.object_detection,
                                 image_bytes.tobytes(), 10,
                                 None, return_response],
            "face_detection": [detect.detection_faces,
                               image_bytes.tobytes(),
                               return_response],
            "ppe_detection": [detect.detection_ppe,
                              image_bytes.tobytes(),
                              return_response],
            "face_search": [detect.face_search,
                            image_bytes.tobytes(),
                            80, 2, return_response],
            "static_object": [static_object.detect_static_object,
                              image_bytes.tobytes(),
                              id_count, 20, "Person",
                              return_response],
            "yolo_detector": [detect.yolo_detector,
                              image_bytes.tobytes(),
                              return_response]

        }

        # Create a threadingpoolexcecuter for tasks given in list from user
        if not modules_list:
            modules_list = list(modules_dict.keys())

        for module in modules_list:
            task_to_submit = modules_dict[module][0]
            task_args = modules_dict[module][1:]
            with concurrent.futures.ThreadPoolExecutor(12) as module_executor:
                module_executor.submit(task_to_submit, *task_args)

        metadata_schema = {
            "frame_data": [],
            "timestamp": tags[0]
        }

        # Create a copy of metadata for each inference on the frame captured
        metadata = metadata_schema.copy()

        # Converting AWS rekognition response according
        # to the requirements for KDS metadata production
        # Appending the inferences to frame_data(array) in the metadata

        # Object detection metadata parsing
        try:
            object_detection_response = \
                return_response["object_detection"]["Labels"]
            metadata["frame_data"].append(
                {
                    "inference_type": "object_detection",
                    "boxes": [],
                }
            )

            for _, label in enumerate(object_detection_response):
                for i in range(len(label["Instances"])):
                    metadata["frame_data"][-1]["boxes"].append({
                    "width": label["Instances"][i]["BoundingBox"]["Width"],
                    "height": label["Instances"][i]["BoundingBox"]["Height"],
                    "row": label["Instances"][i]["BoundingBox"]["Top"],
                    "column": label["Instances"][i]["BoundingBox"]["Left"],
                    "labels": [{"label": label["Name"],
                                "confidence": label["Confidence"] / 100
                                }],})
        except KeyError:
            pass
        except Exception as object_detection_error:
            print(str(object_detection_error))

        # Face detection metadata parsing
        try:
            face_detection_response = \
                return_response["detection_faces"]["FaceDetails"]
            metadata["frame_data"].append(
                {
                    "inference_type": "face_detection",
                    "boxes": [],
                }
            )
            for _, face_detail in enumerate(face_detection_response):
                metadata["frame_data"][-1]["boxes"].append({
                    "width": face_detail["BoundingBox"]["Width"],
                    "height": face_detail["BoundingBox"]["Height"],
                    "row": face_detail["BoundingBox"]["Top"],
                    "column": face_detail["BoundingBox"]["Left"],
                    "labels": [{"label": "Face",
                                "confidence": face_detail["Confidence"] / 100
                                }],})
        except KeyError:
            pass
        except Exception as face_detection_error:
            print(str(face_detection_error))

        # PPE detection metadata parsing
        try:
            ppe_detection_response = \
                return_response["detection_ppe"]["Persons"]
            metadata["frame_data"].append({
                "inference_type": "ppe_detection",
                "boxes": [],
            })
            for _, person in enumerate(ppe_detection_response):
                metadata["frame_data"][-1]["boxes"].append({
                    "width": person["BoundingBox"]["Width"],
                    "height": person["BoundingBox"]["Height"],
                    "row": person["BoundingBox"]["Top"],
                    "column": person["BoundingBox"]["Left"],
                    "labels": [{"label": "PPE",
                                "confidence": person["Confidence"] / 100
                                }],})

                # Changes are in feature/fix_PPE_box branch, needs to merge.
        except KeyError:
            pass
        except Exception as ppe_detection_error:
            print(str(ppe_detection_error))

        # Face Search metadata parsing
        try:
            face_search_response = return_response["face_search"]
            metadata["frame_data"].append({
                "inference_type": "face_search",
                "boxes": []
            })
            if face_search_response is None:
                pass
            else:
                if face_search_response["FaceMatches"]:
                    metadata["frame_data"][-1]["boxes"].append({
                    "width":
                    face_search_response['SearchedFaceBoundingBox']['Width'],
                    "height":
                    face_search_response['SearchedFaceBoundingBox']["Height"],
                    "row":
                    face_search_response["SearchedFaceBoundingBox"]["Top"],
                    "column":
                    face_search_response["SearchedFaceBoundingBox"]["Left"],
                    "labels": [
                        {"label":
                         face_search_response["FaceMatches"]
                            [0]['Face']['ExternalImageId'].split('.')[0],
                         "confidence":
                         face_search_response['SearchedFaceConfidence'] / 100
                         }],})
                else:
                    pass
                    # print("No Match Found!")
        except KeyError:
            pass
        except Exception as face_search_error:
            print(str(face_search_error))

        # Static Object Detection metadata parsing
        try:
            static_object_response = return_response["static_object"]
            metadata["frame_data"].append({
                "inference_type": "static_object",
                "boxes": []
            })
            if static_object_response is None:
                pass
            else:
                for _, label in enumerate(static_object_response):
                    for i in range(len(label["Instances"])):
                        metadata["frame_data"][-1]["boxes"].append({
                            "width":
                                label["Instances"][i]["BoundingBox"]["Width"],
                            "height":
                                label["Instances"][i]["BoundingBox"]["Height"],
                            "row":
                                label["Instances"][i]["BoundingBox"]["Top"],
                            "column":
                                label["Instances"][i]["BoundingBox"]["Left"],
                            "labels": [{"label": label["Instances"]
                            [i]['staticness']['status'],
                                        "confidence":
                                            label["Confidence"] / 100
                                        }],})
            id_count = id_count + 1
        except KeyError:
            pass
        except Exception as static_object_error:
            print(str(static_object_error))

        # YOLO Object detector
        try:
            yolo_detector_resp = return_response["yolo_detector"]
            metadata["frame_data"].append({
                "inference_type": "yolo_detector_resp",
                "boxes": []
            })
            if yolo_detector_resp["yolo_detector"] is None:
                pass
            else:
                for _, label in enumerate(yolo_detector_resp):
                        metadata["frame_data"][-1]["boxes"].append({
                            "width":
                                label["xmax"],
                            "height":
                                label["ymax"],
                            "row":
                                label["xmin"],
                            "column":
                                label["ymin"],
                            "labels": [{"label": label["name"]
                                        }], })
        except KeyError:
            pass


        pprint(metadata)

        # sends response from object Detection to producers
        last_index = len(inference_list) - 1
        if last_index == -1:
            pass
        elif inference_list[last_index]["timestamp"] < metadata["timestamp"]:
            inference_list.insert(last_index, metadata)
        inference_list.append(metadata)
        last_tag = tags[0]
        # uncomment to log the time stamps
        # f = open("logs.txt", "a")
        # f.write(str(tags) + '\n')
        # f.close()


def producer_loop():
    """
    Producer loop that puts inference in producer.
    :return: None
    """
    while True:
        if WAIT_FLAG:
            print("producer loop sleeping")
            sleep(5)
        elif inference_list:
            #write Detection App to json
            with open('output_data.json', 'a', encoding='utf-8') as output_file:
                json.dump(inference_list, output_file, ensure_ascii=False, indent=4)

        elif QUIT:
            break


# try:
#     with concurrent.futures.ThreadPoolExecutor(6) as main_thread:
#         kvs_consumer_thread = main_thread.submit(loop_kvs_consume)
#
#         inference_thread = main_thread.submit(inference_loop)
#
#         inference_thread_1 = main_thread.submit(inference_loop)
#
#         kds_producer_thread = main_thread.submit(producer_loop)
#
# except KeyboardInterrupt:
#     QUIT = True
#     main_thread.shutdown(wait=False)
#
# except Exception as error:
#     print(str(error))
#     QUIT = True
#     main_thread.shutdown(wait=False)

KVS_thread = Thread(target=loop_kvs_consume)
KVS_thread.start()

inference_thread_1 = Thread(target=inference_loop)
inference_thread_1.start()

inference_thread_2 = Thread(target=inference_loop)
inference_thread_2.start()

producer_thread = Thread(target=producer_loop)
producer_thread.start()

KVS_thread.join()
inference_thread_1.join()
inference_thread_2.join()
producer_thread.join()
