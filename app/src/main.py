import fastapi
import fastapi.staticfiles
import fastapi.templating

from models.db import db
import routers.api.agent
import routers.dashboard
import routers.transcript
import tasks

app = fastapi.FastAPI()

app.mount("/public", fastapi.staticfiles.StaticFiles(directory="public"), name="public")
app.include_router(routers.dashboard.router)
app.include_router(routers.transcript.router)
app.include_router(routers.api.agent.router)


@app.get("/api/health")
async def health():
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


@app.get("/add/{x}/{y}")
async def add_numbers(x: int, y: int, timeout: int = 10):
    # Send the task to Celery
    result = tasks.add.apply_async(args=[x, y])
    try:
        # Wait for the result with a timeout
        task_result = result.get(timeout=timeout)
        return {"task_id": result.id, "status": "Task completed", "result": task_result}
    except TimeoutError:
        return {"task_id": result.id, "status": "Task still running, timeout exceeded"}
