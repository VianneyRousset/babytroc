from redis.asyncio import Redis

from app.infrastructure.config import RedisConfig


def create_redis_client(config: RedisConfig) -> Redis:
    return Redis(
        host=config.host,
        port=config.port,
        db=config.db,
        password=config.password,
    )
