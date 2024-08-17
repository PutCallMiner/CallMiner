import fastapi

import models.agent

router = fastapi.APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("/")
async def index() -> list[models.agent.Agent]:
    return await models.agent.get_all()


@router.post(
    "/", status_code=fastapi.status.HTTP_201_CREATED, response_model_by_alias=False
)
async def create(
    agent: models.agent.Agent,
) -> str:
    return await models.agent.add(agent)
