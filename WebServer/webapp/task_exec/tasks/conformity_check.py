import json
from json import JSONDecodeError

from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.configs.globals import (
    MLFLOW_CONFORMITY_CHECK_URL,
    VECTOR_STORAGE_COLLECTION_NAME,
)
from webapp.configs.intents import PREDEFINED_INTENTS, Intent
from webapp.crud.common import get_vector_storage_client, get_vector_storage_collection
from webapp.crud.recordings import get_recording_by_id, update_with_conformity
from webapp.crud.vector_storage_manage import (
    delete_embeddings,
    generate_speaker_entries_embeddings,
    retrieve_speaker_entries_intents,
)
from webapp.errors import ConformityCheckError
from webapp.models.conformity import ConformityResults
from webapp.task_exec.tasks.base import (
    AnalyzeParams,
    RecordingTask,
)
from webapp.task_exec.utils import async_request_with_timeout


class ConformityCheckTask(RecordingTask):
    async def is_result_in_db(
        self, db: AsyncIOMotorDatabase, recording_id: str
    ) -> bool:
        recording = await get_recording_by_id(db, recording_id)
        assert recording is not None
        return recording.conformity_results is not None

    @staticmethod
    def _parse_predefined_intents(
        defined_intents: list[Intent],
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
            intents=PREDEFINED_INTENTS,
            recording_id=recording_id,
            speaker=speaker,
        )

        predefined_intents_parsed = self._parse_predefined_intents(PREDEFINED_INTENTS)  # noqa: F841
        speaker_intents_parsed = self._parse_speaker_intents(speaker_intents)  # noqa: F841

        resp_data = await async_request_with_timeout(
            f"{MLFLOW_CONFORMITY_CHECK_URL}/invocations",
            {
                "instances": [
                    {
                        "predefined_intents": [predefined_intents_parsed],
                        "speaker_intents": [speaker_intents_parsed],
                    }
                ]
            },
            timeout,
            ConformityCheckError,
        )
        try:
            conformity_check: dict = json.loads(resp_data["predictions"][0])  # noqa: F841
        except JSONDecodeError as _:
            raise ConformityCheckError(
                "Failed to load JSON from speaker classifier results"
            )

        conformity_results = ConformityResults.model_validate(
            {"results": conformity_check}
        )
        await update_with_conformity(db, recording_id, conformity_results)
