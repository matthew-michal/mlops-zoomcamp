#!/usr/bin/env python
# coding: utf-8
import pickle
import pandas as pd
import os
import sys
import uuid
# import mlflow

from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error
from sklearn.pipeline import make_pipeline


# MLFLOW_TRACKING_URI = "http://ec2-3-80-40-111.compute-1.amazonaws.com:5000/"



# mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
# mlflow.set_experiment("nyc-taxi-exp")

def generate_uuids(n):
    return [str(uuid.uuid4()) for i in range(n)]

def read_dataframe(filename: str, year: int, month: int):
    print("Preparing dataframe")
    df = pd.read_parquet(filename)
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')

    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df.duration = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)]

    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)
    return df


def prepare_dictionaries(df: pd.DataFrame):
    print("Preparing dictionaries")
    df['PU_DO'] = df['PULocationID'] + '_' + df['DOLocationID']
    categorical = ['PU_DO']
    numerical = ['trip_distance']
    dicts = df[categorical + numerical].to_dict(orient='records')
    return dicts


def load_model(run_id):
    print("Loading Model")
    # logged_model = f"s3://mlflow-artifact-mmichal/2/{run_id}/artifacts/model"
    # model = mlflow.pyfunc.load_model(logged_model)
    with open('./model.bin', 'rb') as f_in:
        (dv, model) = pickle.load(f_in)
    return dv, model

def apply_model(input_file, run_id, output_file, year, month):
    df = read_dataframe(input_file, year, month)
    dicts = prepare_dictionaries(df)

    # Load model as a PyFuncModel.
    (dv, model) = load_model(run_id) # logged_model
    print("Applying Model")
    y_pred = model.predict(dv.transform(dicts))
    df_results = pd.DataFrame()#y_pred
    df_results['ride_id'] = df['ride_id']
    df_results['lpep_dropoff_datetime'] = df.tpep_dropoff_datetime
    df_results['PULocationID'] = df.PULocationID
    df_results['DOLocationID'] = df.DOLocationID
    df_results['actual_duration'] = df.duration
    df_results['predicted_duration'] = y_pred
    df_results['model_version'] = run_id
    df_results['diff'] = df_results['actual_duration'] - y_pred

    print(df_results.predicted_duration.mean())

    # df_results.to_parquet(
    #     output_file,
    #     engine='pyarrow',
    #     compression=None,
    #     index=False
    # )


def main():
    taxi_type = sys.argv[1] #'green'
    year = int(sys.argv[2]) #2023
    month = int(sys.argv[3]) #2
    
    RUN_ID = os.getenv("RUN_ID","e0b68d8dd70d4e6fbcaf656cf45a31d5") #Environmental variable e0b68d8dd70d4e6fbcaf656cf45a31d5

    input_file = f'https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet'
    output_file = f'output/{taxi_type}/{year:04d}-{month:02d}_predicted.parquet'

    apply_model(input_file, RUN_ID, output_file, year, month)

if __name__ == '__main__':
    main()