from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.configs.views import nav_links, templates
from webapp.crud.common import get_rec_db
from webapp.crud.recordings import get_recordings

router = APIRouter(prefix="/recordings", tags=["Jinja"])


@router.get("/")
async def table(
    request: Request,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_rec_db)],
    skip: int = 0,
    take: int = 20,
) -> HTMLResponse:
    recordings = await get_recordings(db, skip=skip, take=take)

    # TODO: fix template according to the new Recording model
    return templates.TemplateResponse(
        request=request,
        name="transcript.html.jinja2",
        context={
            "nav_links": nav_links,
            "current": 1,
            "page_title": "Transcripts",
            "transcripts": recordings,
            "total": len(recordings),
            "take": take,
            "skip": skip,
        },
    )
