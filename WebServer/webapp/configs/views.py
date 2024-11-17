import os
from dataclasses import dataclass

from fastapi.templating import Jinja2Templates


@dataclass
class NavLink:
    url: str
    title: str
    description: str


templates = Jinja2Templates(directory=os.path.join("webapp", "views"))
templates.env.add_extension("jinja2.ext.do")
templates.env.add_extension("jinja2.ext.loopcontrols")
nav_links = [
    NavLink("/", "Dashboard", "View call data and statistics"),
    NavLink("/recordings", "Recordings", "View call recordings"),
]
