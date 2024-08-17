import motor.motor_asyncio as motor
import os

MONGO_HOST = os.environ["MONGO_HOST"]
MONGO_ROOT_USERNAME = os.environ["MONGO_ROOT_USERNAME"]
MONGO_ROOT_PASSWORD = os.environ["MONGO_ROOT_PASSWORD"]
MONGO_DB_NAME = os.environ["MONGO_DB_NAME"]
MONGO_PORT = os.environ["MONGO_PORT"]


async def get_db():
    client = motor.AsyncIOMotorClient(
        f"mongodb://{MONGO_ROOT_USERNAME}:{MONGO_ROOT_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}",
        connect=True,
    )
    db = client[MONGO_DB_NAME]
    try:
        yield db
    finally:
        db.client.close()
