import boto3
from kinesisUtils.KinesisStreamWrapper import KinesisStream
import csv


class Consume:
    def __init__(self, stream_name, region, aws_creds="credentials.csv"):
        with open(aws_creds, "r") as input:
            next(input)
            reader = csv.reader(input)
            for line in reader:
                self.AWS_KEY = line[2]
                self.AWS_SECRET = line[3]

        self.AWS_STREAM_NAME = stream_name
        self.AWS_REGION = region

    def get(self, aws_env="AWS.env"):
        client = boto3.client("kinesis",
                              region_name=self.AWS_REGION,
                              aws_access_key_id=self.AWS_KEY,
                              aws_secret_access_key=self.AWS_SECRET)

        # streamer = KinesisStream(client)
        # streamer.describe(AWS_STREAM_NAME)

        response = client.get_shard_iterator(
            StreamName=self.AWS_STREAM_NAME, ShardId="shardId-000000000000", ShardIteratorType='LATEST'
        )
        shard_iter = response['ShardIterator']
        print(shard_iter)
        response = client.get_records(
            ShardIterator=shard_iter, Limit=10
        )
        shard_iter = response['NextShardIterator']
        records = response['Records']
        print(records[0]['Data'])
