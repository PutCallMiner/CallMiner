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
    def parse_ner_output(text: str, ents) -> NER:
        """Takes the text that was used for NER and entities that were found
        Parses the entities and adjusts start and end positions to match the
        positions in conversation split by paragraphs
        """
        ner = NER(entries=[])

        par_start = 0
        i = 0
        for paragraph in text.split("\n"):
            entities = []
            speaker_label = paragraph.split(": ")[0]
            speaker_label_len = len(speaker_label) + 2
            par_end = par_start + len(paragraph) + 1

            while True:
                if i >= len(ents):
                    break
                cur_ent = ents[i]

                if cur_ent["end"] < par_end:
                    entities.append(
                        NEREntry(
                            entity=cur_ent["label"],
                            start_char=cur_ent["start"] - par_start - speaker_label_len,
                            end_char=cur_ent["end"] - par_start - speaker_label_len,
                        )
                    )
                    i += 1
                else:
                    break
            ner.entries.append(entities)
            par_start = par_end
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

        text = recording.get_conversation_text(sep="\n")
        resp_data = await async_request_with_timeout(
            f"{MLFLOW_NER_URL}/invocations",
            {"instances": [text]},
            timeout,
            NERError,
        )
        ner = self.parse_ner_output(text, resp_data["predictions"][0]["ents"])
        await update_with_ner(db, recording.id, ner)
