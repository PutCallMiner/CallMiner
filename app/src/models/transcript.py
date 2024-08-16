import datetime
import pydantic
import motor.motor_asyncio as motor


class Transcript(pydantic.BaseModel):
    id: str | None = pydantic.Field(serialization_alias="_id", default=None)
    agent_id: str
    agent: str
    timestamp: datetime.datetime
    duration_secs: int
    score: int
    topic: str
    tags: list[str]


async def get_all(db: motor.AsyncIOMotorDatabase, skip, take) -> list[Transcript]:
    records = await db["transcripts"].find().skip(skip).limit(take).to_list(None)
    return [Transcript.model_validate(record) for record in records]
