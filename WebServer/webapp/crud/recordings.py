from collections.abc import Mapping
from typing import Any, Iterable

import bson
import bson.errors
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.results import InsertManyResult, UpdateResult

from webapp.errors import RecordingAlreadyExistsError
from webapp.models.conformity import ConformityResults
from webapp.models.ner import NER
from webapp.models.record import PyObjectId, Recording, RecordingBase, SpeakerMapping
from webapp.models.transcript import Transcript


async def get_recordings(
    db: AsyncIOMotorDatabase,
    query: Mapping[str, Any] | None = None,
    skip: int | None = None,
    take: int | None = None,
) -> list[Recording]:
    query = query or {}
    cursor = db["recordings"].find(query)
    if skip is not None:
        cursor = cursor.skip(skip)
    if take is not None:
        cursor = cursor.limit(take)
    records: list[dict] = await cursor.to_list(None)
    return [Recording.model_validate(record) for record in records]


async def count_recordings(
    db: AsyncIOMotorDatabase, query: Mapping[str, Any] | None = None
) -> int:
    query = query or {}
    return await db["recordings"].count_documents(query)


async def get_recording_by_id(db: AsyncIOMotorDatabase, id: str) -> Recording | None:
    try:
        objectid = bson.ObjectId(id)
    except bson.errors.InvalidId:
        return None

    recording = await db["recordings"].find_one({"_id": objectid})
    if recording is None:
        return None
    return Recording.model_validate(recording)


async def insert_recordings(
    db: AsyncIOMotorDatabase, recordings: list[RecordingBase]
) -> InsertManyResult:
    blob_names = [rec.blob_name for rec in recordings]
    prev_recording_doc = await db["recordings"].find_one(
        {"blob_name": {"$in": list(blob_names)}}
    )
    if prev_recording_doc is not None:
        raise RecordingAlreadyExistsError(
            Recording.model_validate(prev_recording_doc).blob_name
        )
    recording_docs = [rec.model_dump() for rec in recordings]
    result = await db["recordings"].insert_many(recording_docs)
    return result


async def update_with_transcript(
    db: AsyncIOMotorDatabase, recording_id: PyObjectId, transcript: Transcript
) -> UpdateResult:
    """Overwrite 'transcript' field of recording with given transcript data"""
    update_result = await db["recordings"].update_one(
        filter={"_id": bson.ObjectId(recording_id)},
        update={"$set": {"transcript": transcript.model_dump()}},
    )
    return update_result


async def update_with_summary(
    db: AsyncIOMotorDatabase, recording_id: PyObjectId, summary: str
) -> UpdateResult:
    update_result = await db["recordings"].update_one(
        filter={"_id": bson.ObjectId(recording_id)},
        update={"$set": {"summary": summary}},
    )
    return update_result


async def update_with_ner(
    db: AsyncIOMotorDatabase, recording_id: PyObjectId, ner: NER
) -> UpdateResult:
    update_result = await db["recordings"].update_one(
        filter={"_id": bson.ObjectId(recording_id)},
        update={"$set": {"ner": ner.model_dump()}},
    )
    return update_result


async def update_with_speaker_mapping(
    db: AsyncIOMotorDatabase, recording_id: PyObjectId, speaker_mapping: SpeakerMapping
) -> UpdateResult:
    update_result = await db["recordings"].update_one(
        filter={"_id": bson.ObjectId(recording_id)},
        update={
            "$set": {
                "speaker_mapping": {
                    # mongo doesn't accept int as key so we convert it to str
                    str(key): val
                    for key, val in speaker_mapping.items()
                }
            }
        },
    )
    return update_result


async def update_with_duration(
    db: AsyncIOMotorDatabase, recording_id: PyObjectId, duration: int
):
    update_result = await db["recordings"].update_one(
        filter={"_id": bson.ObjectId(recording_id)},
        update={"$set": {"duration": duration}},
    )
    return update_result


async def update_with_conformity(
    db: AsyncIOMotorDatabase,
    recording_id: PyObjectId,
    conformity: ConformityResults,
):
    update_result = await db["recordings"].update_one(
        filter={"_id": bson.ObjectId(recording_id)},
        update={"$set": {"conformity": conformity.model_dump()}},
    )
    return update_result


async def delete_analysis_elements(
    db: AsyncIOMotorDatabase, recording_id: PyObjectId, elem_names: Iterable[str]
):
    update_data = {elem_name: None for elem_name in elem_names}
    update_result = await db["recordings"].update_one(
        filter={"_id": bson.ObjectId(recording_id)}, update={"$set": update_data}
    )
    return update_result
