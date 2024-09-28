import base64
import json
import logging
import os
from typing import Any, Literal

import requests
from celery.exceptions import TimeoutError  # type: ignore[import-untyped]

from webapp.celery_app import celery_app
from webapp.configs.globals import MLFLOW_ASR_URL
from webapp.errors import ASRError, TaskTimeoutError
from webapp.models.analysis import ASRParams
from webapp.models.transcript import Transcript


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
    asr_result = asr_task.apply_async(
        args=[base64.b64encode(audio_bytes).decode(), asr_params.model_dump()]
    )
    try:
        transcript_raw = asr_result.get(timeout=timeout)["predictions"][0]
    except TimeoutError as _:
        raise TaskTimeoutError(asr_task.name, asr_result.id)
    transcript = Transcript.model_validate({"entries": transcript_raw})
    return transcript
