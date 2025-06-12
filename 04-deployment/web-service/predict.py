import pickle
import xgboost as xgb
from flask import Flask, request, jsonify

with open('./xgb_reg.bin', 'rb') as f_in:
    (dv, model) = pickle.load(f_in)

def prepare_features(ride):
    features = {}
    features["PU_DO"] = '%s_%s' % (ride["PULocationID"], ride["DOLocationID"])
    return features

def predict(features):
    X = dv.transform(features)
    X = xgb.DMatrix(X)
    preds = model.predict(X)
    return preds

app = Flask("duration-prediction")

@app.route('/predict', methods=["POST"])
def predict_endpoint():
    ride = request.get_json()
    features = prepare_features(ride)
    pred = predict(features).tolist()

    result = {
        "duration" : pred
    }

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)