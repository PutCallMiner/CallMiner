from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.crud.common import get_db
from webapp.crud.recordings import get_recordings

router = APIRouter(prefix="/api/recordings", tags=["API"])


@router.get("/")
async def table(
        request: Request,
        db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
        skip: int = 0,
        take: int = 20,
) -> JSONResponse:
    recordings = await get_recordings(db, skip=skip, take=take)

    # TODO: fix template according to the new Template Entry model
    return JSONResponse(content=recordings, status_code=200)
