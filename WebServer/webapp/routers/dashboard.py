from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from webapp.configs.views import nav_links, templates

router = APIRouter(tags=["Jinja"])


@router.get("/")
def root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="layout.html.jinja2",
        context={"nav_links": nav_links, "current": 0, "page_title": "Dashboard"},
    )
