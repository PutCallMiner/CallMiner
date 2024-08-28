import json
import logging
import os
import requests  # type: ignore
from webapp.celery_app import celery_app
from webapp.configs.globals import MLFLOW_ASR_URL
from webapp.errors import ASRError
from webapp.models.transcript import Transcript


@celery_app.task
def asr_task(audio_bytes_encoded: str, asr_params_dict: dict) -> Transcript:
    logging.info(json.dumps(dict(os.environ), indent=4))
    resp = requests.post(
        f"{MLFLOW_ASR_URL}/invocations",
        json={"dataframe_records": [audio_bytes_encoded], "params": asr_params_dict},
    )
    if not resp.ok:
        raise ASRError(resp.content.decode())
    return resp.json()
