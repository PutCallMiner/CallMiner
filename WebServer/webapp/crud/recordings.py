import bson
import bson.errors
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.results import InsertManyResult, UpdateResult

from webapp.errors import RecordingAlreadyExistsError
from webapp.models.record import PyObjectId, Recording, RecordingBase
from webapp.models.transcript import Transcript


async def get_recordings(
    db: AsyncIOMotorDatabase, skip: int | None = None, take: int | None = None
) -> list[Recording]:
    cursor = db["recordings"].find()
    if skip is not None:
        cursor = cursor.skip(skip)
    if take is not None:
        cursor = cursor.limit(take)
    records: list[dict] = await cursor.to_list(None)
    return [Recording.model_validate(record) for record in records]


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
    recording_urls = [rec.recording_url for rec in recordings]
    prev_recording_doc = await db["recordings"].find_one(
        {"recording_url": {"$in": list(recording_urls)}}
    )
    if prev_recording_doc is not None:
        raise RecordingAlreadyExistsError(
            Recording.model_validate(prev_recording_doc).recording_url
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
