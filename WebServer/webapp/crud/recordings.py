from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.results import InsertManyResult

from webapp.errors import RecordingAlreadyExistsError
from webapp.models.record import Recording


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


async def insert_recordings(
    db: AsyncIOMotorDatabase, recordings: list[Recording]
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
