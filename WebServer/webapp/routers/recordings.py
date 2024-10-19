from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from webapp.configs.views import nav_links, templates
from webapp.crud.common import get_rec_db, get_tasks_db
from webapp.crud.recordings import count_recordings, get_recording_by_id, get_recordings
from webapp.crud.redis_manage import get_key_value
from webapp.errors import RecordingNotFoundError
from webapp.models.record import Recording
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
        name=(
            "recordings.html.jinja2"
            if not request.headers.get("hx-request")
            else "recordings_table.html.jinja2"
        ),
        context={
            "nav_links": nav_links,
            "current": 1,
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


async def get_content(
    request: Request,
    recording: Recording,
    content: str,
    not_in_db: bool,
    delay: int,
    tasks_db: Redis,
) -> HTMLResponse:
    if not_in_db:
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

    return await get_content(
        request,
        recording,
        content,
        getattr(recording, content, None) is None,
        delay,
        tasks_db,
    )
