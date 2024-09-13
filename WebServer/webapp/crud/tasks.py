from redis.asyncio import Redis


async def set_key_value(
    redis_client: Redis,
    key: str,
    value: str | list | set | dict,
    expiration_seconds: int | None = None,
) -> None:
    await redis_client.set(key, value, ex=expiration_seconds)  # Set with expiration


async def get_key_value(
    redis_client: Redis, key: str
) -> str | list | set | dict | None:
    value = await redis_client.get(key)
    if value:
        return value.decode("utf-8")
    return None
