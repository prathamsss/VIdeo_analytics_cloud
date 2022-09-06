#Video Analytics Pipeline-Serving Multiple Models Together

Hey, thanks for giving me this opportunity to test at Xihlem Robotics. Here I have presented a sample of my recent Python project.

####AIM: The motivation to develop this system was to do video analytics inference of multiple Machine models in parallel on video streams coming via the cloud.

####Objective:
 1. Streaming video from any camera/robot to the cloud using a producer-consumer architecture with the help of AWS KVS-based HTTP streaming.
 2. This stream from the cloud would be consumed by multiple Machine Learning Models in parallel using Threading architecture and would pump their output data into a json.
 3. Here you could also switch specific models to run. To do this in the main.py file just comment out line no.115
 
### Flow of the project:
    1.Gstreammer starts streaming local video to the cloud.
    2.This video is consumed by the main.py file and it applies multiple ML Models together.
    3.The output of each module is written in the output_data.json file.

######Note - I have used AWS Models API and YOLO Object detector for test purposes, originally I used custom-trained models served via flask.

##Features:
- **_General Object Det ection:_** General objects that include a variety of classes. Also, can filter for classes as required. 


- **_Mask Detection:_** Comes Under PPE Detection from AWS. 


- **_Face Detection_**:  General Face Detection.


- **_Face Search: Needs_** to add faces to recognize in S3 (Link)


- **_Static Object detection._** :  Algorithm for detecting the steadiness of a person.


- _**YOLO**_:  YOLO object detection model, served using Flask.

###Files and their usage:
    1. main.py - This is the main engine where it gets the video frames, applies ML Models, and pumps data. All there three process works in parallel. All ML Models also work in parallel on frames.
    2. model_detections.py - Here ML Models API has been initialized. This would probably call the models via POST request and pass each frame for inference.
    3. app.py - Here YOLO Model is been hosted using Flask.
    4. static_object_detection.py - An algorithm that uses the bounding box to detect static objects in frames.


###**HOW TO RUN:**
For these tests, I have enabled docker since there are a lot of dependencies. I have built the docker script assuming that you are using Ubuntu, since on Mac, docker doesn't support camera access. It would take some time to build the docker!

1. Build container:
           
              sudo docker build -t va_demo .
2. Run container:
 
         sudo docker run --name va_container --env-file=test.env --device=/dev/video0  -v /opt/vc:/opt/vc va_demo

Don't wait step 2 to get completed in another termial run step 3.

3. Run Video Streammer:
            
            sudo docker exec -it va_container /bin/sh -c "cd;LD_LIBRARY_PATH=/opt/amazon-kinesis-video-streams-producer--source/local/lib;GST_PLUGIN_PATH=/opt/amazon-kinesis-video-streams-producer-sdk-cpp/build;gst-launch-1.0 v4l2src do-timestamp=TRUE device=/dev/video0 ! videoconvert ! video/x-raw,format=I420,width=640,height=480,framerate=30/1 ! x264enc  bframes=0 key-int-max=45 bitrate=500 ! video/x-h264,stream-format=avc,alignment=au,profile=baseline ! kvssink stream-name="testapp" storage-size=512 access-key="AKIAU7NAZHMYB6H2VJ7S" secret-key="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" aws-region="us-west-2""


####Switching VA Module:


Users can also pass a custom list of VA modules from Robot to run custom VA modules.
NOTE: The names of VA modules are case-sensitive. The following are names used -


`"object_detection",
"face_detection",
"ppe_detection",
"face_search",
"static_object",`

It runs all VA modules, by default, if the empty list of VA modules is passed. See line no 115 in main.py