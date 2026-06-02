from unittest.mock import patch

import pytest
from pydantic import SecretStr

from babytroc.infrastructure.config import RedisConfig


class TestRedisConfigFromEnv:
    def test_defaults_when_no_env(self):
        with patch.dict("os.environ", {}, clear=True):
            cfg = RedisConfig.from_env()
        assert cfg.scheme == "redis"
        assert cfg.host == "localhost"
        assert cfg.port == 6379
        assert cfg.db == 0
        assert cfg.username == ""
        assert cfg.password.get_secret_value() == ""
        assert cfg.socket_path is None

    def test_discrete_vars(self):
        env = {
            "REDIS_HOST": "redis.internal",
            "REDIS_PORT": "6390",
            "REDIS_DB": "5",
            "REDIS_PASSWORD": "s3cret",
        }
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env()
        assert cfg.scheme == "redis"
        assert cfg.host == "redis.internal"
        assert cfg.port == 6390
        assert cfg.db == 5
        assert cfg.password.get_secret_value() == "s3cret"
        assert cfg.socket_path is None

    def test_redis_url_tcp(self):
        env = {"REDIS_URL": "redis://r.example.com:6380/3"}
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env()
        assert cfg.scheme == "redis"
        assert cfg.host == "r.example.com"
        assert cfg.port == 6380
        assert cfg.db == 3
        assert cfg.socket_path is None

    def test_redis_url_defaults_port_and_db(self):
        env = {"REDIS_URL": "redis://r.example.com"}
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env()
        assert cfg.port == 6379
        assert cfg.db == 0

    def test_redis_url_tls(self):
        env = {"REDIS_URL": "rediss://r.example.com:6380/0"}
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env()
        assert cfg.scheme == "rediss"
        assert cfg.host == "r.example.com"
        assert cfg.port == 6380
        assert cfg.db == 0

    def test_redis_url_unix_with_db_query(self):
        env = {"REDIS_URL": "unix:///tmp/redis.sock?db=2"}
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env()
        assert cfg.scheme == "unix"
        assert cfg.socket_path == "/tmp/redis.sock"  # noqa: S108
        assert cfg.db == 2
        assert cfg.host is None
        assert cfg.port is None

    def test_redis_url_unix_db_defaults_to_zero(self):
        env = {"REDIS_URL": "unix:///var/run/redis.sock"}
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env()
        assert cfg.socket_path == "/var/run/redis.sock"
        assert cfg.db == 0

    def test_redis_url_user_and_password_decoded(self):
        env = {"REDIS_URL": "redis://alice:p%40ss%2Fword@host:6379/0"}
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env()
        assert cfg.username == "alice"
        assert cfg.password.get_secret_value() == "p@ss/word"

    def test_redis_url_password_only(self):
        env = {"REDIS_URL": "redis://:onlypass@host:6379/0"}
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env()
        assert cfg.username == ""
        assert cfg.password.get_secret_value() == "onlypass"

    def test_db_kwarg_overrides_redis_url_path(self):
        env = {"REDIS_URL": "redis://r.example.com:6380/3"}
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env(db=9)
        assert cfg.db == 9
        assert cfg.url == "redis://r.example.com:6380/9"

    def test_db_kwarg_overrides_unix_url_query(self):
        env = {"REDIS_URL": "unix:///tmp/redis.sock?db=2"}
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env(db=9)
        assert cfg.db == 9
        assert cfg.url == "unix:///tmp/redis.sock?db=9"

    def test_db_kwarg_overrides_discrete_vars(self):
        env = {"REDIS_HOST": "r.example.com", "REDIS_DB": "3"}
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env(db=9)
        assert cfg.db == 9


class TestRedisConfigUrl:
    def test_url_redis(self):
        cfg = RedisConfig(
            scheme="redis",
            host="h.example.com",
            port=6379,
            socket_path=None,
            db=2,
            username="",
            password=SecretStr(""),
        )
        assert cfg.url == "redis://h.example.com:6379/2"

    def test_url_rediss(self):
        cfg = RedisConfig(
            scheme="rediss",
            host="h.example.com",
            port=6380,
            socket_path=None,
            db=0,
            username="",
            password=SecretStr(""),
        )
        assert cfg.url == "rediss://h.example.com:6380/0"

    def test_url_unix(self):
        cfg = RedisConfig(
            scheme="unix",
            host=None,
            port=None,
            socket_path="/tmp/redis.sock",  # noqa: S108
            db=3,
            username="",
            password=SecretStr(""),
        )
        assert cfg.url == "unix:///tmp/redis.sock?db=3"

    def test_url_with_password_only(self):
        cfg = RedisConfig(
            scheme="redis",
            host="h",
            port=6379,
            socket_path=None,
            db=0,
            username="",
            password=SecretStr("p@ss"),
        )
        assert cfg.url == "redis://:p%40ss@h:6379/0"

    def test_url_with_user_and_password(self):
        cfg = RedisConfig(
            scheme="redis",
            host="h",
            port=6379,
            socket_path=None,
            db=0,
            username="alice",
            password=SecretStr("p/w"),
        )
        assert cfg.url == "redis://alice:p%2Fw@h:6379/0"

    def test_url_with_username_only(self):
        cfg = RedisConfig(
            scheme="redis",
            host="h",
            port=6379,
            socket_path=None,
            db=0,
            username="alice",
            password=SecretStr(""),
        )
        assert cfg.url == "redis://alice@h:6379/0"


class TestRedisConfigValidation:
    def test_invalid_scheme_raises(self):
        env = {"REDIS_URL": "http://nope.example.com"}
        with (
            patch.dict("os.environ", env, clear=True),
            pytest.raises(ValueError, match="scheme"),
        ):
            RedisConfig.from_env()

    def test_unix_url_without_path_raises(self):
        env = {"REDIS_URL": "unix://"}
        with (
            patch.dict("os.environ", env, clear=True),
            pytest.raises(ValueError, match="socket"),
        ):
            RedisConfig.from_env()

    def test_redis_url_without_host_raises(self):
        env = {"REDIS_URL": "redis:///0"}
        with (
            patch.dict("os.environ", env, clear=True),
            pytest.raises(ValueError, match="host"),
        ):
            RedisConfig.from_env()

    def test_password_redacted_in_repr(self):
        env = {"REDIS_URL": "redis://:supersecret@h:6379/0"}
        with patch.dict("os.environ", env, clear=True):
            cfg = RedisConfig.from_env()
        assert "supersecret" not in repr(cfg)

    def test_unix_url_with_relative_path_raises(self):
        env = {"REDIS_URL": "unix://relative/path"}
        with patch.dict("os.environ", env, clear=True), pytest.raises(
            ValueError, match="absolute socket path"
        ):
            RedisConfig.from_env()

    def test_unix_url_with_netloc_raises(self):
        env = {"REDIS_URL": "unix://host:6379/var/run/redis.sock"}
        with patch.dict("os.environ", env, clear=True), pytest.raises(
            ValueError, match="absolute socket path"
        ):
            RedisConfig.from_env()

    def test_redis_url_with_non_numeric_db_raises(self):
        env = {"REDIS_URL": "redis://h:6379/abc"}
        with patch.dict("os.environ", env, clear=True), pytest.raises(
            ValueError, match="invalid db value"
        ):
            RedisConfig.from_env()

    def test_unix_url_with_non_numeric_db_raises(self):
        env = {"REDIS_URL": "unix:///tmp/r.sock?db=abc"}
        with patch.dict("os.environ", env, clear=True), pytest.raises(
            ValueError, match="invalid db value"
        ):
            RedisConfig.from_env()
