from typing import Annotated

import bson
from azure.storage.blob.aio import BlobServiceClient
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.crud.common import get_blob_storage_client, get_rec_db
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
    blob_names: list[str], db: Annotated[AsyncIOMotorDatabase, Depends(get_rec_db)]
) -> LoadRecordingsResponse:
    """Create new (not analyzed yet) recordings into the database"""
    recordings = [
        RecordingBase(
            blob_name=blob_name,
            transcript=None,
            summary=None,
            speaker_mapping=None,
            duration=None,
            ner=None,
            conformity=None,
            agent=None,
            tags=[],
        )
        for blob_name in blob_names
    ]
    insert_result = await insert_recordings(db, recordings)
    return LoadRecordingsResponse(num_inserted=len(insert_result.inserted_ids))


@router.delete("/{id}")
async def delete_recording(
    id: str,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_rec_db)],
    blob_service_client: Annotated[BlobServiceClient, Depends(get_blob_storage_client)],
):
    recording = await get_recording_by_id(db, id)
    if not recording:
        raise HTTPException(status_code=404, detail=f"Recording {id} not found!")

    blob_client = blob_service_client.get_blob_client(
        "audio-records", recording.blob_name
    )
    await blob_client.delete_blob()
    await db["recordings"].delete_one({"_id": bson.ObjectId(id)})
    return {"message": f"Recording {id} deleted!"}
