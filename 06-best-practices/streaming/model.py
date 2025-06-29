import base64
import json
import os

import boto3
import mlflow


def get_model_path(run_id):
    "Gets path for model from env or sets to S3 location"
    model_location = os.getenv("MODEL_LOCATION")

    if model_location is not None:
        print("From local")
        return model_location
    print("From S3")
    model_bucket = os.getenv("MODEL_BUCKET", "mlflow-artifact-mmichal")
    experiment_id = os.getenv("MLFLOW_EXPERIMENT_ID", "2")

    logged_model = f"s3://{model_bucket}/{experiment_id}/{run_id}/artifacts/model"
    # s3://mlflow-artifact-mmichal/2/e0b68d8dd70d4e6fbcaf656cf45a31d5/artifacts/model
    return logged_model


def load_model(run_id: str):
    "Load model from path location"
    logged_model = get_model_path(run_id=run_id)
    # Load model as a PyFuncModel.
    model = mlflow.pyfunc.load_model(logged_model)
    return model


def base64_decode(encoded_data):
    "Decode payload using base64"
    payload = base64.b64decode(encoded_data).decode("utf-8")
    ride_event = json.loads(payload)
    return ride_event


class ModelService:
    def __init__(self, model, run_id, callbacks=None):
        self.model = model
        self.model_version = run_id
        self.callbacks = callbacks or []

    def prepare_features(self, ride):
        features = {}
        features["PU_DO"] = "%s_%s" % (ride["PULocationID"], ride["DOLocationID"])
        return features

    def predict(self, features):
        preds = self.model.predict(features)
        return float(preds[0])

    def lambda_handler(self, event):
        # print(json.dumps(event))

        predictions = []

        for record in event["Records"]:
            # Kinesis data is base64 encoded so decode here
            encoded_data = record["kinesis"]["data"]
            ride_event = base64_decode(encoded_data)

            ride = ride_event["ride"]
            ride_id = ride_event["ride_id"]

            features = self.prepare_features(ride)
            prediction = self.predict(features)

            prediction_event = {
                "model": "ride_duration_prediction_model",
                "version": self.model_version,
                "prediction": {"ride_id": ride_id, "ride_duration": prediction},
            }

            for callback in self.callbacks:
                callback(prediction_event)

            # kinesis_client.put_record(
            #     StreamName=STREAM_NAME,
            #     Data=json.dumps(prediction_event),
            #     PartitionKey=str(ride_id)
            # )

            predictions.append(prediction_event)

        # response = kinesis_client.put_records(
        #     StreamName=STREAM_NAME,
        #     Records=predictions
        # )
        return {
            "statusCode": 200,
            # 'ride_id': ride_id,
            "predictions": predictions,
            # 'body': json.dumps('Hello from Lambda!')
        }


class KinesisCallback:
    def __init__(self, kinesis_client, prediction_stream_name):
        self.kinesis_client = kinesis_client
        self.prediction_stream_name = prediction_stream_name

    def put_record(self, prediction_event):
        ride_id = prediction_event["prediction"]["ride_id"]

        self.kinesis_client.put_record(
            StreamName=self.prediction_stream_name,
            Data=json.dumps(prediction_event),
            PartitionKey=str(ride_id),
        )


def create_kinesis_client():
    endpoint_url = os.getenv("KINESIS_ENDPOINT_URL")

    if endpoint_url is None:
        return boto3.client("kinesis")

    return boto3.client("kinesis", endpoint_url=endpoint_url)


def init(stream_name: str, run_id: str, test_run: bool):
    model = load_model(run_id=run_id)

    callbacks = []

    if not test_run:
        kinesis_client = create_kinesis_client()
        kinesis_callback = KinesisCallback(kinesis_client, stream_name)
        callbacks.append(kinesis_callback.put_record)

    model_service = ModelService(model=model, run_id=run_id, callbacks=callbacks)

    return model_service
