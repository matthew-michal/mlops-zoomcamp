#!/usr/bin/env python
# coding: utf-8


# In[2]:


import mlflow
import pickle
import argparse
from pathlib import Path

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import xgboost as xgb
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient

from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
from hyperopt.pyll import scope
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.metrics import mean_squared_error, root_mean_squared_error



# mlflow.set_tracking_uri("sqlite:///mlflow.db")
MLFLOW_TRACKING_URI = "http://localhost:5000"
EXPERIMENT_NAME = "nyc-taxi-exp"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)
mlflow.xgboost.autolog(disable=True)

models_folder = Path('models')
models_folder.mkdir(exist_ok=True)

def read_clean_df(year, month):
    url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_{year}-{month:02d}.parquet'
    df = pd.read_parquet(url)

    df['lpep_dropoff_datetime'] = pd.to_datetime(df['lpep_dropoff_datetime'])
    df['lpep_pickup_datetime'] = pd.to_datetime(df['lpep_pickup_datetime'])

    df['duration'] = df['lpep_dropoff_datetime'] - df['lpep_pickup_datetime']
    df['duration'] = df['duration'].apply(lambda x: x.total_seconds() / 60)

    df = df.loc[((df.duration >= 1) & (df.duration <= 60))]

    cat_feats = ['PULocationID', 'DOLocationID']
    df[cat_feats] = df[cat_feats].astype(str)

    df['PU_DO'] = df['PULocationID'] + '_' + df['DOLocationID']

    return df


# df_train = read_clean_df(year=2023, month=1)
# df_valid = read_clean_df(year=2023, month=2)
# df_test = read_clean_df(year=2023, month=3)

def create_X(df, dv=None):
    cat_feats = ['PU_DO']
    
    dicts = df[cat_feats].to_dict(orient='records')

    if dv is None:
        dv = DictVectorizer(sparse=True)
        X = dv.fit_transform(dicts)
    else:
        X = dv.transform(dicts)
    
    return X, dv
    
# X_train, dv = create_X(df_train)
# X_val, _ = create_X(df_valid, dv=dv)
# X_test, _ = create_X(df_test, dv=dv)

# target = 'duration'
# y_train = df_train[target].values
# y_valid = df_valid[target].values
# y_test = df_test[target].values

def train_model(X_train, y_train, X_valid, y_valid, dv):
    with mlflow.start_run() as run:
        train = xgb.DMatrix(X_train, label=y_train)
        valid = xgb.DMatrix(X_valid, label=y_valid)
        params = {
            'learning_rate':0.18772960331122643,
            'max_depth':84,
            'min_child_weight':4.414579549205784,
            'objective':'reg:linear',
            'reg_alpha': 0.05803027983214606,
            'reg_lambda':0.028651500789683607,
            'seed':42
        }
    
        mlflow.log_params(params)
    
        booster = xgb.train(
            params=params,
            dtrain=train,
            num_boost_round=1000,
            evals=[(valid, "validation")],
            early_stopping_rounds = 50
        )
    
    
    
        y_pred = booster.predict(valid)
        rmse = root_mean_squared_error(y_valid, y_pred)
        mlflow.log_metric("rmse", rmse)
    
        with open("models/preprocessor.b", 'wb') as f_out:
            pickle.dump(dv, f_out)
    
        mlflow.log_artifact("models/preprocessor.b", artifact_path="preprocessor")

        mlflow.xgboost.log_model(booster, artifact_path="models_mlflow")

        return run.info.run_id



# with open('models/xgb_reg.bin', 'wb') as f_out:
#     pickle.dump((dv, booster), f_out)

def main(year, month):
    df_train = read_clean_df(year=year, month=month)

    next_month = month +1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    df_valid = read_clean_df(year=next_year, month=next_month)

    X_train, dv = create_X(df_train)
    X_valid, _ = create_X(df_valid, dv=dv)

    target = 'duration'
    y_train = df_train[target].values
    y_valid = df_valid[target].values

    train_model(X_train, y_train, X_valid, y_valid, dv)

if __name__ == "__main__":
    # use argparse to get year and month from the command line
    parser = argparse.ArgumentParser(description='Train a model to predict taxi trip duration.')
    parser.add_argument('--year', type=int, required=True, help='Year of the data to train on')
    parser.add_argument('--month', type=int, required=True, help='Month of the data to train on')
    args = parser.parse_args()
    
    run_id = main(year=args.year, month=args.month)
    print(run_id)
    with open('run_id.txt','w') as f_out:
        f_out.write(run_id)
    
