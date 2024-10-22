import json
from json import JSONDecodeError

import requests
from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.celery_app import celery_app
from webapp.configs.globals import (
    MLFLOW_SPEAKER_CLASSIFIER_URL,
    SPEAKER_CLASSIFIER_NUM_ENTRIES,
)
from webapp.crud.recordings import get_recording_by_id, update_with_speaker_mapping
from webapp.errors import SpeakerClassifierError
from webapp.tasks.base import TIMEOUT, AnalyzeParams, DatabaseTask
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


class SpeakerClassifyTask(DatabaseTask):
    async def run(
        self, db: AsyncIOMotorDatabase, recording_id: str, params: AnalyzeParams
    ):
        recording = await get_recording_by_id(db, recording_id)
        assert recording is not None
        assert recording.transcript is not None

        text = recording.transcript.get_n_entries_text_with_speakers(
            SPEAKER_CLASSIFIER_NUM_ENTRIES
        )
        result = await task_to_async(TIMEOUT)(classify_speaker_task)(args=[text])
        try:
            speaker_classifier_mapping: dict = json.loads(result["predictions"][0])
        except JSONDecodeError as _:
            raise SpeakerClassifierError(
                "Failed to load JSON from speaker classifier results"
            )

        await update_with_speaker_mapping(db, recording.id, speaker_classifier_mapping)
