import json
from json import JSONDecodeError
import re
from typing import cast

from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.configs.globals import (
    MLFLOW_SPEAKER_CLASSIFIER_URL,
    SPEAKER_CLASSIFIER_NUM_ENTRIES,
)
from webapp.crud.recordings import get_recording_by_id, update_with_speaker_mapping
from webapp.errors import SpeakerClassifierError
from webapp.task_exec.tasks.base import (
    AnalyzeParams,
    RecordingTask,
)
from webapp.models.record import SpeakerMapping, SpeakerClass
from webapp.task_exec.utils import async_request_with_timeout


def parse_speaker_mapping(input_dict: dict[str, str]) -> SpeakerMapping:
    """Function to parse dict from {"speaker 0": "client" ...} to {0: "client"}"""
    result: SpeakerMapping = {}
    for key, value in input_dict.items():
        match = re.match(r"speaker (\d+)", key, re.IGNORECASE)
        if match:
            speaker_number = int(match.group(1))
            result[speaker_number] = cast(SpeakerClass, value)
    return result


class SpeakerClassifyTask(RecordingTask):
    async def is_result_in_db(self, db: AsyncIOMotorDatabase, recording_id: str):
        recording = await get_recording_by_id(db, recording_id)
        assert recording is not None
        return recording.speaker_mapping is not None

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

        text = recording.transcript.get_n_entries_text_with_speakers(
            SPEAKER_CLASSIFIER_NUM_ENTRIES
        )

        resp_data = await async_request_with_timeout(
            f"{MLFLOW_SPEAKER_CLASSIFIER_URL}/invocations",
            {"instances": [{"conversation": [text]}]},
            timeout,
            SpeakerClassifierError,
        )
        try:
            speaker_mapping = parse_speaker_mapping(
                json.loads(resp_data["predictions"][0])
            )
        except JSONDecodeError as _:
            raise SpeakerClassifierError(
                "Failed to load JSON from speaker classifier results"
            )
        await update_with_speaker_mapping(db, recording.id, speaker_mapping)
