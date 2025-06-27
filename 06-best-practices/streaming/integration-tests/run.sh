#!/usr/bin/env bash

cd "$(dirname "$0")"

LOCAL_TAG = date +"%Y-%m-%d-%H-%m"
LOCAL_IMAGE_NAME = "stream-model-duration:${LOCAL_TAG}"

docker build -t ${LOCAL_IMAGE_NAME} .

docker run -it --rm \
    -p 8080:8080 \
    -e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e RUN_ID="e0b68d8dd70d4e6fbcaf656cf45a31d5" \
    -v ~/.aws:/root/.aws \
    -e MODEL_LOCATION="/app/model" \
    -e AWS_DEFAULT_REGION="us-east-1" \
    -v /workspaces/mlops-zoomcamp/06-best-practices/streaming/integration-tests/model:/app/model \
    ${LOCAL_IMAGE_NAME}



pipenv run python test_docker.py