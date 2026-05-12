import os
from datetime import timedelta
from typing import NamedTuple, Self

import sqlalchemy


def _env(key: str, *, default: str | None = None) -> str:
    """Read env var. In test mode, prefer TEST_ prefixed version."""
    if "PYTEST_CURRENT_TEST" in os.environ:
        test_val = os.environ.get(f"TEST_{key}")
        if test_val is not None:
            return test_val
    if default is not None:
        return os.environ.get(key, default)
    return os.environ[key]


def _env_optional(key: str) -> str | None:
    """Read optional env var. In test mode, prefer TEST_ prefixed version."""
    if "PYTEST_CURRENT_TEST" in os.environ:
        test_val = os.environ.get(f"TEST_{key}")
        if test_val is not None:
            return test_val
    return os.environ.get(key)


class DatabaseConfig(NamedTuple):
    url: sqlalchemy.URL

    @classmethod
    def from_env(
        cls,
        url: sqlalchemy.URL | None = None,
    ) -> Self:
        if url is None:
            user = _env("POSTGRES_USER")
            password = _env("POSTGRES_PASSWORD")
            host = _env("POSTGRES_HOST")
            port = int(_env("POSTGRES_PORT"))
            database = _env("POSTGRES_DATABASE")

            url = sqlalchemy.URL.create(
                "postgresql+asyncpg",
                username=user,
                password=password,
                host=host,
                port=port,
                database=database,
            )
        return cls(url=url)


class RedisConfig(NamedTuple):
    host: str
    port: int
    db: int
    password: str | None

    @classmethod
    def from_env(
        cls,
        host: str | None = None,
        port: int | None = None,
        db: int | None = None,
        password: str | None = None,
    ) -> Self:
        if host is None:
            host = _env("REDIS_HOST", default="localhost")
        if port is None:
            port = int(_env("REDIS_PORT", default="6379"))
        if db is None:
            db = int(_env("REDIS_DB", default="0"))
        if password is None:
            password = _env_optional("REDIS_PASSWORD")

        return cls(host=host, port=port, db=db, password=password)

    @property
    def url(self) -> str:
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


class PubsubConfig(NamedTuple):
    url: str

    @classmethod
    def from_env(cls, url: str | None = None) -> Self:
        if url is None:
            redis_config = RedisConfig.from_env()
            url = redis_config.url

        return cls(url=url)


class EmailConfig(NamedTuple):
    server: str
    port: int
    username: str
    password: str
    from_email: str
    from_name: str

    @classmethod
    def from_env(
        cls,
        server: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
        from_email: str | None = None,
        from_name: str | None = None,
    ) -> Self:
        if server is None:
            server = _env("EMAIL_SERVER")
        if port is None:
            port = int(_env("EMAIL_PORT"))
        if username is None:
            username = _env("EMAIL_USERNAME")
        if password is None:
            password = _env("EMAIL_PASSWORD")
        if from_email is None:
            from_email = _env("EMAIL_FROM_EMAIL")
        if from_name is None:
            from_name = _env("EMAIL_FROM_NAME")

        return cls(
            server=server,
            port=port,
            username=username,
            password=password,
            from_email=from_email,
            from_name=from_name,
        )


class S3Config(NamedTuple):
    endpoint_url: str
    access_key: str
    secret_key: str
    bucket: str
    public_url: str

    @classmethod
    def from_env(
        cls,
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        bucket: str | None = None,
        public_url: str | None = None,
    ) -> Self:
        if endpoint_url is None:
            endpoint_url = _env("S3_ENDPOINT_URL")
        if access_key is None:
            access_key = _env("S3_ACCESS_KEY")
        if secret_key is None:
            secret_key = _env("S3_SECRET_KEY")
        if bucket is None:
            bucket = _env("S3_BUCKET")
        if public_url is None:
            public_url = _env("S3_PUBLIC_URL")

        return cls(
            endpoint_url=endpoint_url,
            access_key=access_key,
            secret_key=secret_key,
            bucket=bucket,
            public_url=public_url,
        )


class AuthConfig(NamedTuple):
    algorithm: str
    secret_key: str
    refresh_token_duration: timedelta
    access_token_duration: timedelta
    account_password_reset_authorization_duration: timedelta

    @classmethod
    def from_env(
        cls,
        algorithm: str | None = None,
        secret_key: str | None = None,
        refresh_token_duration: timedelta | None = None,
        access_token_duration: timedelta | None = None,
        account_password_reset_authorization_duration: timedelta | None = None,
    ) -> Self:
        if algorithm is None:
            algorithm = _env("JWT_ALGORITHM")

        if secret_key is None:
            secret_key = _env("JWT_SECRET_KEY")

        if refresh_token_duration is None:
            refresh_token_duration = timedelta(
                days=int(_env("JWT_REFRESH_TOKEN_DURATION_DAYS")),
            )

        if access_token_duration is None:
            access_token_duration = timedelta(
                minutes=int(_env("JWT_ACCESS_TOKEN_DURATION_MINUTES")),
            )

        if account_password_reset_authorization_duration is None:
            account_password_reset_authorization_duration = timedelta(
                minutes=int(
                    _env(
                        "ACCOUNT_PASSWORD_RESET_AUTHORIZATION_DURATION_MINUTES",
                    ),
                ),
            )
        return cls(
            algorithm=algorithm,
            secret_key=secret_key,
            refresh_token_duration=refresh_token_duration,
            access_token_duration=access_token_duration,
            account_password_reset_authorization_duration=account_password_reset_authorization_duration,
        )


class RateLimitConfig(NamedTuple):
    anon: int
    auth: int
    window: timedelta

    @classmethod
    def from_env(
        cls,
        *,
        env_prefix: str,
        default_anon: int,
        default_auth: int,
        default_window_seconds: int,
    ) -> Self:
        anon = int(_env(f"{env_prefix}_RATE_LIMIT_ANON", default=str(default_anon)))
        auth = int(_env(f"{env_prefix}_RATE_LIMIT_AUTH", default=str(default_auth)))
        window = timedelta(
            seconds=int(
                _env(
                    f"{env_prefix}_RATE_LIMIT_WINDOW_SECONDS",
                    default=str(default_window_seconds),
                ),
            ),
        )
        return cls(anon=anon, auth=auth, window=window)


class ContactConfig(NamedTuple):
    email: str
    rate_limit: RateLimitConfig

    @classmethod
    def from_env(
        cls,
        email: str | None = None,
        rate_limit: RateLimitConfig | None = None,
    ) -> Self:
        if email is None:
            email = _env("CONTACT_EMAIL")
        if rate_limit is None:
            rate_limit = RateLimitConfig.from_env(
                env_prefix="CONTACT",
                default_anon=5,
                default_auth=10,
                default_window_seconds=3600,
            )
        return cls(email=email, rate_limit=rate_limit)


class CapConfig(NamedTuple):
    api_url: str
    site_key: str
    secret_key: str

    @classmethod
    def from_env(
        cls,
        api_url: str | None = None,
        site_key: str | None = None,
        secret_key: str | None = None,
    ) -> Self:
        if api_url is None:
            api_url = _env("CAP_API_URL")
        if site_key is None:
            site_key = _env("CAP_SITE_KEY")
        if secret_key is None:
            secret_key = _env("CAP_SECRET_KEY")
        return cls(api_url=api_url, site_key=site_key, secret_key=secret_key)


class Config(NamedTuple):
    host_name: str
    app_name: str
    root_path: str
    test: bool
    delay: float
    database: DatabaseConfig
    pubsub: PubsubConfig
    email: EmailConfig
    s3: S3Config
    redis: RedisConfig
    auth: AuthConfig
    contact: ContactConfig
    cap: CapConfig
    signup: RateLimitConfig
    password_reset: RateLimitConfig
    item_create: RateLimitConfig
    image_upload: RateLimitConfig

    @classmethod
    def from_env(  # noqa: C901
        cls,
        *,
        host_name: str | None = None,
        app_name: str | None = None,
        root_path: str | None = None,
        test: bool | None = None,
        delay: float | None = None,
        database: DatabaseConfig | None = None,
        pubsub: PubsubConfig | None = None,
        email: EmailConfig | None = None,
        s3: S3Config | None = None,
        redis: RedisConfig | None = None,
        auth: AuthConfig | None = None,
        contact: ContactConfig | None = None,
        cap: CapConfig | None = None,
        signup: RateLimitConfig | None = None,
        password_reset: RateLimitConfig | None = None,
        item_create: RateLimitConfig | None = None,
        image_upload: RateLimitConfig | None = None,
    ) -> Self:
        if host_name is None:
            host_name = _env("HOST_NAME")

        if app_name is None:
            app_name = _env("APP_NAME")

        if root_path is None:
            root_path = _env("ROOT_PATH", default="")

        if test is None:
            test = "PYTEST_CURRENT_TEST" in os.environ

        if delay is None:
            delay = float(_env("DELAY", default="0"))

        if database is None:
            database = DatabaseConfig.from_env()

        if redis is None:
            redis = RedisConfig.from_env()

        if pubsub is None:
            pubsub = PubsubConfig.from_env(url=redis.url)

        if email is None:
            email = EmailConfig.from_env()

        if s3 is None:
            s3 = S3Config.from_env()

        if auth is None:
            auth = AuthConfig.from_env()

        if contact is None:
            contact = ContactConfig.from_env()

        if cap is None:
            cap = CapConfig.from_env()

        if signup is None:
            signup = RateLimitConfig.from_env(
                env_prefix="SIGNUP",
                default_anon=3, default_auth=3, default_window_seconds=3600,
            )
        if password_reset is None:
            password_reset = RateLimitConfig.from_env(
                env_prefix="PASSWORD_RESET",
                default_anon=3, default_auth=3, default_window_seconds=3600,
            )
        if item_create is None:
            item_create = RateLimitConfig.from_env(
                env_prefix="ITEM_CREATE",
                default_anon=30, default_auth=30, default_window_seconds=3600,
            )
        if image_upload is None:
            image_upload = RateLimitConfig.from_env(
                env_prefix="IMAGE_UPLOAD",
                default_anon=60, default_auth=60, default_window_seconds=3600,
            )

        return cls(
            host_name=host_name,
            app_name=app_name,
            root_path=root_path,
            test=test,
            delay=delay,
            database=database,
            pubsub=pubsub,
            email=email,
            s3=s3,
            redis=redis,
            auth=auth,
            contact=contact,
            cap=cap,
            signup=signup,
            password_reset=password_reset,
            item_create=item_create,
            image_upload=image_upload,
        )
