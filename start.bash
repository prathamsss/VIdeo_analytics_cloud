sudo docker build -t va_demo .
#launch docker :
sudo docker run -it --device=/dev/video0  -v /opt/vc:/opt/vc test_va /bin/bash
export GST_PLUGIN_PATH=/opt/amazon-kinesis-video-streams-producer-sdk-cpp/build
export LD_LIBRARY_PATH=/opt/amazon-kinesis-video-streams-producer-sdk-cpp/open-source/local/lib
echo "Starting Vdieo Streaming..."
gst-launch-1.0 v4l2src do-timestamp=TRUE device=/dev/video0 ! videoconvert ! video/x-raw,format=I420,width=640,height=480,framerate=30/1 ! x264enc  bframes=0 key-int-max=45 bitrate=500 ! video/x-h264,stream-format=avc,alignment=au,profile=baseline ! kvssink stream-name="testapp" storage-size=512 access-key="AKIAU7NAZHMYB6H2VJ7S" secret-key="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" aws-region="us-west-2"