import fastapi

from .agent import router as agent_router

router = fastapi.APIRouter(prefix="/api", tags=["api"])
router.include_router(agent_router)
