from collections.abc import AsyncGenerator

import redis.asyncio as redis
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from webapp.configs.globals import (
    MONGO_CONNECTION_STRING,
    MONGO_DB_NAME,
    REDIS_TASKS_DB,
)


async def get_rec_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    client: AsyncIOMotorClient = AsyncIOMotorClient(
        MONGO_CONNECTION_STRING,
        connect=True,
    )
    db = client[MONGO_DB_NAME]
    try:
        yield db
    finally:
        db.client.close()


async def init_rec_db():
    # NOTE: we have to keep the generator, so the connection doesn't close prematurely
    db_gen = get_rec_db()
    db = await anext(db_gen)  # noqa: F821
    await db["recordings"].create_index([("recording_url", 1)], unique=True)


async def get_tasks_db() -> AsyncGenerator[redis.Redis, None]:
    redis_tasks_db = redis.from_url(REDIS_TASKS_DB)
    try:
        yield redis_tasks_db
    finally:
        await redis_tasks_db.close()
