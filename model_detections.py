""" Basic utility for accessing AWS rekognition APIs"""

import os
import boto3
import requests



class ModelDetections:
    """
    Basic utility for accessing AWS rekognition APIs
    """

    def __init__(self):
        """
        Here we initalise the boto3 client using credentials from CSV file.

        :param creds_csv: PATH of csv files containing AWS credentials.
        :raises keyError: raises an exception
        """

        self.client = boto3.client(
            'rekognition', region_name="us-west-2")

    def detection_faces(self, img_bytes, return_response={}):
        """Method for accessing AWS face rekognition

        :param img_bytes: Image bytes coverted to base64
        :returns: Json String having attributes for detected objects
        """
        response = self.client.detect_faces(Image={'Bytes': img_bytes})

        return_response["detection_faces"] = response
        return response

    def detection_ppe(self, img_bytes, return_response={}):
        """
        Method for accessing AWS PPE rekognition

        :param img_bytes: Image bytes coverted to base64
        :returns: Json String having attributes for detected objects
        """
        response = self.client.detect_protective_equipment(Image=
                                                           {'Bytes': img_bytes},
                                                           SummarizationAttributes=
                                                           {'MinConfidence': 80,
                                                            'RequiredEquipmentTypes':
                                                                ['FACE_COVER']})

        return_response["detection_ppe"] = response
        return response

    def object_detection(self, img_bytes, max_labels, target_object=False, return_response={}):
        """
        Method for accessing AWS Object rekognition

        :param img_bytes: Image bytes converted to base64
        :param max_labels: Threshold for maximum labels.
        :param target_object: Any specific object to detect (String)
        :returns: Json String having attributes for detected objects.
        """
        response = self.client.detect_labels(Image={'Bytes': img_bytes},
                                             MaxLabels=max_labels)

        if target_object:
            response['Labels'] = [i for i in response['Labels'] if i['Name'] == target_object]

        return_response["object_detection"] = response
        return response

    def face_search(self, img_byte_arr, threshold, max_faces, return_response={}):
        """
        Method to do face search w.r.t image in s3

        :param img_byte_arr: input face image to compare
        :param threshold: confidence threshold to compare
        :param max_faces: max no of faces to detect
        :param return_response: Dict For Multi threading purpose.

        :return: Metadata response of face search
        """
        response = {}
        try:
            response = self.client.search_faces_by_image(CollectionId=os.environ["COLLECTION_ID"],
                                                         Image={
                                                             'Bytes': img_byte_arr
                                                         },
                                                         FaceMatchThreshold=threshold,
                                                         MaxFaces=max_faces)
        except:
            response['FaceMatches'] = None

        return_response['face_search'] = response
        return response

    def yolo_detector(self, img_byte_arr, return_response={}):
        """
        Method to do face search w.r.t image in s3

        :param img_byte_arr: input face image to compare
        :param threshold: confidence threshold to compare
        :param max_faces: max no of faces to detect
        :param return_response: Dict For Multi threading purpose.

        :return: Metadata response of face search
        """
        api = "http://localhost:5000/get-prediction"

        response = {}
        try:
            response = requests.post(
                api,
                data=img_byte_arr.tobytes())

        except:
            response['yolo_detector'] = None

        return_response['yolo_detector'] = response
        return response
