import fastapi
import routers

router = fastapi.APIRouter()


@router.get("/")
def root(request: fastapi.Request):
    return routers.templates.TemplateResponse(
        request=request,
        name="layout.html.jinja2",
        context={"nav_links": routers.nav_links, "current": 0},
    )
