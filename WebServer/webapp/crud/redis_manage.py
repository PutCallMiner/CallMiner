from redis.asyncio import Redis


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
