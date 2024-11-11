from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import chromadb
import redis.asyncio as redis
from chromadb import AsyncClientAPI
from chromadb.api.models.AsyncCollection import AsyncCollection
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from webapp.configs.globals import (
    CHROMADB_HOST,
    CHROMADB_PORT,
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


get_rec_db_context = asynccontextmanager(get_rec_db)


async def init_rec_db():
    # NOTE: we have to keep the generator, so the connection doesn't close prematurely
    async with get_rec_db_context() as db:
        await db["recordings"].create_index([("recording_url", 1)], unique=True)


async def get_tasks_db() -> AsyncGenerator[redis.Redis, None]:
    redis_tasks_db = redis.from_url(REDIS_TASKS_DB)
    try:
        yield redis_tasks_db
    finally:
        await redis_tasks_db.close()


get_tasks_db_context = asynccontextmanager(get_tasks_db)


async def get_vector_storage_client() -> AsyncClientAPI:
    client = await chromadb.AsyncHttpClient(host=CHROMADB_HOST, port=int(CHROMADB_PORT))
    return client


async def get_vector_storage_collection(
    client: AsyncClientAPI, collection_name: str
) -> AsyncCollection:
    collection = await client.get_or_create_collection(collection_name)
    return collection
