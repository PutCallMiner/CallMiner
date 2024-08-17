import typing
import pydantic

from models.db import db

agents = db["agents"]


class Agent(pydantic.BaseModel):
    id: typing.Optional[str] = pydantic.Field(alias="_id", default=None)
    name: str


async def get_all() -> list[Agent]:
    records = await agents.find().to_list(None)
    return [Agent.model_validate(record) for record in records]


async def add(agent: Agent) -> str:
    result = await agents.insert_one(
        agent.model_dump(by_alias=True, exclude_unset=True)
    )
    return result.inserted_id
