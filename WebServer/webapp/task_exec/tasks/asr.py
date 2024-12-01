import base64

from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.configs.globals import MLFLOW_ASR_URL
from webapp.crud.common import get_blob_storage_client_context
from webapp.crud.recordings import (
    get_recording_by_id,
    update_with_duration,
    update_with_transcript,
)
from webapp.errors import ASRError, RecordingNotFoundError
from webapp.models.transcript import Transcript
from webapp.task_exec.tasks.base import (
    AnalyzeParams,
    RecordingTask,
)
from webapp.task_exec.utils import async_request_with_timeout
from webapp.utils.audio import get_audio_duration


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
        async with get_blob_storage_client_context() as storage_client:
            blob_client = storage_client.get_blob_client(
                "audio-records", recording.blob_name
            )
            blob = await blob_client.download_blob()
            audio_bytes = await blob.readall()
            duration = get_audio_duration(audio_bytes)
        await update_with_duration(db, recording_id, duration)

        # Run celery task
        audio_bytes_encoded = base64.b64encode(audio_bytes).decode()
        resp_data = await async_request_with_timeout(
            f"{MLFLOW_ASR_URL}/invocations",
            {
                "dataframe_records": [audio_bytes_encoded],
                "params": params.asr.model_dump(),
            },
            timeout,
            ASRError,
        )

        # Write results to DB
        transcript_raw = resp_data["predictions"][0]
        transcript = Transcript.model_validate({"entries": transcript_raw})
        await update_with_transcript(db, recording_id, transcript)
        return transcript
