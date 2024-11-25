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
    def fix_locations(text: str, array: list) -> list:
        """Takes the text that was used in spacy pipeline and array that is the output
        of the pipeline, e.g.: [{"start": 10, "end": 15, "label": "persName"}, ...]
        function fixes the locations (start and end) of all objects in the array in a
        way that corresponds to conversation text. (list of lists of entries without speaker labels)
        """
        fixed_entries = []
        par_start = 0
        i = 0
        for paragraph in text.split("\n"):
            entries = []

            speaker_label = paragraph.split(": ")[0]
            speaker_label_len = len(speaker_label) + 2
            par_end = par_start + len(paragraph) + 1

            while i < len(array):
                cur = array[i]

                if cur["end"] < par_end:
                    i += 1
                    fixed = cur.copy()
                    fixed["start"] -= par_start + speaker_label_len
                    if fixed["start"] < 0:
                        continue
                    fixed["end"] -= par_start + speaker_label_len
                    entries.append(fixed)
                else:
                    break
            fixed_entries.append(entries)
            par_start = par_end
        return fixed_entries

    @staticmethod
    def merge_siblings(ents: list) -> list:
        """Merges sibling entities with the same label"""
        merged_ents = []
        for ent_list in ents:
            new_list = []
            i = 0
            while i < len(ent_list) - 1:
                ent1 = ent_list[i]
                ent2 = ent_list[i + 1]
                if ent1["label"] == ent2["label"] and ent1["end"] == ent2["start"]:
                    ent1["end"] = ent2["end"]
                    new_list.append(ent1)
                    i += 2
                else:
                    new_list.append(ent1)
                    i += 1
            if i == len(ent_list) - 1:
                new_list.append(ent_list[-1])
            merged_ents.append(new_list)
        return merged_ents

    @staticmethod
    def parse_ner_endpoint_results(ents: list, tokens: list) -> NER:
        """Combines the output of spacy pipeline into a NER object"""
        ner = NER(entries=[])
        for ent_entries, token_entries in zip(ents, tokens):
            entries = []
            ti = 0
            for ent_entry in ent_entries:
                while ent_entry["start"] != token_entries[ti]["start"]:
                    ti += 1

                ner_entry = NEREntry(
                    entity=ent_entry["label"],
                    start_char=ent_entry["start"],
                    end_char=ent_entry["end"],
                    lemmas=list(),
                )
                while True:
                    ner_entry.lemmas.append(token_entries[ti]["lemma"])
                    if ent_entry["end"] == token_entries[ti]["end"]:
                        break
                    ti += 1
                entries.append(ner_entry)
            ner.entries.append(entries)
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
        prediction = resp_data["predictions"][0]
        ents = self.fix_locations(text, prediction["ents"])
        tokens = self.fix_locations(text, prediction["tokens"])

        merged = self.merge_siblings(ents)
        ner_results = self.parse_ner_endpoint_results(merged, tokens)
        await update_with_ner(db, recording.id, ner_results)
