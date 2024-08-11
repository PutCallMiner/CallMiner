from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from be.models import PersonDB
from be.schemas import Person


async def connect():
    client = AsyncIOMotorClient("mongodb://root:example@localhost:27017")
    await init_beanie(database=client["test"], document_models=[PersonDB])

def _person_to_db(p: Person) -> PersonDB:
    return PersonDB(fname=p.fname, lname=p.lname)

async def add_person(person: Person):
    p = _person_to_db(person)
    await p.insert()
    return True

async def find_persons_by_fname(fname: str):
    res = await PersonDB.find_many(PersonDB.fname == fname).to_list()
    return res