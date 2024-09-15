from redis.asyncio import Redis


async def set_key_value(
    redis_db: Redis,
    key: str,
    value: str | list | set | dict,
    expiration_seconds: int | None = None,
) -> None:
    await redis_db.set(key, value, ex=expiration_seconds)  # Set with expiration


async def get_key_value(redis_db: Redis, key: str) -> str | list | set | dict | None:
    value = await redis_db.get(key)
    if value:
        return value.decode("utf-8")
    return None
