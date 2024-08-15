from motor.motor_asyncio import AsyncIOMotorClient

from be.config import MONGO_DB_NAME, MONGO_ROOT_PASSWORD, MONGO_ROOT_USERNAME
from be.schemas import Person


class MongoCollection:
    def __init__(
        self, username: str, password: str, db_name: str, collection_name: str
    ):
        self.client = AsyncIOMotorClient(
            f"mongodb://{username}:{password}@localhost:27017", connect=True
        )
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]


class PersonsCollection(MongoCollection):
    async def add_person(self, person: Person):
        result = await self.collection.insert_one(person.model_dump())
        return result.inserted_id

    async def find_persons_by_fname(self, fname: str) -> list[Person]:
        person_docs = await self.collection.find({"fname": fname}).to_list(None)
        return [Person.model_validate(person_doc) for person_doc in person_docs]


persons_db = PersonsCollection(
    username=MONGO_ROOT_USERNAME,
    password=MONGO_ROOT_PASSWORD,
    db_name=MONGO_DB_NAME,
    collection_name="persons",
)
