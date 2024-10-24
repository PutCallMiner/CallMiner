from asyncio import Lock

from redis.asyncio import Redis

from webapp.crud.common import get_tasks_db_context
from webapp.errors import AnalysisInProgressError
from webapp.models.task_status import TaskStatus


async def set_key_value(
    redis_db: Redis,
    key: str,
    value: bytes | str | memoryview | int | float,
    expiration_seconds: int | None = None,
) -> None:
    await redis_db.set(key, value, ex=expiration_seconds)  # Set with expiration


async def get_key_value(redis_db: Redis, key: str) -> str | None:
    value = await redis_db.get(key)
    if value:
        return value.decode("utf-8")
    return None


analysis_lock = Lock()


async def update_task_status(recording_id: str, new_status: TaskStatus):
    async with get_tasks_db_context() as tasks_db:
        async with analysis_lock:
            old_status = await get_key_value(tasks_db, recording_id)
            if new_status == TaskStatus.IN_PROGRESS:
                if old_status == TaskStatus.IN_PROGRESS:
                    raise AnalysisInProgressError(recording_id)
                await set_key_value(tasks_db, recording_id, new_status)
            elif new_status == TaskStatus.FINISHED:
                assert old_status == TaskStatus.IN_PROGRESS
                await set_key_value(tasks_db, recording_id, new_status)
            elif new_status == TaskStatus.FAILED:
                assert old_status == TaskStatus.IN_PROGRESS
                await set_key_value(tasks_db, recording_id, new_status)
