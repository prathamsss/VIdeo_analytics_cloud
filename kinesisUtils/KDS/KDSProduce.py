import boto3
from kinesisUtils.KDS.KinesisStreamWrapper import KinesisStream
import json
import csv


class Produce:
    def __init__(self, stream_name):
        self.AWS_STREAM_NAME = stream_name

    def put(self, metadata, partitionkey='partitionkey'):

        client = boto3.client("kinesis",
                              region_name="us-west-2")
        streamer = KinesisStream(client)
        description = streamer.describe(self.AWS_STREAM_NAME)
        print("putting data... ")
        streamer.put_record(metadata, partitionkey)
