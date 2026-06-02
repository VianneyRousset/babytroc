from unittest.mock import patch

from pydantic import SecretStr

from babytroc.infrastructure.config import RedisConfig
from babytroc.infrastructure.redis import create_redis_client


class TestCreateRedisClient:
    def test_uses_from_url_with_config_url(self):
        cfg = RedisConfig(
            scheme="unix",
            host=None,
            port=None,
            socket_path="/tmp/redis.sock",  # noqa: S108
            db=4,
            username="",
            password=SecretStr(""),
        )
        with patch(
            "babytroc.infrastructure.redis.Redis.from_url",
        ) as mock_from_url:
            create_redis_client(cfg)
        mock_from_url.assert_called_once_with("unix:///tmp/redis.sock?db=4")

    def test_uses_from_url_with_tcp(self):
        cfg = RedisConfig(
            scheme="redis",
            host="h.example.com",
            port=6390,
            socket_path=None,
            db=2,
            username="",
            password=SecretStr("pw"),
        )
        with patch(
            "babytroc.infrastructure.redis.Redis.from_url",
        ) as mock_from_url:
            create_redis_client(cfg)
        mock_from_url.assert_called_once_with("redis://:pw@h.example.com:6390/2")
