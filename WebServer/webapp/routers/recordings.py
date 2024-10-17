from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from webapp.configs.globals import AZURE_SAS_TOKEN
from webapp.configs.views import nav_links, templates
from webapp.crud.common import get_rec_db, get_tasks_db
from webapp.crud.recordings import count_recordings, get_recording_by_id, get_recordings
from webapp.crud.redis_manage import get_key_value
from webapp.errors import RecordingNotFoundError
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
    query = {"recording_url": {"$regex": search, "$options": "i"}} if search else None
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
) -> StreamingResponse:
    recording = await get_recording_by_id(recording_db, recording_id)

    if recording is None:
        raise RecordingNotFoundError(recording_id)

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{recording.recording_url}?{AZURE_SAS_TOKEN}")

    response_headers = {
        "Accept-Ranges": resp.headers.get("Accept-Ranges"),
        "Content-Length": resp.headers.get("Content-Length"),
    }

    return StreamingResponse(
        resp.aiter_bytes(),
        headers=response_headers,
        media_type="audio/wav",
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

    if getattr(recording, content, None) is None:
        status = await get_key_value(tasks_db, recording.id)
        if status != TaskStatus.IN_PROGRESS:
            return HTMLResponse(
                content=f"<p>{content.capitalize()} not found, please run the analysis first.</p>",
            )

    return templates.TemplateResponse(
        request=request,
        name="recording_content.html.jinja2",
        context={"recording": recording, "content": content, "delay": delay + 1},
    )
