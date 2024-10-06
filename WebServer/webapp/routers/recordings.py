from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.configs.views import nav_links, templates
from webapp.crud.common import get_rec_db
from webapp.crud.recordings import count_recordings, get_recordings

router = APIRouter(prefix="/recordings", tags=["Jinja"])


@router.get("/")
async def table(
    request: Request,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_rec_db)],
    skip: int = 0,
    take: int = 20,
) -> HTMLResponse:
    recordings = await get_recordings(db, skip=skip, take=take)
    total = await count_recordings(db)

    return templates.TemplateResponse(
        request=request,
        name="recordings.html.jinja2",
        context={
            "nav_links": nav_links,
            "current": 1,
            "recordings": recordings,
            "total": total,
            "take": take,
            "skip": skip,
        },
    )
