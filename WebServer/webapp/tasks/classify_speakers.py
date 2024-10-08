import json
from json import JSONDecodeError
from typing import Literal

import requests
from celery.exceptions import TimeoutError  # type: ignore[import-untyped]

from webapp.celery_app import celery_app
from webapp.configs.globals import (
    MLFLOW_SPEAKER_CLASSIFIER_URL,
    SPEAKER_CLASSIFIER_NUM_ENTRIES,
)
from webapp.errors import SpeakerClassifierError, TaskTimeoutError
from webapp.models.transcript import Transcript


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
    speaker_classifier_result = classify_speaker_task.apply_async(args=[text])
    try:
        speaker_classifier_mapping: dict = json.loads(
            speaker_classifier_result.get(timeout=timeout)["predictions"][0]
        )
    except TimeoutError as _:
        raise TaskTimeoutError(classify_speaker_task.name, speaker_classifier_result.id)
    except JSONDecodeError as _:
        raise SpeakerClassifierError(
            "Failed to load JSON from speaker classifier results"
        )
    return speaker_classifier_mapping
