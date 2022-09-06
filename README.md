
# Video Analytics Pipeline - Serving Multiple models Together

Hey Thanks for giving me this oppotunity for test at Xihlem Robotics.
Here I have presented sample of my recent python project. 

AIM : Motivation to develop this system was to do video analytics infernece of multiple models in parallel on video stream coming via Cloud.

Objective: 
 1. Streaming Video from any camera/robot to cloud using producer consumer arrchietcure with the help of AWS KVS based HTTP streaming.  
 2. This stream from cloud would be consumed by multiple Machine Learning Models in parallel using Threading architecture and write a final output data in json. 
 3. Here you could also mention specific models to run in

Va module costumes frames using AWS KVS => Applies detection algorithms on frames => pumps output into KDS Consumer  
Hence, it has for following features:

**_1. General Object Detection_**:  General objects that includes variety of classes. Also, can filter for classes any as required.

_**2. Mask Detection**_:  Comes Under PPE Detection from AWS.
             
**_3. Face Detection_** : General Face Detection.

**_4. Face Search_** :  Needs to add faces to recognise in S3 ([Link](https://docs.aws.amazon.com/rekognition/latest/dg/add-faces-to-collection-procedure.html))
             
**_5. Static Object detection._** : Algoroithm for detecting steadiness of objects. Good for limited conditions (Eg. Non living objects)
             
**_6. License Plate reading._** : Using plate recognizer API we had done license plate reading that gives us license plate string. 

### API Usage

```python
from model_detections import ModelDetections

# create instance 
detect = ModelDetections("my_aws_creds.csv")
# returns 'metadata with required data for visualisation'
# Example: 
object_detection_respose = detect.object_detection(input_base64_image, max_labels=10)
```


Refer Main.py for an example. 


## KVS and KDS integration

```bash
git clone git@bitbucket.org:cognicept/kinesis-utils.git
python setup.py install --user
```

## Metadata structure :
#### 1. General Structure:
           {'frame_data': [{'boxes': [],'inference_type': 'object_detection'},
                          {'boxes': [], 'inference_type': 'face_detection'},
                          ..,
           'timestamp': '2022-06-09T11:22:04.807369Z'}

#### 2. Metadata structure for Object Detection, PPE, Face Detection and search, Static Object, License Plate Reading:
```
{'boxes':  
    [{'inference_type': 'object_detection',
              'column': 0.1,
              'height': 0.2,
              'row': 0.3,
              'width': 0.3}],
              'labels': [{'confidence': 0.85,
                          'label': 'Chair'}
```

### Files and  Usage:
     main.py :  1. Continuously streams frames using KVS.
                2. Applies algo on incoming frames and runs all VA Modules in parallel using Multi threading.
                3. Continuously metadata got in step 2 to KDS.

    aws_detection.py : Here we have implemented all APIs for repective type of  detections from AWS/Third party.
    
    staticobjectdetection.py :  Algorithm for static object Detection. 
    
    env.template : For ruuning entire project, needs to set some env variables as shown in this template.


### Custom VA Module:
User can also pass custom list of VA modules from Robot to tun custom VA modules.

_NOTE_ : This names of va modules are case-sensitive. Following are names used - 

    "object_detection",
    "face_detection",
    "ppe_detection",
    "face_search",
    "static_object",
    "license_plate_reading"
    
It runs all VA modules, by default, if empty list of va modules is passed.
