from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.crud.common import get_rec_db
from webapp.crud.recordings import (
    get_recording_by_id,
    get_recordings,
    insert_recordings,
)
from webapp.models.record import (
    LoadRecordingsResponse,
    Recording,
    RecordingBase,
    RecordingsResponse,
)

router = APIRouter(prefix="/api/recordings", tags=["API"])


@router.get("/")
async def list_recordings(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_rec_db)],
) -> RecordingsResponse:
    """List all recordings in the database"""
    recordings = await get_recordings(db)
    return RecordingsResponse(recordings=recordings)


@router.get("/{id}")
async def show_recording(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_rec_db)], id: str
) -> Recording:
    """Get the specific recording, looked by its id"""
    recording = await get_recording_by_id(db, id)
    if not recording:
        raise HTTPException(status_code=404, detail=f"Recording {id} not found!")
    return recording


@router.post("/")
async def add_recordings(
    recording_urls: list[str], db: Annotated[AsyncIOMotorDatabase, Depends(get_rec_db)]
) -> LoadRecordingsResponse:
    """Create new (not analyzed yet) recordings into the database"""
    recordings = [
        RecordingBase(
            recording_url=rec_url,
            transcript=None,
            summary=None,
            speaker_mapping=None,
            duration=None,
            ner=None,
            conformity=None,
        )
        for rec_url in recording_urls
    ]
    insert_result = await insert_recordings(db, recordings)
    return LoadRecordingsResponse(num_inserted=len(insert_result.inserted_ids))
