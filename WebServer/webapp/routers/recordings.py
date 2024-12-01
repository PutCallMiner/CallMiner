from typing import Annotated, Optional

from azure.core.credentials import AzureSasCredential
from azure.storage.blob.aio import BlobServiceClient
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from webapp.configs.globals import AZURE_BLOB_STORAGE_URL, AZURE_SAS_TOKEN
from webapp.configs.views import nav_links, templates
from webapp.crud.common import get_blob_storage_client, get_rec_db, get_tasks_db
from webapp.crud.recordings import count_recordings, get_recording_by_id, get_recordings
from webapp.crud.redis_manage import get_key_value
from webapp.errors import RecordingNotFoundError
from webapp.models.record import Agent, RecordingBase
from webapp.models.task_status import TaskStatus

router = APIRouter(prefix="/recordings", tags=["Jinja", "Recordings"])


@router.get("")
async def table(
    request: Request,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_rec_db)],
    search: str = "",
    skip: int = 0,
    take: int = 20,
) -> HTMLResponse:
    query = {"blob_name": {"$regex": search, "$options": "i"}} if search else None
    total = await count_recordings(db, query=query)
    recordings = await get_recordings(db, query=query, skip=skip, take=take)

    return templates.TemplateResponse(
        request=request,
        name="recordings.html.jinja2",
        context={
            "nav_links": nav_links,
            "current": 1,
            "partial": request.headers.get("hx-request"),
            "recordings": recordings,
            "total": total,
            "take": take,
            "skip": skip,
            "search": search,
        },
    )


@router.post("/upload")
async def upload(
    agent_name: Annotated[str, Form()],
    agent_email: Annotated[str, Form()],
    tags: Annotated[str, Form()],
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
        conformity=None,
        agent=Agent(id=2, name=agent_name, email=agent_email),
        tags=[tag.strip() for tag in tags.split(",")],
    )

    await recording_db["recordings"].insert_one(recording.model_dump())
    blob_client = blob_service_client.get_blob_client("audio-records", file.filename)
    await blob_client.upload_blob(file.file, overwrite=True)

    return RedirectResponse(url="/recordings", status_code=303)


@router.get("/{recording_id}")
async def detail(
    request: Request,
    recording_id: str,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_rec_db)],
    tab: int = 0,
) -> HTMLResponse:
    recording = await get_recording_by_id(db, recording_id)

    if recording is None:
        raise RecordingNotFoundError(recording_id)

    return templates.TemplateResponse(
        request=request,
        name=("recording.html.jinja2"),
        context={
            "nav_links": nav_links,
            "current": 1,
            "recording": recording,
            "partial": request.headers.get("hx-request"),
            "tab": tab,
            "delay": 0,
        },
    )


@router.get("/{recording_id}/audio")
async def audio(
    recording_id: str,
    recording_db: Annotated[AsyncIOMotorDatabase, Depends(get_rec_db)],
    range: Optional[str] = None,
) -> StreamingResponse:
    sas = AzureSasCredential(AZURE_SAS_TOKEN)
    blob_storage = BlobServiceClient(AZURE_BLOB_STORAGE_URL, sas)
    recording = await get_recording_by_id(recording_db, recording_id)

    if recording is None:
        raise RecordingNotFoundError(recording_id)

    blob_client = blob_storage.get_blob_client("audio-records", recording.blob_name)
    properties = await blob_client.get_blob_properties()
    blob_size = properties.size

    if range is not None:
        bytes_unit, bytes_range = range.strip().split("=")
        if bytes_unit != "bytes":
            raise HTTPException(status_code=416, detail="Invalid unit in Range header")

        ranges = bytes_range.split("-")
        if len(ranges) != 2:
            raise HTTPException(status_code=416, detail="Invalid Range header format")

        start = int(ranges[0])
        if ranges[1]:
            end = int(ranges[1])
        else:
            end = blob_size - 1

        if start > end or end >= blob_size:
            raise HTTPException(
                status_code=416, detail="Requested Range Not Satisfiable"
            )
        content_length = end - start + 1
        status_code = 206
    else:
        start = 0
        end = blob_size - 1
        content_length = blob_size
        status_code = 200

    response_headers = {
        "Content-Type": "audio/wav",
        "Accept-Ranges": "bytes",
        "Content-Length": str(content_length),
        "Content-Range": f"bytes {start}-{end}/{blob_size}",
    }

    async def iterfile():
        stream = await blob_client.download_blob(offset=start, length=content_length)
        async for chunk in stream.chunks():
            yield chunk
        await blob_storage.close()

    return StreamingResponse(
        iterfile(),
        status_code=status_code,
        headers=response_headers,
    )


@router.get("/{recording_id}/{content}")
async def content(
    request: Request,
    recording_id: str,
    recording_db: Annotated[AsyncIOMotorDatabase, Depends(get_rec_db)],
    tasks_db: Annotated[Redis, Depends(get_tasks_db)],
    content: str = "transcript",
    delay: int = 0,
) -> HTMLResponse:
    recording = await get_recording_by_id(recording_db, recording_id)

    if recording is None:
        raise RecordingNotFoundError(recording_id)

    attr = content.split("-")[0]
    attr_name = attr.upper() if attr in ["ner"] else attr.capitalize()

    if getattr(recording, attr, None) is None:
        status = await get_key_value(tasks_db, recording.id)
        if status != TaskStatus.IN_PROGRESS:
            return HTMLResponse(
                content=f"<p>{attr_name} not found, please run the analysis first.</p>",
            )

    return templates.TemplateResponse(
        request=request,
        name="recording_content.html.jinja2",
        context={
            "recording": recording,
            "content": content,
            "delay": delay + 1,
        },
    )
