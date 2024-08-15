from fastapi import APIRouter
from be.db import persons
from be.schemas import Person

router = APIRouter(prefix="/person")


@router.post("/")
async def add_person(person: Person):
    await persons.add_person(person)
    return {"success": True}


@router.get("/")
async def get_people(fname: str) -> list[Person]:
    return await persons.find_persons_by_fname(fname)
