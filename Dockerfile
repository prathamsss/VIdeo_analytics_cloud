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

WORKDIR /app
COPY requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app
ENTRYPOINT ["python3", "main.py"]