FROM python:3.12.1-slim

RUN pip install -U pip
RUN pip install pipenv

WORKDIR /app

COPY [ "Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --system --deploy

COPY [ "04-deployment/web-service/predict.py", "04-deployment/web-service/xgb_reg.bin","04-deployment/web-service/lin_reg.bin", "./"]

EXPOSE 9696

ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0:9696", "predict:app"]