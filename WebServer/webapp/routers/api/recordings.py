from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.crud.common import get_db
from webapp.crud.recordings import get_recordings, insert_recordings
from webapp.models.record import LoadRecordingsResponse, Recording

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


@router.post("/")
async def load_recordings(
    recording_urls: list[str], db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]
):
    recordings = [
        Recording(recording_url=rec_url, transcript=None, summary=None)
        for rec_url in recording_urls
    ]
    insert_result = await insert_recordings(db, recordings)
    return LoadRecordingsResponse(num_inserted=len(insert_result.inserted_ids))
