"""
Algorithm  for Static Object Detection
This algo consumes frames from AWS or YOLO Model.
"""
import time
from time import sleep
import collections
import itertools
from itertools import combinations
import cv2
from shapely.geometry import Polygon
from model_detections import ModelDetections


class StaticObjectDetection:
    """ Utility for Static Object Detection"""
    def __init__(self, frame_obj, intersection_thress, thress_time):
        """
        Method to Initialise variables for
        static object detection.
        :param frame_obj: object for Vi
        :param intersection_thress frame_obj:
                threshold for detections overlapping.
        :param thress_time: limit for object to stay in frame.

        :return: None
        """
        self.frame_obj = frame_obj
        self.intersection_thress = intersection_thress
        self.thress_time = thress_time
        self.id_count = 0
        self.detect = ModelDetections()
        self.fps = self.get_fps(self.frame_obj, 5)
        self.buffer = collections.deque([], maxlen=self.fps * thress_time)
        #self.font = cv2.FONT_HERSHEY_SIMPLEX

    def get_fps(self, vid, num):
        """
        Method to calculate FPS for given limit
        :param vid: video or frame object.
        :param num: no of frames to calculate FPS.

        :return: FPS (int)
        """
        prev_frame_time = 0
        new_frame_time = 0
        frame_rate = []
        print("Calculating FPS...")
        return_response_kvs =[]
        for _ in range(num):
            try:
                _, frame = vid.run(return_response_kvs) #vid.read()
                _, image_bytes = cv2.imencode(".jpg", frame)
                _ = self.detect.object_detection(image_bytes.tobytes(),
                                                 max_labels=10)
            except ValueError as value_error:
                if str(value_error) == "Tags not found":
                    print("kvs loop sleeping")
                    sleep(5)
                    continue

            new_frame_time = time.time()
            fps = 1 / (new_frame_time - prev_frame_time)
            prev_frame_time = new_frame_time
            frame_rate.append(fps)

        try:
            fps = round(sum(frame_rate) / len(frame_rate))
        except ZeroDivisionError:
            fps=0
        if fps == 0:
            fps = 1
        print(f"Running at {fps} FPS")
        return fps

    def get_overlapping_area(self, frame1, frame2):
        """
        Calculates overlapping between two successive frames.
        For multiple objects it keeps a track using position for that frame
        in response from AWS detection.
        :param frame1: nth frame
        :param frame2: nth +1 frame

        :return:: Dict of area of intersection and it's coordinates
        """
        rect1 = []
        rect2 = []
        area_intersection = []
        intersection_corrds = []
        final_dict = {}
        temp_perc = []
        temp_intersection = []
        for frame in frame1:
            for inst in frame['Instances']:
                left = inst['BoundingBox']['Left']
                top = inst['BoundingBox']['Top']
                width = inst['BoundingBox']['Width']
                height = inst['BoundingBox']['Height']

                points = [(left, top),
                          (left + width, top),
                          (left + width, top + height),
                          (left, top + height)]
                rect1.append(Polygon(points))

        for frame in frame2:
            for inst in frame['Instances']:
                left = inst['BoundingBox']['Left']
                top = inst['BoundingBox']['Top']
                width = inst['BoundingBox']['Width']
                height = inst['BoundingBox']['Height']
                points = [(left, top),
                          (left + width, top),
                          (left + width, top + height),
                          (left, top + height)]
                rect2.append(Polygon(points))

        for first_rect in range(len(rect1)):
            for second_rect in range(len(rect2)):
                rect_intersection = \
                    (rect1[first_rect].intersection(rect2[second_rect]))
                percentage_intersect = \
                    rect_intersection.area / (
                            rect1[first_rect].area +
                            rect2[second_rect].area - rect_intersection.area
                )
                temp_perc.append(percentage_intersect)
                temp_intersection.append(rect_intersection)

            area_intersection.append(max(temp_perc))
            intersection_corrds.append(
                temp_intersection[temp_perc.index(max(temp_perc))]
            )
            final_dict['area_intersection'] = area_intersection
            final_dict['intersection_corrds'] = intersection_corrds
            temp_perc.clear()
            temp_intersection.clear()

        # area_intersection and intersection_corrds contains a list of
        # area_intersection_confidence & intersection points of each
        # consecutive frame respectively ...
        return final_dict

    def num_of_static_frames(self, final_decision, intersection_thress):
        """
        Helper function for checking number of frames aligning with threshold.
        :param final_decision: list of dict of overlapping frames in buffer.
        :param intersection_thress: threshold for detections overlapping.

        :return: List of no static frames and respective intersection points.
        """
        counting_list = [0] * len(final_decision[0]['area_intersection'])
        intersection_pts = []
        for frame in final_decision:
            for intersect_area in \
                    frame['area_intersection']:
                if intersect_area >= \
                        intersection_thress:
                    indexes = \
                        frame['area_intersection'].index(intersect_area)
                    try:
                        counting_list[indexes] = counting_list[indexes] + 1
                        intersection_pts.append(frame['intersection_corrds'])
                    except IndexError:
                        pass

        return counting_list, intersection_pts

    def get_static_decision(self, buffer):
        """
        Method to calculate static object for given buffer.
        :param buffer: Buffer containing frames.

        :return: Status of newth frame and newth frame.
        """
        final_decision=[]
        viz_status=[]
        new_final_decision=[]
        for _, combo in enumerate(
                combinations(list(buffer)[1:], 2)):  # 1-2-Many Comparison
            first_frame, second_frame = combo
            final_dict = self.get_overlapping_area(first_frame['Labels'],
                                                   second_frame['Labels'])
            final_decision.append(final_dict)

        # Computation for newth frame
        for new_conf in range(1, len(list(buffer))):
            new_final_dict = self.get_overlapping_area(
                            buffer[0]['Labels'],buffer[new_conf]['Labels'])
            new_final_decision.append(new_final_dict)

        new_counting_list, _ = \
            self.num_of_static_frames(
                new_final_decision, self.intersection_thress)

        for new_count in range(len(new_counting_list)):
            if new_counting_list[new_count] > round(len(buffer) / 2):
                new_status = {"person_no": new_count, "status": "Static"}
                viz_status.append(new_status)
            else:
                new_status = {"person_no": new_count, "status": "Not Static"}
                viz_status.append(new_status)

        new_final_decision.clear()
        final_decision.clear()
        return viz_status, buffer[0]['Labels']
        # returning Status for respective frame

    def detect_static_object(self, image_bytes, id_count,
                             max_labels, target_object,
                             return_response={}):
        """
        Method to do static object detection incoming frames.
        :param: image_bytes: input camera frames in bytes
        :param: id_count: frame id, should initialise as
        :param: zero & increment by end of loop.
        :param: max_labels: Detection max labels
        :param: target_object: Eg. Person, Bags, etc.

        :return: Frame containing object detection &
                 staticness details.
        """
        response = self.detect.object_detection(image_bytes, max_labels=max_labels,
                                                target_object=target_object)
        response['id'] = id_count
        status_frames = None
        if not response['Labels']:
            print("Static object - No detections")

        else:
            self.buffer.appendleft(response)
            if len(self.buffer) == \
                    self.fps * self.thress_time:
                status, status_frames = \
                    self.get_static_decision(self.buffer)
                for status_frame in status_frames:
                    for dict_key, dict_val in \
                            itertools.zip_longest(status_frame["Instances"], status):
                        dict_key['staticness'] = dict_val
        return_response["static_object"] = status_frames
        return status_frames


# Driver code example

# from PIL import  Image, ImageFont,ImageDraw
# import numpy as np
#
# MAX_LABELS = 10
# TARGET_OBJECT = "Person"
# intersection_thress = 0.80
# thress_time = 5
#
# vid = cv2.VideoCapture(0)
# static_obj = StaticObjectDetection(vid, intersection_thress, thress_time)
#
# id = 0
# while (vid.isOpened()):
#     ret, frame = vid.read()
#     hasFrame, imageBytes = cv2.imencode(".jpg", frame)
#     stauts_frame = static_obj.detect_static_object(imageBytes.tobytes(), id, max_labels=10, target_object='Person')
#     print(stauts_frame)
#     id = id + 1
#
#     # Visualisation.
#     if stauts_frame == None:
#         pass
#
#     else:
#         print("Status_frame =",stauts_frame)
#         image = Image.fromarray(frame)
#         imgWidth, imgHeight = image.size
#         font = ImageFont.truetype("/Users/prathameshsardeshmukh/Desktop/kabam/projects/static-object-detection/arial.ttf", size=32)
#
#
#         for i in stauts_frame:
#             for bbox in i['Instances']:
#                 top = bbox['BoundingBox']['Top'] * imgHeight
#                 left = bbox['BoundingBox']['Left'] * imgWidth
#                 width = bbox['BoundingBox']['Width'] * imgWidth
#                 height = bbox['BoundingBox']['Height'] * imgHeight
#
#
#                 points = (
#                     (left, top),
#                     (left + width, top),
#                     (left + width, top + height),
#                     (left, top + height),
#                     (left, top)
#                 )
#
#                 image = Image.fromarray(frame)
#                 draw = ImageDraw.Draw(image)
#                 text = bbox['staticness']['status']
#                 draw.line(points, fill="#0000FF", width=5)
#                 draw.text((left, top-30), text, (255, 0, 0),font)
#                 frame = np.array(image)
#
#
#         cv2.imshow("Static Object Detection",frame)
#
#     if cv2.waitKey(100) & 0xFF == ord('q'):
#         break
#
#
# vid.release()
# cv2.destroyAllWindows()
