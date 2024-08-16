import dataclasses
import fastapi
import fastapi.templating


@dataclasses.dataclass
class NavLink:
    url: str
    title: str
    description: str


templates = fastapi.templating.Jinja2Templates(directory="views")
nav_links = [
    NavLink("/", "Dashboard", "View call data and statistics"),
    NavLink("/transcripts", "Transcripts", "View call transcripts"),
]
