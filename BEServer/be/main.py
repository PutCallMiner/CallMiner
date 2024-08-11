from contextlib import asynccontextmanager
from fastapi import FastAPI

from be import db
from be.db import Person, connect

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

@app.post("/person")
async def add_person(person: Person):
    await db.add_person(person)
    return {"success": True}

@app.get("/person")
async def get_people(fname: str) -> list[Person]:
    return await db.find_persons_by_fname(fname)