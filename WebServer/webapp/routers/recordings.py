from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from webapp.configs.views import nav_links, templates
from webapp.crud.common import get_rec_db
from webapp.crud.recordings import count_recordings, get_recordings

router = APIRouter(prefix="/recordings", tags=["Jinja", "Recordings"])


@router.get("")
async def table(
    request: Request,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_rec_db)],
    search: str = "",
    skip: int = 0,
    take: int = 20,
) -> HTMLResponse:
    print("search:", search)
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
