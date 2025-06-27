import os
import model

STREAM_NAME = os.getenv('STREAM_NAME', 'ride_predictions')
RUN_ID = os.getenv("RUN_ID","e0b68d8dd70d4e6fbcaf656cf45a31d5") #Environmental variable e0b68d8dd70d4e6fbcaf656cf45a31d5

model_service = model.init(
    stream_name=STREAM_NAME,
    run_id=RUN_ID
)

def lambda_handler(event, context):
    
    return model_service.lambda_handler(event)
