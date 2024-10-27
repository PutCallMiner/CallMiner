from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.configs.globals import VECTOR_STORAGE_COLLECTION_NAME
from webapp.configs.intents import INTENTS
from webapp.crud.common import get_vector_storage_client, get_vector_storage_collection
from webapp.crud.recordings import get_recording_by_id
from webapp.crud.vector_storage_manage import (
    delete_embeddings,
    generate_speaker_entries_embeddings,
    retrieve_speaker_entries_intents,
)
from webapp.task_exec.tasks.base import (
    AnalyzeParams,
    RecordingTask,
)


class ConformityCheckTask(RecordingTask):
    async def is_result_in_db(self, db: AsyncIOMotorDatabase, recording_id: str):
        recording = await get_recording_by_id(db, recording_id)
        assert recording is not None
        # TODO: check db entry existence
        return False

    @staticmethod
    def _parse_defined_intents(
        defined_intents: list[dict[str, str | list[str]]],
    ) -> str:
        result = []
        for intent in defined_intents:
            intent_name = intent["intent_name"]
            intent_description = intent["intent"]
            intent_examples = ";".join(intent["examples"])
            result.append(
                f"Intent name: {intent_name}\nIntent description: {intent_description}\nIntent examples: {intent_examples}"
            )
        return "\n".join(result)

    @staticmethod
    def _parse_speaker_intents(speaker_intents: dict[int, str]) -> str:
        result = []
        for entry_id, text in sorted(speaker_intents.items()):
            result.append(f"Entry ID: {entry_id}\nEntry Text: {text}")
        return "\n".join(result)

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

        vector_storage_client = await get_vector_storage_client()
        vector_storage_collection = await get_vector_storage_collection(
            client=vector_storage_client, collection_name=VECTOR_STORAGE_COLLECTION_NAME
        )
        await delete_embeddings(
            vector_storage_collection=vector_storage_collection,
            recording_id=recording_id,
        )
        speaker = recording.get_agent_speaker_id()
        await generate_speaker_entries_embeddings(
            vector_storage_collection=vector_storage_collection,
            recording_id=recording_id,
            transcript=recording.transcript,
            speaker=speaker,
        )
        speaker_intents = await retrieve_speaker_entries_intents(
            vector_storage_collection=vector_storage_collection,
            intents=INTENTS,
            recording_id=recording_id,
            speaker=speaker,
        )

        defined_intents = self._parse_defined_intents(INTENTS)  # noqa: F841
        speaker_intents = self._parse_speaker_intents(speaker_intents)  # noqa: F841

        # TODO: Conformity check API call
        # TODO: Conformity check db results saving
