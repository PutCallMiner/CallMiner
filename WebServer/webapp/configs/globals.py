import logging
import os

# mongo
MONGO_ROOT_USERNAME = os.environ["MONGO_ROOT_USERNAME"]
MONGO_ROOT_PASSWORD = os.environ["MONGO_ROOT_PASSWORD"]
MONGO_DB_NAME = os.environ["MONGO_DB_NAME"]
MONGO_HOST = os.environ["MONGO_HOST"]
MONGO_PORT = os.environ["MONGO_PORT"]
MONGO_CONNECTION_STRING = (
    f"mongodb://{MONGO_ROOT_USERNAME}:{MONGO_ROOT_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"
)

# redis
REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = os.environ["REDIS_PORT"]
REDIS_TASKS_DB = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"

# celery
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# azure
AZURE_STORAGE_CONNECTION_STRING = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
AZURE_SAS_TOKEN = os.environ["AZURE_SAS_TOKEN"]

# mlflow models
MLFLOW_ASR_URL = os.environ["MLFLOW_ASR_URL"]
MLFLOW_SUMMARIZER_URL = os.environ["MLFLOW_SUMMARIZER_URL"]
MLFLOW_SPEAKER_CLASSIFIER_URL = os.environ["MLFLOW_SPEAKER_CLASSIFIER_URL"]

SPEAKER_CLASSIFIER_NUM_ENTRIES = 8

logger = logging.getLogger("uvicorn")
