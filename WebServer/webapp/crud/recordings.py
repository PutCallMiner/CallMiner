from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.models.record import Recording


async def get_recordings(
    db: AsyncIOMotorDatabase, skip: int, take: int
) -> list[Recording]:
    records: list[dict] = (
        await db["recordings"].find().skip(skip).limit(take).to_list(None)
    )
    return [Recording.model_validate(record) for record in records]
