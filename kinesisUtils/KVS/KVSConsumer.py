import io
import time
import cv2
import imageio as iio
import boto3
import timeit
import kinesisUtils.KVS.MKV_tags as mkv
import csv


class Consume:
    def __init__(self, stream_name):

        self.AWS_STREAM_NAME = stream_name

        kvs_client = boto3.client("kinesisvideo",
                                  region_name="us-west-2")

        self.kvs_endpoint = kvs_client.get_data_endpoint(
            StreamName=self.AWS_STREAM_NAME,
            APIName='GET_MEDIA'
        )['DataEndpoint']

    def transcode_frame(self, frame):
        # Encode frame into bytes for job submission
        img_str = cv2.imencode('.jpg', frame)[1].tobytes()
        return img_str

    def get_frame(self, chunk):
        try:
            fragment = iio.v3.imread(io.BytesIO(chunk), format_hint=".mkv")
            for num, im in enumerate(fragment):
                if num % 10 == 0:
                    sts = 0
                    print("Frame captured")
                    break
            print("Returning result")
            return im, sts, fragment
            # print(f'Finish one chunk took: {timeit.default_timer() - start_time}')
        except OSError as e:
            print("Broken fragment received")
            sts = 1
            return None, sts

    def read_chunk(self, fragment):
        chunk = fragment['Payload'].read(1024 * 8 * 8)
        tags = mkv.getMkvTagVal(chunk, reqs=["producer_timestamp"])
        return chunk, tags

    def get_fragment(self):
        media_client = boto3.client(
            'kinesis-video-media', endpoint_url=self.kvs_endpoint, region_name='us-west-2')
        fragment = media_client.get_media(
            StreamName=self.AWS_STREAM_NAME,
            StartSelector={
                'StartSelectorType': 'NOW'
            }
        )
        # print(f'Downloading one chunk took: {timeit.default_timer() - start_time}')
        print('Fragment downloaded ', fragment)
        return fragment

    def run(self, return_response_KVS):
        while True:
            start_time = timeit.default_timer()
            fragment = self.get_fragment()
            try:
                chunk, tags = self.read_chunk(fragment)

                if not chunk:
                    break

                im, sts, fragment = self.get_frame(chunk)

                if sts != 0:
                    time.sleep(0.25)
                    continue
                img_str = self.transcode_frame(im)
                try:
                    # put_queue(img_str)
                    time.sleep(0.25)
                    end_time = timeit.default_timer()
                except:
                    print('Cannot connect to RabbitMQ')
                    time.sleep(3)
                    continue
                return_response_KVS.append([tags, fragment])
                return tags, fragment

            except Exception as error:
                print("Video Stream is OFF, make sure you stream it via gst-launch pipeline!")
                print(error, "From CHUNKS")
                pass
            # print('Time between fragment download and frame processing: {overalltime}'.format(overalltime))
