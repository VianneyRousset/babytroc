from redis.asyncio import Redis

from babytroc.infrastructure.config import RedisConfig


def create_redis_client(config: RedisConfig) -> Redis:
    return Redis.from_url(config.url)
