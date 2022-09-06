
# Video Analytics Pipeline - Serving Multiple models Together

Hey Thanks for giving me this oppotunity for test at Xihlem Robotics.
Here I have presented sample of my recent python project. 

####AIM : Motivation to develop this system was to do video analytics infernece of multiple Machine models models in parallel on video stream coming via Cloud.

####Objective: 
 1. Streaming Video from any camera/robot to cloud using producer consumer arrchietcure with the help of AWS KVS based HTTP streaming.  
 2. This stream from cloud would be consumed by multiple Machine Learning Models in parallel using Threading architecture and would pump there output data into a json.
 3. Here you could also switch specific models to run. To do this in main.py file just comment out line no.` 115`


####Flow of the project:
    1. Gstreammer starts streaming local video to cloud.
    2. These video is consumed by main.py file and it applied Mutiple ML Models together.
    3. Output of each module is writen in output_data.json file.

######Note - I have used AWS Models API and YOLO Object detector for test prpose, originally I have used cusotom trained models serving via flask.

###Features:
**_1. General Object Detection_**:  General objects that includes variety of classes. Also, can filter for classes any as required.

_**2. Mask Detection**_:  Comes Under PPE Detection from AWS.
             
**_3. Face Detection_** : General Face Detection.

**_4. Face Search_** :  Needs to add faces to recognise in S3 ([Link](https://docs.aws.amazon.com/rekognition/latest/dg/add-faces-to-collection-procedure.html))
             
**_5. Static Object detection._** : Algoroithm for detecting steadiness of person.

**_5. YOLO_** : YOLO object detectin model served using Flask. 


####Files and there usage:
main.py - This is the main engine where it gets the video frames and applies ML Models, and pupms data. All there three process works in parallel. All ML Models also works in parallel on frames.

model_detections.py - Here ML Models API are been initialised, these would probably call the models via POST request and pass each frames for inference.

app.py - Here YOLO Model is been hosted using Flask.

static_object_detection.py - An algorithm that uses bounding box to detect static objects in frames.

##HOW TO RUN:

For these test I have enabled docker since there are alot of dependencies. 
I have built the docker script assuming that you are using Ubuntu since on mac docker doesn't support camera access.
It would take some time building the docker! 

### Swiitching VA Module:
User can also pass custom list of VA modules from Robot to tun custom VA modules.

_NOTE_ : This names of va modules are case-sensitive. Following are names used - 

    "object_detection",
    "face_detection",
    "ppe_detection",
    "face_search",
    "static_object",
    
It runs all VA modules, by default, if empty list of va modules is passed.
See line no 115 in main.py

