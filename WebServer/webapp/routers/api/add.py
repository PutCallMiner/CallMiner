from fastapi import APIRouter
from fastapi.responses import JSONResponse

from webapp.tasks.add import add

router = APIRouter(prefix="/api", tags=["API"])


@router.get("/add/{x}/{y}")
async def add_numbers(x: int, y: int, timeout: int = 10):
    # Send the task to Celery
    result = add.apply_async(args=[x, y])
    try:
        # Wait for the result with a timeout
        task_result = result.get(timeout=timeout)
        return JSONResponse(
            content={
                "task_id": result.id,
                "status": "Task completed",
                "result": task_result,
            },
            status_code=200,
        )
    except TimeoutError:
        return JSONResponse(
            content={
                "task_id": result.id,
                "status": "Task still running, timeout exceeded",
            },
            status_code=500,
        )
