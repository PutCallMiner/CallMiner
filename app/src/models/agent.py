import typing
import pydantic
import motor.motor_asyncio as motor


class Agent(pydantic.BaseModel):
    id: typing.Optional[str] = pydantic.Field(alias="_id", default=None)
    name: str


async def get_all(db: motor.AsyncIOMotorDatabase) -> list[Agent]:
    records = await db["agents"].find().to_list(None)
    return [Agent.model_validate(record) for record in records]


async def add(db: motor.AsyncIOMotorDatabase, agent: Agent) -> str:
    result = await db["agents"].insert_one(
        agent.model_dump(by_alias=True, exclude_unset=True)
    )
    return result.inserted_id
