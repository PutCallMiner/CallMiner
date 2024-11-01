import re

from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.configs.globals import MLFLOW_NER_URL
from webapp.crud.recordings import get_recording_by_id, update_with_ner
from webapp.errors import NERError
from webapp.models.ner import NER, NEREntry
from webapp.task_exec.tasks.base import (
    AnalyzeParams,
    RecordingTask,
)
from webapp.task_exec.utils import async_request_with_timeout


class NERTask(RecordingTask):
    async def is_result_in_db(self, db: AsyncIOMotorDatabase, recording_id: str):
        recording = await get_recording_by_id(db, recording_id)
        assert recording is not None
        return recording.ner is not None

    @staticmethod
    def parse_ner_output(text: str) -> NER:
        """Takes output from NER model in the following form: <|Speaker x|> Text <entity>text</entity>\n...
        Converts it into list of lists of NER Entries to match the transcript, each entry in the outer
        list matches entry in transcript and each entry in the inner lists is an entity with addresses of
        characters relative to the current transcript entry
        """
        ner = NER(entries=[])
        components = re.finditer(r"<\|(?P<speaker_class>.+?)\|> (?P<text>.+)", text)
        for component in components:
            ner_entries = []
            tags_chars = 0
            matches = re.finditer(
                r"<(?P<entity>[a-zA-Z]+)>.*?</(?P=entity)>", component.group("text")
            )
            for match in matches:
                entity = match.group("entity")
                start_char = match.span()[0] - tags_chars
                tags_chars = tags_chars + 5 + 2 * len(entity)
                end_char = match.span()[1] - tags_chars
                ner_entries.append(
                    NEREntry(
                        entity=entity,
                        start_char=start_char,
                        end_char=end_char,
                    )
                )
            ner.entries.append(ner_entries)
        return ner

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

        text = recording.get_conversation_text(left="<|", right="|> ")
        resp_data = await async_request_with_timeout(
            f"{MLFLOW_NER_URL}/invocations",
            {"instances": [text]},
            timeout,
            NERError,
        )
        ner = self.parse_ner_output(resp_data["predictions"][0])
        await update_with_ner(db, recording.id, ner)
