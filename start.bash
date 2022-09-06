sudo docker build -t va_demo .
#launch docker :
echo "Starting Vdieo Streaming..."
sudo docker run --env-file=test.env --device=/dev/video0  -v /opt/vc:/opt/vc va_demo  /bin/sh -c "LD_LIBRARY_PATH=/opt/amazon-kinesis-video-streams-producer--source/local/lib;GST_PLUGIN_PATH=/opt/amazon-kinesis-video-streams-producer-sdk-cpp/build;gst-launch-1.0 v4l2src do-timestamp=TRUE device=/dev/video0 ! videoconvert ! video/x-raw,format=I420,width=640,height=480,framerate=30/1 ! x264enc  bframes=0 key-int-max=45 bitrate=500 ! video/x-h264,stream-format=avc,alignment=au,profile=baseline ! kvssink stream-name="testapp" storage-size=512 access-key="AKIAU7NAZHMYB6H2VJ7S" secret-key="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" aws-region="us-west-2""

