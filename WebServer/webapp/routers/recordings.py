from typing import Annotated, Optional

from azure.core.credentials import AzureSasCredential
from azure.storage.blob.aio import BlobServiceClient
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from webapp.configs.analysis import EUROTAX_PARAMS
from webapp.configs.globals import AZURE_BLOB_STORAGE_URL, AZURE_SAS_TOKEN
from webapp.configs.intents import PREDEFINED_INTENTS
from webapp.configs.views import nav_links, templates
from webapp.crud.common import get_blob_storage_client, get_rec_db, get_tasks_db
from webapp.crud.recordings import count_recordings, get_recording_by_id, get_recordings
from webapp.crud.redis_manage import get_key_value
from webapp.errors import RecordingNotFoundError
from webapp.models.record import Agent, RecordingBase
from webapp.routers.api.analysis import run_recording_analysis
from webapp.task_exec.common import TaskType

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


@router.post("")
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
            "loading": False,
            "intents": PREDEFINED_INTENTS,
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


@router.get("/{recording_id}/status")
async def status(
    request: Request,
    recording_id: str,
    tasks_db: Annotated[Redis, Depends(get_tasks_db)],
    recording_db: Annotated[AsyncIOMotorDatabase, Depends(get_rec_db)],
    previous: str = "",
) -> HTMLResponse:
    task_status = await get_key_value(tasks_db, recording_id)
    # task_status = "in_progress"

    if previous == "in_progress" and task_status == "in_progress":
        return templates.TemplateResponse(
            request=request,
            name="analysis.html.jinja2",
            context={
                "request": request,
                "recording_id": recording_id,
                "status": task_status,
            },
        )

    recording = await get_recording_by_id(recording_db, recording_id)

    if recording is None:
        raise RecordingNotFoundError(recording_id)

    return templates.TemplateResponse(
        request=request,
        name="analysis.html.jinja2",
        context={
            "recording": recording,
            "tab": 0,
            "partial": True,
            "reload": True,
            "loading": task_status == "in_progress",
            "intents": PREDEFINED_INTENTS,
            "status": (
                "" if task_status is None or task_status == previous else task_status
            ),
            "recording_id": recording_id,
        },
    )


@router.post("/{recording_id}/analyze")
async def analyze(
    recording_id: str,
    background_tasks: BackgroundTasks,
    transcript: Annotated[str, Form()] = "",
    summary: Annotated[str, Form()] = "",
    ner: Annotated[str, Form()] = "",
    conformity: Annotated[str, Form()] = "",
    force_rerun: Annotated[bool, Form()] = False,
) -> RedirectResponse:
    required_tasks = []
    if force_rerun:
        required_tasks.append(TaskType.ASR)
        required_tasks.append(TaskType.SPEAKER_CLASS)

        if summary:
            required_tasks.append(TaskType.SUMMARY)
        if ner:
            required_tasks.append(TaskType.NER)
        if conformity:
            required_tasks.append(TaskType.CONFORMITY)
    else:
        required_tasks = list(TaskType.__members__.values())

    await run_recording_analysis(
        recording_id=recording_id,
        required_tasks=required_tasks,
        force_rerun="selected" if force_rerun else "none",
        background_tasks=background_tasks,
        analyze_params=EUROTAX_PARAMS,
    )

    return RedirectResponse(url=f"/recordings/{recording_id}/status", status_code=303)
