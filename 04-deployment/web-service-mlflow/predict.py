import pickle
import xgboost as xgb
from flask import Flask, request, jsonify
import mlflow
import os
from mlflow.tracking import MlflowClient

MLFLOW_TRACKING_URI = "http://ec2-3-80-40-111.compute-1.amazonaws.com:5000/"
RUN_ID = os.getenv("RUN_ID") #Environmental variable e0b68d8dd70d4e6fbcaf656cf45a31d5

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("nyc-taxi-exp")

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
    return preds

app = Flask("duration-prediction")

@app.route('/predict', methods=["POST"])
def predict_endpoint():
    ride = request.get_json()
    features = prepare_features(ride)
    pred = predict(features).tolist()

    result = {
        "duration" : pred,
        "model_version": RUN_ID
    }

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)