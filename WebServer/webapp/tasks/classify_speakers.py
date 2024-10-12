import json
from json import JSONDecodeError
from typing import Literal

import requests

from webapp.celery_app import celery_app
from webapp.configs.globals import (
    MLFLOW_SPEAKER_CLASSIFIER_URL,
    SPEAKER_CLASSIFIER_NUM_ENTRIES,
)
from webapp.errors import SpeakerClassifierError
from webapp.models.transcript import Transcript
from webapp.tasks.utils import task_to_async


@celery_app.task
def classify_speaker_task(text: str) -> str:
    resp = requests.post(
        f"{MLFLOW_SPEAKER_CLASSIFIER_URL}/invocations",
        json={"instances": [{"conversation": [text]}]},
    )
    if not resp.ok:
        raise SpeakerClassifierError(resp.content.decode())
    return resp.json()


async def run_classify_speaker_task(
    transcript: Transcript, timeout: float
) -> dict[str, Literal["agent", "client"]]:
    text = transcript.get_n_entries_text_with_speakers(SPEAKER_CLASSIFIER_NUM_ENTRIES)
    result = await task_to_async(timeout)(classify_speaker_task)(args=[text])
    try:
        speaker_classifier_mapping: dict = json.loads(result["predictions"][0])
    except JSONDecodeError as _:
        raise SpeakerClassifierError(
            "Failed to load JSON from speaker classifier results"
        )
    return speaker_classifier_mapping
