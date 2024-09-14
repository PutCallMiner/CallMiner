from typing import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from webapp.configs.globals import MONGO_CONNECTION_STRING, MONGO_DB_NAME


async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    client: AsyncIOMotorClient = AsyncIOMotorClient(
        MONGO_CONNECTION_STRING,
        connect=True,
    )
    db = client[MONGO_DB_NAME]
    try:
        yield db
    finally:
        db.client.close()


async def init_db():
    # NOTE: we have to keep the generator, so the connection doesn't close prematurely
    db_gen = get_db()
    db = await anext(db_gen)  # noqa
    await db["recordings"].create_index([("recording_url", 1)], unique=True)
