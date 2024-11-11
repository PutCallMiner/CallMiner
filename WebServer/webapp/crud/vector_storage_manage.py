from chromadb import Metadata, Where
from chromadb.api.models.AsyncCollection import AsyncCollection
from chromadb.api.types import OneOrMany, QueryResult

from webapp.configs.globals import N_CLOSEST_EMBEDDINGS
from webapp.configs.intents import Intent
from webapp.models.transcript import Transcript


async def generate_embeddings(
    vector_storage_collection: AsyncCollection,
    ids: list[str],
    documents: list[str],
    metadatas: OneOrMany[Metadata],
) -> None:
    await vector_storage_collection.add(ids, documents=documents, metadatas=metadatas)


async def delete_embeddings(
    vector_storage_collection: AsyncCollection, recording_id: str
) -> None:
    await vector_storage_collection.delete(where={"recording_id": recording_id})


async def retrieve_embeddings(
    vector_storage_collection: AsyncCollection,
    query_texts: list[str],
    where_condition: dict | None,
    n_results: int,
) -> QueryResult:
    query_result = await vector_storage_collection.query(
        query_texts=query_texts, n_results=n_results, where=where_condition
    )
    return query_result


async def generate_speaker_entries_embeddings(
    vector_storage_collection: AsyncCollection,
    recording_id: str,
    transcript: Transcript,
    speaker: int,
) -> None:
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[Metadata] = []
    for i, entry in enumerate(transcript.entries):
        if entry.speaker == speaker:
            ids.append(f"{recording_id}:{i}")
            documents.append(entry.text)
            metadatas.append(
                {"recording_id": recording_id, "entry_id": i, "speaker": speaker}
            )

    await generate_embeddings(
        vector_storage_collection=vector_storage_collection,
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )


async def retrieve_speaker_entries_intents(
    vector_storage_collection: AsyncCollection,
    intents: list[Intent],
    recording_id: str,
    speaker: int,
) -> dict[int, str]:
    result = {}
    where_condition = metadata_to_where_condition(
        {"recording_id": recording_id, "speaker": speaker}
    )
    for intent in intents:
        intent_examples = intent["examples"]

        for example in intent_examples:
            embeddings = await retrieve_embeddings(
                vector_storage_collection=vector_storage_collection,
                query_texts=[example],
                where_condition=where_condition,
                n_results=N_CLOSEST_EMBEDDINGS,
            )
            assert (
                embeddings["documents"] is not None
                and embeddings["metadatas"] is not None
            )
            for doc, metadata in zip(
                embeddings["documents"][0], embeddings["metadatas"][0]
            ):
                entry_id = metadata["entry_id"]
                assert isinstance(entry_id, int)
                if entry_id not in result:
                    result[entry_id] = doc

    return result


def metadata_to_where_condition(
    metadata: Metadata,
) -> Where:
    where_condition: Where = {"$and": [{key: value} for key, value in metadata.items()]}
    return where_condition
