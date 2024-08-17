import datetime
import pydantic

from models.db import db

transcripts = db["transcripts"]


class Transcript(pydantic.BaseModel):
    id: str | None = pydantic.Field(serialization_alias="_id", default=None)
    agent_id: str
    agent: str
    timestamp: datetime.datetime
    duration_secs: int
    score: int
    topic: str
    tags: list[str]


async def get_all(skip, take) -> list[Transcript]:
    records = await transcripts.find().skip(skip).limit(take).to_list(None)
    return [Transcript.model_validate(record) for record in records]
