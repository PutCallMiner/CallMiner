from fastapi import APIRouter
from be.db import persons_db
from be.schemas import Person

router = APIRouter(prefix="/person")


@router.post("/")
async def add_person(person: Person):
    await persons_db.add_person(person)
    return {"success": True}


@router.get("/")
async def get_people(fname: str) -> list[Person]:
    return await persons_db.find_persons_by_fname(fname)
