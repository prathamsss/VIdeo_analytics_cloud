from kinesisUtils.KDS.KDSConsume import Consume

AWS_CREDS = "credentials.csv"
AWS_REGION = "ap-southeast-1"
KDS_STREAM = "test_data_stream"

consumer = Consume(KDS_STREAM, AWS_REGION, AWS_CREDS)
while True:
    try:
        consumer.get()
    except IndexError:
        pass
