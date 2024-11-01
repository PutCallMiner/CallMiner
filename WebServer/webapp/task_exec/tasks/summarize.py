from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.configs.globals import MLFLOW_SUMMARIZER_URL
from webapp.crud.recordings import get_recording_by_id, update_with_summary
from webapp.errors import SummarizerError
from webapp.task_exec.tasks.base import (
    AnalyzeParams,
    RecordingTask,
)
from webapp.task_exec.utils import async_request_with_timeout


class SummarizeTask(RecordingTask):
    async def is_result_in_db(self, db: AsyncIOMotorDatabase, recording_id: str):
        recording = await get_recording_by_id(db, recording_id)
        assert recording is not None
        return recording.summary is not None

    async def run(
        self,
        db: AsyncIOMotorDatabase,
        recording_id: str,
        params: AnalyzeParams,
        timeout: float | None = None,
    ):
        recording = await get_recording_by_id(db, recording_id)
        assert recording is not None
        assert recording.transcript is not None

        text = recording.get_conversation_text()

        resp_data = await async_request_with_timeout(
            f"{MLFLOW_SUMMARIZER_URL}/invocations",
            {"instances": [{"conversation": [text]}]},
            timeout,
            SummarizerError,
        )
        summary = resp_data["predictions"][0]

        await update_with_summary(db, recording.id, summary)
