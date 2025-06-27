import model

def test_prepare_features():
    model_service = model.ModelService(None, '123')
    ride = {
        "PULocationID": 130,
        "DOLocationID": 205,
        
    }
    actual_features = model_service.prepare_features(ride)
    expected_features = {
        "PU_DO": "130_205"
    }

    assert actual_features == expected_features

    # assert 1 == 1

def test_base64_decode():
    base64_input = b'eyJQVUxvY2F0aW9uSUQiOiAxMzAsICJET0xvY2F0aW9uSUQiOiAyMDV9'
    actual_decoding = model.base64_decode(base64_input)
    expected_decoding = {
        "PULocationID": 130,
        "DOLocationID": 205,
        
    }
    print(actual_decoding)

    assert actual_decoding == expected_decoding

class ModelMock:
    def __init__(self, value) -> None:
        self.value = value

    def predict(self, X):
        n = len(X)
        return [self.value] * n

def test_predict():
    modelmock = ModelMock(10.0)
    model_service = model.ModelService(modelmock, '123')
    features = {
        "PU_DO": "130_205"
    }
    actual_preds = model_service.predict(features=features)
    expected_preds = 10.0

    assert actual_preds == expected_preds

def test_lambda_handler():
    modelmock = ModelMock(10.0)
    model_version = '123'
    model_service = model.ModelService(modelmock, model_version)
    event = {
        "Records": [{
                "kinesis": {
                    "data": "ewoicmlkZSI6IHsKIlBVTG9jYXRpb25JRCI6MTMwLAoiRE9Mb2NhdGlvbklEIjoyMDUKfSwKInJpZGVfaWQiOjI1Ngp9"
                }
            }]
    }
    actual_load = model_service.lambda_handler(event=event)
    expected_load = {'statusCode': 200, 'predictions': [{'model': 'ride_duration_prediction_model', 'version': model_version, 'prediction': {'ride_id': 256, 'ride_duration': 10.0}}]}

    assert actual_load == expected_load
    pass