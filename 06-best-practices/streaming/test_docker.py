import requests

event = {
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "1",
                "sequenceNumber": "49664446144264195863968399814519302281841101500737126402",
                "data": "ewoicmlkZSI6IHsKIlBVTG9jYXRpb25JRCI6MTMwLAoiRE9Mb2NhdGlvbklEIjoyMDUKfSwKInJpZGVfaWQiOjI1Ngp9",
                "approximateArrivalTimestamp": 1750471614.483
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49664446144264195863968399814519302281841101500737126402",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::231917356461:role/lambda-kinesis-role",
            "awsRegion": "us-east-1",
            "eventSourceARN": "arn:aws:kinesis:us-east-1:231917356461:stream/ride_events"
        }
    ]
}

url = "http://localhost:8080/2015-03-31/functions/function/invocations"
response = requests.post(url, json=event)
print(response.json())