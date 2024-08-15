import fastapi
import routers
import models.transcript

router = fastapi.APIRouter(prefix="/transcripts", tags=["transcripts"])


@router.get("/")
def root(request: fastapi.Request):
    transcripts = models.transcript.get_all()

    return routers.templates.TemplateResponse(
        request=request,
        name="transcript.html.jinja2",
        context={
            "nav_links": routers.nav_links,
            "current": 1,
            "transcripts": transcripts,
            "total": len(transcripts),
            "take": 20,
            "skip": 0,
        },
    )
