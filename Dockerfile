FROM python:3.9

LABEL MAINTAINER "pratham.sardeshmukh@gmail.com"

RUN apt-get update && \
	apt-get install -y \
	cmake \
	curl \
	g++ \
	gcc \
	git \
	gstreamer1.0-plugins-base-apps \
	gstreamer1.0-plugins-bad \
	gstreamer1.0-plugins-good \
	gstreamer1.0-plugins-ugly \
	gstreamer1.0-tools \
	gstreamer1.0-omx \
	libssl-dev \
	libcurl4-openssl-dev \
	liblog4cplus-dev \
	libgstreamer1.0-dev \
	libgstreamer-plugins-base1.0-dev \
	m4 \
	make \
	openssh-server \
	pkg-config \
	vim \
	ffmpeg \
    libsm6 \
    libxext6

WORKDIR /opt/
RUN git clone https://github.com/awslabs/amazon-kinesis-video-streams-producer-sdk-cpp.git
RUN mkdir -p amazon-kinesis-video-streams-producer-sdk-cpp/build
WORKDIR /opt/amazon-kinesis-video-streams-producer-sdk-cpp/build/
RUN cmake -DBUILD_GSTREAMER_PLUGIN=ON -DBUILD_GSTREAMER_PLUGIN=TRUE ..
RUN make

ENV LD_LIBRARY_PATH=/opt/amazon-kinesis-video-streams-producer-sdk-cpp/open-source/local/lib
ENV GST_PLUGIN_PATH=/opt/amazon-kinesis-video-streams-producer-sdk-cpp/build/:$GST_PLUGIN_PATH


RUN export GST_PLUGIN_PATH=/opt/amazon-kinesis-video-streams-producer-sdk-cpp/build
RUN export LD_LIBRARY_PATH=/opt/amazon-kinesis-video-streams-producer-sdk-cpp/open-source/local/lib

# main program
COPY requirements.txt /app/requirements.txt

RUN cd
WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

RUN gst-launch-1.0 v4l2src do-timestamp=TRUE device=/dev/video0 ! videoconvert ! video/x-raw,format=I420,width=640,height=480,framerate=30/1 ! x264enc  bframes=0 key-int-max=45 bitrate=500 ! video/x-h264,stream-format=avc,alignment=au,profile=baseline ! kvssink stream-name="testapp" storage-size=512 access-key="AKIAU7NAZHMYB6H2VJ7S" secret-key="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" aws-region="us-west-2"

# ENTRYPOINT ["python3", "main.py"]
