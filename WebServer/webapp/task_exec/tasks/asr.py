import base64
import json
import logging
import os
from typing import Any, Literal

import requests
from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.celery_app import celery_app
from webapp.configs.globals import AZURE_SAS_TOKEN, MLFLOW_ASR_URL
from webapp.crud.recordings import get_recording_by_id, update_with_transcript
from webapp.errors import ASRError, RecordingNotFoundError
from webapp.models.transcript import Transcript
from webapp.task_exec.tasks.base import AnalyzeParams, RecordingTask
from webapp.task_exec.utils import task_to_async
from webapp.utils.azure import download_azure_blob


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


class ASRTask(RecordingTask):
    async def is_result_in_db(self, db: AsyncIOMotorDatabase, recording_id: str):
        recording = await get_recording_by_id(db, recording_id)
        assert recording is not None
        return recording.transcript is not None

    async def run(
        self,
        db: AsyncIOMotorDatabase,
        recording_id: str,
        params: AnalyzeParams,
        timeout: float | None = None,
    ):
        recording = await get_recording_by_id(db, recording_id)
        if recording is None:
            raise RecordingNotFoundError(recording_id)
        audio_bytes = await download_azure_blob(
            recording.recording_url, AZURE_SAS_TOKEN
        )

        # Run celery task
        result = await task_to_async(timeout=timeout)(asr_task)(
            args=[base64.b64encode(audio_bytes).decode(), params.asr.model_dump()]
        )

        # Write results to DB
        transcript_raw = result["predictions"][0]
        transcript = Transcript.model_validate({"entries": transcript_raw})
        await update_with_transcript(db, recording_id, transcript)
        return transcript
