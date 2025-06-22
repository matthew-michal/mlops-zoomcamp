import json
import base64
import boto3
import os
import mlflow

kinesis_client = boto3.client('kinesis')
STREAM_NAME = os.getenv('STREAM_NAME', 'ride_predictions')


# MLFLOW_TRACKING_URI = "http://ec2-3-80-40-111.compute-1.amazonaws.com:5000/"
RUN_ID = os.getenv("RUN_ID") #Environmental variable e0b68d8dd70d4e6fbcaf656cf45a31d5

# mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
# mlflow.set_experiment("nyc-taxi-exp")

logged_model = f"s3://mlflow-artifact-mmichal/2/{RUN_ID}/artifacts/model"
# logged_model = f'runs:/{RUN_ID}/model'

# Load model as a PyFuncModel.
model = mlflow.pyfunc.load_model(logged_model)

def prepare_features(ride):
    features = {}
    features["PU_DO"] = '%s_%s' % (ride["PULocationID"], ride["DOLocationID"])
    return features

def predict(features):
    # X = dv.transform(features)
    # X = xgb.DMatrix(X)
    preds = model.predict(features)
    return float(preds[0])
    # return 20.0

def lambda_handler(event, context):
    # print(json.dumps(event))

    predictions = []

    for record in event['Records']:
        # Kinesis data is base64 encoded so decode here
        payload = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")
        print("Decoded payload: " + str(payload))
        ride_event = json.loads(payload)
        # print("Decoded payload: " + str(ride_event))

        ride = ride_event['ride']
        ride_id = ride_event['ride_id']

        features = prepare_features(ride)
        prediction = predict(features)

        prediction_event = {
            'model': 'ride_duration_prediction_model',
            'version': '123',
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
