import celery
import os

REDIS_PORT = os.environ["REDIS_PORT"]

app = celery.Celery(
    "callminer",
    broker=f"redis://redis:{REDIS_PORT}/0",
    backend=f"redis://redis:{REDIS_PORT}/0",
)
