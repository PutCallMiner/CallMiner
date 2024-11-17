from typing import Annotated

from azure.storage.blob.aio import BlobServiceClient
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.configs.views import nav_links, templates
from webapp.crud.common import get_blob_storage_client, get_rec_db
from webapp.models.record import Agent, RecordingBase, Tag

router = APIRouter(prefix="/upload", tags=["Jinja", "Recordings"])


@router.get("")
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="upload.html.jinja2",
        context={"nav_links": nav_links, "current": 2, "page_title": "Upload"},
    )


@router.post("")
async def upload(
    agent_name: Annotated[str, Form()],
    email: Annotated[str, Form()],
    tag: Annotated[str, Form()],
    tag_color: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
    blob_service_client: Annotated[BlobServiceClient, Depends(get_blob_storage_client)],
    recording_db: Annotated[AsyncIOMotorDatabase, Depends(get_rec_db)],
):
    if not file.filename:
        raise ValueError("No file provided")

    recording = RecordingBase(
        blob_name=file.filename,
        transcript=None,
        summary=None,
        speaker_mapping=None,
        duration=None,
        ner=None,
        conformity_results=None,
        agent=Agent(id=2, name=agent_name, email=email),
        tags=[Tag(name=tag, color=tag_color)],
    )

    await recording_db["recordings"].insert_one(recording.model_dump())
    blob_client = blob_service_client.get_blob_client("audio-records", file.filename)
    await blob_client.upload_blob(file.file)

    return RedirectResponse(url="/recordings", status_code=303)
