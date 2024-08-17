import celery
import os

REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = os.environ["REDIS_PORT"]

app = celery.Celery(
    "callminer",
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
    backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
    include=["tasks"],
)


@app.task
def add(x: int, y: int) -> int:
    return x + y
