from collections.abc import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from webapp.configs.globals import MONGO_CONNECTION_STRING, MONGO_DB_NAME


async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase]:
    client = AsyncIOMotorClient(
        MONGO_CONNECTION_STRING,
        connect=True,
    )
    db = client[MONGO_DB_NAME]
    try:
        yield db
    finally:
        db.client.close()
