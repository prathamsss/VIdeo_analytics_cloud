from kinesisUtils.KVS.KVSConsumer import Consume
from PIL import Image
import numpy as np

KVS_STREAM_NAME = "testwebapp"
AWS_REGION = "ap-southeast-1"
AWS_CREDS = "credentials.csv"

consumer = Consume(KVS_STREAM_NAME, AWS_REGION, AWS_CREDS)

tags, frame = consumer.run()

print(tags)

array = np.array(frame, dtype=np.uint8)

image = Image.fromarray(array)
image.show()
