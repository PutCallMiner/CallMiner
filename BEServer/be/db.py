from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from be.config import (
    MONGO_DB_NAME,
    MONGO_HOST,
    MONGO_PORT,
    MONGO_ROOT_PASSWORD,
    MONGO_ROOT_USERNAME,
)
from be.schemas import Person


class MongoCollection:
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str):
        self.db = db
        self.collection = self.db[collection_name]


class PersonsCollection(MongoCollection):
    async def add_person(self, person: Person):
        result = await self.collection.insert_one(person.model_dump())
        return result.inserted_id

    async def find_persons_by_fname(self, fname: str) -> list[Person]:
        person_docs = await self.collection.find({"fname": fname}).to_list(None)
        return [Person.model_validate(person_doc) for person_doc in person_docs]


client = AsyncIOMotorClient(
    f"mongodb://{MONGO_ROOT_USERNAME}:{MONGO_ROOT_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}",
    connect=True,
)
mongo_db = client[MONGO_DB_NAME]

persons = PersonsCollection(db=mongo_db, collection_name="persons")
