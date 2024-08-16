import fastapi

from . import templates, nav_links

router = fastapi.APIRouter()


@router.get("/", response_class=fastapi.responses.HTMLResponse)
def root(request: fastapi.Request):
    return templates.TemplateResponse(
        request=request,
        name="layout.html.jinja2",
        context={"nav_links": nav_links, "current": 0, "page_title": "Dashboard"},
    )
