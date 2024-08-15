from fastapi import FastAPI

from be.routers.persons import router as persons_router
from be.celery_app import celery_app


app = FastAPI()

app.include_router(persons_router)


@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

@app.get("/add/{x}/{y}")
async def add_numbers(x: int, y: int, timeout: int = 10):
    # Send the task to Celery
    result = celery_app.send_task("be.tasks.add", args=[x, y])

    try:
        # Wait for the result with a timeout
        task_result = result.get(timeout=timeout)
        return {"task_id": result.id, "status": "Task completed", "result": task_result, "task1": task_result1}
    except TimeoutError:
        return {"task_id": result.id, "status": "Task still running, timeout exceeded"}