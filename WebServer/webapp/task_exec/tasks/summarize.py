import requests
from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.celery_app import celery_app
from webapp.configs.globals import MLFLOW_SUMMARIZER_URL
from webapp.crud.recordings import get_recording_by_id, update_with_summary
from webapp.errors import SummarizerError
from webapp.task_exec.tasks.base import TIMEOUT, AnalyzeParams, RecordingTask
from webapp.task_exec.utils import task_to_async


@celery_app.task
def summarize_task(text: str) -> str:
    resp = requests.post(
        f"{MLFLOW_SUMMARIZER_URL}/invocations",
        json={"instances": [{"conversation": [text]}]},
    )
    if not resp.ok:
        raise SummarizerError(resp.content.decode())
    return resp.json()


class SummarizeTask(RecordingTask):
    async def is_result_in_db(self, db: AsyncIOMotorDatabase, recording_id: str):
        recording = await get_recording_by_id(db, recording_id)
        assert recording is not None
        return recording.summary is not None

    async def run(
        self, db: AsyncIOMotorDatabase, recording_id: str, params: AnalyzeParams
    ):
        recording = await get_recording_by_id(db, recording_id)
        assert recording is not None
        assert recording.transcript is not None

        text = recording.transcript.get_text_with_speakers()
        result = await task_to_async(TIMEOUT)(summarize_task)(args=[text])
        summary = result["predictions"][0]

        await update_with_summary(db, recording.id, summary)
