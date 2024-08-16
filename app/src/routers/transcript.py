import fastapi
import typing
import motor.motor_asyncio as motor

import models.db
import models.transcript
from . import templates, nav_links

router = fastapi.APIRouter(prefix="/transcripts", tags=["transcripts"])


@router.get("/", response_class=fastapi.responses.HTMLResponse)
async def table(
    request: fastapi.Request,
    db: typing.Annotated[motor.AsyncIOMotorDatabase, fastapi.Depends(models.db.get_db)],
    skip: int = 0,
    take: int = 20,
):
    transcripts = await models.transcript.get_all(db, skip=skip, take=take)

    return templates.TemplateResponse(
        request=request,
        name="transcript.html.jinja2",
        context={
            "nav_links": nav_links,
            "current": 1,
            "page_title": "Transcripts",
            "transcripts": transcripts,
            "total": len(transcripts),
            "take": take,
            "skip": skip,
        },
    )
