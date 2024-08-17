import fastapi

import models.transcript
from . import templates, nav_links

router = fastapi.APIRouter(prefix="/transcripts", tags=["transcripts"])


@router.get("/", response_class=fastapi.responses.HTMLResponse)
async def table(
    request: fastapi.Request,
    skip: int = 0,
    take: int = 20,
):
    transcripts = await models.transcript.get_all(skip=skip, take=take)

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
