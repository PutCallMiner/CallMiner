import datetime
import pydantic


class Transcript(pydantic.BaseModel):
    id: int
    agent_id: int
    agent: str
    timestamp: datetime.datetime
    duration_secs: int
    score: int
    topic: str
    tags: list[str]


def get_all() -> list[Transcript]:
    return []
