```bash

docker build -t stream-model-duration:v2 .

```

```bash
docker run -it --rm \
    -p 8080:8080 \
    -e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e RUN_ID="e0b68d8dd70d4e6fbcaf656cf45a31d5" \
    -v ~/.aws:/root/.aws \
    -e AWS_DEFAULT_REGION="us-east-1" \
    stream-model-duration:v2
````

```bash
docker run -it --rm \
    -p 8080:8080 \
    -e RUN_ID="e0b68d8dd70d4e6fbcaf656cf45a31d5" \
    -e AWS_DEFAULT_REGION="us-east-1" \
    stream-model-duration:v2
````