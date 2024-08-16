import fastapi
import typing
import motor.motor_asyncio as motor

import models.db
import models.agent

router = fastapi.APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("/")
async def index(
    db: typing.Annotated[motor.AsyncIOMotorDatabase, fastapi.Depends(models.db.get_db)],
) -> list[models.agent.Agent]:
    return await models.agent.get_all(db)


@router.post(
    "/", status_code=fastapi.status.HTTP_201_CREATED, response_model_by_alias=False
)
async def create(
    agent: models.agent.Agent,
    db: typing.Annotated[motor.AsyncIOMotorDatabase, fastapi.Depends(models.db.get_db)],
) -> str:
    return await models.agent.add(db, agent)
