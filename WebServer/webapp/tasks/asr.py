import base64
import json
import logging
import os
from typing import Any, Literal

import requests

from webapp.celery_app import celery_app
from webapp.configs.globals import MLFLOW_ASR_URL
from webapp.errors import ASRError
from webapp.models.analysis import ASRParams
from webapp.models.transcript import Transcript
from webapp.tasks.utils import task_to_async


@celery_app.task
def asr_task(
    audio_bytes_encoded: str, asr_params_dict: dict
) -> dict[Literal["predictions"], list[Any]]:
    logging.info(json.dumps(dict(os.environ), indent=4))
    resp = requests.post(
        f"{MLFLOW_ASR_URL}/invocations",
        json={"dataframe_records": [audio_bytes_encoded], "params": asr_params_dict},
    )
    if not resp.ok:
        raise ASRError(resp.content.decode())
    return resp.json()


async def run_asr_task(
    audio_bytes: bytes,
    asr_params: ASRParams,
    timeout: float,
) -> Transcript:
    result = await task_to_async(timeout=timeout)(asr_task)(
        args=[base64.b64encode(audio_bytes).decode(), asr_params.model_dump()]
    )
    transcript_raw = result["predictions"][0]

    transcript = Transcript.model_validate({"entries": transcript_raw})
    return transcript
