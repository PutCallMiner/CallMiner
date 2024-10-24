import asyncio
import time

from asgiref.sync import sync_to_async
from celery import Task  # type: ignore[import]

from webapp.errors import TaskTimeoutError


# Converts a Celery tasks to an async function
def task_to_async(timeout: float | None = None):
    def timeout_wrapper(task: Task):
        async def wrapper(*args, **kwargs):
            delay = 0.1
            async_result = await sync_to_async(task.apply_async)(*args, **kwargs)
            start_time = time.time()
            while not async_result.ready():
                if (timeout is not None) and (time.time() - start_time) > timeout:
                    raise TaskTimeoutError(task.name, async_result.id)
                await asyncio.sleep(delay)
                delay = min(delay * 1.5, 2)  # exponential backoff, max 2 seconds
            return async_result.get()

        return wrapper

    return timeout_wrapper
