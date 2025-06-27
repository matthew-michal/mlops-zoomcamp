import json
import base64
import boto3
import os
import mlflow

# kinesis_client = boto3.client('kinesis')


# logged_model = f"s3://mlflow-artifact-mmichal/2/{RUN_ID}/artifacts/model"
# # logged_model = f'runs:/{RUN_ID}/model'

# # Load model as a PyFuncModel.
# model = mlflow.pyfunc.load_model(logged_model)

def load_model(run_id: str):
    logged_model = f"s3://mlflow-artifact-mmichal/2/{run_id}/artifacts/model"
    # logged_model = f'runs:/{RUN_ID}/model'

    # Load model as a PyFuncModel.
    model = mlflow.pyfunc.load_model(logged_model)
    return model

def base64_decode(encoded_data):
    payload = base64.b64decode(encoded_data).decode("utf-8")
    # print("Decoded payload: " + str(payload))
    ride_event = json.loads(payload)
    return ride_event


class ModelService():
    def __init__(self, model, run_id):
        self.model = model
        self.model_version = run_id

    def prepare_features(self, ride):
        features = {}
        features["PU_DO"] = '%s_%s' % (ride["PULocationID"], ride["DOLocationID"])
        return features

    def predict(self, features):
        # X = dv.transform(features)
        # X = xgb.DMatrix(X)
        preds = self.model.predict(features)
        return float(preds[0])
        # return 20.0

    def lambda_handler(self, event):
        # print(json.dumps(event))

        predictions = []

        for record in event['Records']:
            # Kinesis data is base64 encoded so decode here
            encoded_data = record["kinesis"]["data"]
            ride_event = base64_decode(encoded_data)
            # print("Decoded payload: " + str(ride_event))

            ride = ride_event['ride']
            ride_id = ride_event['ride_id']

            features = self.prepare_features(ride)
            prediction = self.predict(features)

            prediction_event = {
                'model': 'ride_duration_prediction_model',
                'version': self.model_version,
                'prediction': {
                    'ride_id': ride_id,
                    'ride_duration': prediction
                    }
            }

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
            'statusCode': 200,
            # 'ride_id': ride_id,
            'predictions': predictions,
            # 'body': json.dumps('Hello from Lambda!')
        }


def init(stream_name: str, run_id: str):
    model = load_model(run_id=run_id)
    model_service = ModelService(model=model, run_id=run_id)
    return model_service