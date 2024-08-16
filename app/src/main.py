import fastapi
import fastapi.staticfiles
import fastapi.templating
import motor.motor_asyncio as motor
import typing

import models.db
import routers.api.agent
import routers.dashboard
import routers.transcript
import tasks

app = fastapi.FastAPI()

app.mount("/public", fastapi.staticfiles.StaticFiles(directory="public"), name="public")
app.include_router(routers.dashboard.router)
app.include_router(routers.transcript.router)
app.include_router(routers.api.agent.router)


@app.get("/api/health", response_class=fastapi.responses.Response)
async def health(
    db: typing.Annotated[motor.AsyncIOMotorDatabase, fastapi.Depends(models.db.get_db)]
):
    try:
        result = await db.client.admin.command("ping")
    except:
        result = None

    if result is None or result.get("ok") != 1:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database ping failed",
        )

    try:
        result = tasks.app.control.inspect().ping()
    except:
        result = None

    if result is None or not all([v.get("ok") == "pong" for v in result.values()]):
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Celery ping failed",
        )

    return fastapi.Response(status_code=fastapi.status.HTTP_200_OK)
