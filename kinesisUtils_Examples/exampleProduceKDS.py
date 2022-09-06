from kinesisUtils.KDS.KDSProduce import Produce
import json

file = open('kinesisUtils/KDS/metatdataschema.json')
metadata = json.load(file)

KDS_STREAM = "test_data_stream"
AWS_REGION = "ap-southeast-1"
AWS_CREDS = "credentials.csv"

producer = Produce(KDS_STREAM, AWS_REGION, AWS_CREDS)

while True:
    producer.put(metadata)
