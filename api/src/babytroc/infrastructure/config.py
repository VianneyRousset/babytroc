import os
from collections.abc import Mapping
from datetime import timedelta
from typing import Literal, NamedTuple, Self
from urllib.parse import parse_qs, quote, unquote, urlparse

import sqlalchemy
from pydantic import SecretStr


class MissingEnvironmentVariableError(Exception):
    def __init__(self, key: str):
        super().__init__(f"Missing environment variable: {key}")


class EnvironmentVariablesReader(Mapping):
    def __init__(self, *, test: bool | None = None):
        self.test = "PYTEST_CURRENT_TEST" in os.environ if test is None else test

    def __getitem__(self, key: str) -> str:
        """Read env var. In test mode, prefer TEST_ prefixed version."""
        if self.test and f"TEST_{key}" in os.environ:
            key = f"TEST_{key}"

        try:
            return os.environ[key]
        except KeyError as error:
            raise MissingEnvironmentVariableError(key) from error

    def get(self, key: str, default=None):
        """Read optional env var. In test mode, prefer TEST_ prefixed version."""
        if self.test and f"TEST_{key}" in os.environ:
            key = f"TEST_{key}"
        return os.environ.get(key, default)

    def __iter__(self):
        return iter(os.environ)

    def __len__(self):
        return len(os.environ)


class DatabaseConfig(NamedTuple):
    user: str
    password: SecretStr
    host: str
    port: int
    database: str

    @classmethod
    def from_env(
        cls,
        *,
        user: str | None = None,
        password: SecretStr | str | None = None,
        host: str | None = None,
        port: int | None = None,
        database: str | None = None,
        url: sqlalchemy.URL | None = None,
        test: bool | None = None,
    ) -> Self:
        env = EnvironmentVariablesReader(test=test)

        if url is not None:
            user = url.username
            password = url.password
            host = url.host
            port = url.port
            database = url.database

        if user is None:
            user = env["POSTGRES_USER"]
        if password is None:
            password = env.get("POSTGRES_PASSWORD", "")
        if host is None:
            host = env.get("POSTGRES_HOST", "localhost")
        if port is None:
            port = int(env.get("POSTGRES_PORT", 5432))
        if database is None:
            database = env.get("POSTGRES_DATABASE", "babytroc")

        if isinstance(password, str):
            password = SecretStr(password)

        return cls(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database,
        )

    @property
    def url(self) -> sqlalchemy.URL:
        return sqlalchemy.URL.create(
            drivername="postgresql+asyncpg",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            database=self.database,
        )


class RedisConfig(NamedTuple):
    scheme: Literal["redis", "rediss", "unix"]
    host: str | None
    port: int | None
    socket_path: str | None
    db: int
    username: str
    password: SecretStr

    @classmethod
    def from_env(
        cls,
        *,
        url: str | None = None,
        scheme: Literal["redis", "rediss", "unix"] | None = None,
        host: str | None = None,
        port: int | None = None,
        socket_path: str | None = None,
        db: int | None = None,
        username: str | None = None,
        password: SecretStr | str | None = None,
        test: bool | None = None,
    ) -> Self:
        env = EnvironmentVariablesReader(test=test)

        # 1. Source fields from explicit url arg, REDIS_URL, or discrete vars.
        if url is None:
            url = env.get("REDIS_URL")

        parsed_scheme: Literal["redis", "rediss", "unix"]
        parsed_host: str | None
        parsed_port: int | None
        parsed_socket_path: str | None
        parsed_db: int
        parsed_username: str
        parsed_password: str

        if url:
            (
                parsed_scheme,
                parsed_host,
                parsed_port,
                parsed_socket_path,
                parsed_db,
                parsed_username,
                parsed_password,
            ) = cls._parse_url(url)
        else:
            parsed_scheme = "redis"
            parsed_host = env.get("REDIS_HOST", default="localhost")
            parsed_port = int(env.get("REDIS_PORT", default="6379"))
            parsed_socket_path = None
            parsed_db = int(env.get("REDIS_DB", default="0"))
            parsed_username = ""
            parsed_password = env.get("REDIS_PASSWORD", default="")

        # 2. Per-field kwarg overrides win over both URL and discrete vars.
        final_scheme = scheme if scheme is not None else parsed_scheme
        final_host = host if host is not None else parsed_host
        final_port = port if port is not None else parsed_port
        final_socket_path = (
            socket_path if socket_path is not None else parsed_socket_path
        )
        final_db = db if db is not None else parsed_db
        final_username = username if username is not None else parsed_username
        if password is None:
            final_password = SecretStr(parsed_password)
        elif isinstance(password, str):
            final_password = SecretStr(password)
        else:
            final_password = password

        # 3. Validate scheme-specific invariants.
        if final_scheme == "unix":
            if not final_socket_path:
                msg = "Redis unix scheme requires a socket path"
                raise ValueError(msg)
            final_host = None
            final_port = None
        else:
            if not final_host:
                msg = f"Redis {final_scheme} scheme requires a host"
                raise ValueError(msg)
            if final_port is None or final_port <= 0:
                msg = f"Redis {final_scheme} scheme requires a positive port"
                raise ValueError(msg)
            final_socket_path = None

        return cls(
            scheme=final_scheme,
            host=final_host,
            port=final_port,
            socket_path=final_socket_path,
            db=final_db,
            username=final_username,
            password=final_password,
        )

    @staticmethod
    def _parse_url(
        url_str: str,
    ) -> tuple[
        Literal["redis", "rediss", "unix"],
        str | None,
        int | None,
        str | None,
        int,
        str,
        str,
    ]:
        parsed = urlparse(url_str)
        if parsed.scheme not in ("redis", "rediss", "unix"):
            msg = (
                f"Unsupported Redis URL scheme {parsed.scheme!r}; "
                "expected one of: redis, rediss, unix"
            )
            raise ValueError(msg)
        scheme: Literal["redis", "rediss", "unix"] = parsed.scheme  # type: ignore[assignment]

        username = unquote(parsed.username) if parsed.username else ""
        password = unquote(parsed.password) if parsed.password else ""

        if scheme == "unix":
            if parsed.netloc != "" or not parsed.path.startswith("/"):
                msg = (
                    "Redis unix URL must have an absolute socket path "
                    f"and no netloc, got {url_str!r}"
                )
                raise ValueError(msg)
            socket_path = parsed.path
            db_values = parse_qs(parsed.query).get("db", ["0"])
            db = RedisConfig._parse_db(db_values[0])
            return scheme, None, None, socket_path, db, username, password

        host = parsed.hostname
        if not host:
            msg = f"Redis {scheme} URL requires a host"
            raise ValueError(msg)
        port = parsed.port if parsed.port is not None else 6379
        db_path = parsed.path.lstrip("/") if parsed.path else ""
        db = RedisConfig._parse_db(db_path) if db_path else 0
        return scheme, host, port, None, db, username, password

    @staticmethod
    def _parse_db(db_str: str) -> int:
        try:
            return int(db_str)
        except ValueError as e:
            msg = f"Redis URL has invalid db value {db_str!r}"
            raise ValueError(msg) from e

    @property
    def url(self) -> str:
        user = self.username
        pwd = self.password.get_secret_value()
        if user and pwd:
            auth = f"{quote(user, safe='')}:{quote(pwd, safe='')}@"
        elif pwd:
            auth = f":{quote(pwd, safe='')}@"
        elif user:
            auth = f"{quote(user, safe='')}@"
        else:
            auth = ""

        if self.scheme == "unix":
            return f"unix://{auth}{self.socket_path}?db={self.db}"
        return f"{self.scheme}://{auth}{self.host}:{self.port}/{self.db}"


class PubsubConfig(NamedTuple):
    url: str

    @classmethod
    def from_env(
        cls,
        url: str | None = None,
        test: bool | None = None,
    ) -> Self:
        if url is None:
            redis_config = RedisConfig.from_env(test=test)
            url = redis_config.url

        return cls(url=url)


class EmailConfig(NamedTuple):
    server: str
    port: int
    username: str
    password: SecretStr
    from_email: str
    from_name: str

    @classmethod
    def from_env(
        cls,
        server: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: SecretStr | str | None = None,
        from_email: str | None = None,
        from_name: str | None = None,
        test: bool | None = None,
    ) -> Self:
        env = EnvironmentVariablesReader(test=test)

        if server is None:
            server = env["EMAIL_SERVER"]
        if port is None:
            port = int(env["EMAIL_PORT"])
        if username is None:
            username = env["EMAIL_USERNAME"]
        if password is None:
            password = env["EMAIL_PASSWORD"]
        if from_email is None:
            from_email = env["EMAIL_FROM_EMAIL"]
        if from_name is None:
            from_name = env["EMAIL_FROM_NAME"]

        if isinstance(password, str):
            password = SecretStr(password)

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
        test: bool | None = None,
    ) -> Self:
        env = EnvironmentVariablesReader(test=test)

        if endpoint_url is None:
            endpoint_url = env["S3_ENDPOINT_URL"]
        if access_key is None:
            access_key = env["S3_ACCESS_KEY"]
        if secret_key is None:
            secret_key = env["S3_SECRET_KEY"]
        if bucket is None:
            bucket = env["S3_BUCKET"]
        if public_url is None:
            public_url = env["S3_PUBLIC_URL"]

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
        test: bool | None = None,
    ) -> Self:
        env = EnvironmentVariablesReader(test=test)

        if algorithm is None:
            algorithm = env.get(
                "JWT_ALGORITHM",
                default="HS256",
            )

        if secret_key is None:
            secret_key = env["JWT_SECRET_KEY"]

        if refresh_token_duration is None:
            refresh_token_duration = timedelta(
                days=int(
                    env.get(
                        "JWT_REFRESH_TOKEN_DURATION_DAYS",
                        default=7,
                    )
                ),
            )

        if access_token_duration is None:
            access_token_duration = timedelta(
                minutes=int(
                    env.get(
                        "JWT_ACCESS_TOKEN_DURATION_MINUTES",
                        default=15,
                    )
                ),
            )

        if account_password_reset_authorization_duration is None:
            account_password_reset_authorization_duration = timedelta(
                minutes=int(
                    env.get(
                        "ACCOUNT_PASSWORD_RESET_AUTHORIZATION_DURATION_MINUTES",
                        default=20,
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
        anon: int | None = None,
        default_anon: int,
        auth: int | None = None,
        default_auth: int,
        window_seconds: int | None = None,
        default_window_seconds: int,
        test: bool | None = None,
    ) -> Self:
        env = EnvironmentVariablesReader(test=test)

        anon = int(
            env.get(
                f"{env_prefix}_RATE_LIMIT_ANON",
                default=str(default_anon),
            )
        )
        auth = int(
            env.get(
                f"{env_prefix}_RATE_LIMIT_AUTH",
                default=str(default_auth),
            )
        )
        window = timedelta(
            seconds=int(
                env.get(
                    f"{env_prefix}_RATE_LIMIT_WINDOW_SECONDS",
                    default=str(default_window_seconds),
                ),
            ),
        )
        return cls(
            anon=anon,
            auth=auth,
            window=window,
        )


class ContactConfig(NamedTuple):
    email: str
    rate_limit: RateLimitConfig

    @classmethod
    def from_env(
        cls,
        email: str | None = None,
        rate_limit: RateLimitConfig | None = None,
        test: bool | None = None,
    ) -> Self:
        env = EnvironmentVariablesReader(test=test)

        if email is None:
            email = env["CONTACT_EMAIL"]
        if rate_limit is None:
            rate_limit = RateLimitConfig.from_env(
                env_prefix="CONTACT",
                default_anon=5,
                default_auth=10,
                default_window_seconds=3600,
            )
        return cls(
            email=email,
            rate_limit=rate_limit,
        )


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
        test: bool | None = None,
    ) -> Self:
        env = EnvironmentVariablesReader(test=test)

        if api_url is None:
            api_url = env["CAP_API_URL"]
        if site_key is None:
            site_key = env["CAP_SITE_KEY"]
        if secret_key is None:
            secret_key = env["CAP_SECRET_KEY"]
        return cls(
            api_url=api_url,
            site_key=site_key,
            secret_key=secret_key,
        )


class ImageConfig(NamedTuple):
    max_upload_bytes: int
    max_pixels: int
    max_concurrent_processing_per_worker: int

    @classmethod
    def from_env(cls, *, test: bool | None = None) -> Self:
        env = EnvironmentVariablesReader(test=test)
        return cls(
            max_upload_bytes=int(
                env.get(
                    "IMAGE_MAX_UPLOAD_BYTES",
                    default=str(5 * 1024 * 1024),
                ),
            ),
            max_pixels=int(
                env.get(
                    "IMAGE_MAX_PIXELS",
                    default="16000000",
                ),
            ),
            max_concurrent_processing_per_worker=int(
                env.get(
                    "IMAGE_MAX_CONCURRENT_PROCESSING_PER_WORKER",
                    default="4",
                ),
            ),
        )


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
    image: ImageConfig
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
        delay: float | None = None,
        database: DatabaseConfig | None = None,
        pubsub: PubsubConfig | None = None,
        email: EmailConfig | None = None,
        s3: S3Config | None = None,
        image: ImageConfig | None = None,
        redis: RedisConfig | None = None,
        auth: AuthConfig | None = None,
        contact: ContactConfig | None = None,
        cap: CapConfig | None = None,
        signup: RateLimitConfig | None = None,
        password_reset: RateLimitConfig | None = None,
        item_create: RateLimitConfig | None = None,
        image_upload: RateLimitConfig | None = None,
        test: bool | None = None,
    ) -> Self:
        if test is None:
            test = "PYTEST_CURRENT_TEST" in os.environ

        env = EnvironmentVariablesReader(test=test)

        if host_name is None:
            host_name = env["HOST_NAME"]

        if app_name is None:
            app_name = env["APP_NAME"]

        if root_path is None:
            root_path = env.get("ROOT_PATH", default="")

        if delay is None:
            delay = float(env.get("DELAY", default="0"))

        if database is None:
            database = DatabaseConfig.from_env(test=test)

        if redis is None:
            redis = RedisConfig.from_env(test=test)

        if pubsub is None:
            pubsub = PubsubConfig.from_env(url=redis.url, test=test)

        if email is None:
            email = EmailConfig.from_env(test=test)

        if s3 is None:
            s3 = S3Config.from_env(test=test)

        if image is None:
            image = ImageConfig.from_env(test=test)

        if auth is None:
            auth = AuthConfig.from_env(test=test)

        if contact is None:
            contact = ContactConfig.from_env(test=test)

        if cap is None:
            cap = CapConfig.from_env(test=test)

        if signup is None:
            signup = RateLimitConfig.from_env(
                env_prefix="SIGNUP",
                default_anon=3,
                default_auth=3,
                default_window_seconds=3600,
                test=test,
            )
        if password_reset is None:
            password_reset = RateLimitConfig.from_env(
                env_prefix="PASSWORD_RESET",
                default_anon=3,
                default_auth=3,
                default_window_seconds=3600,
                test=test,
            )
        if item_create is None:
            item_create = RateLimitConfig.from_env(
                env_prefix="ITEM_CREATE",
                default_anon=30,
                default_auth=30,
                default_window_seconds=3600,
                test=test,
            )
        if image_upload is None:
            image_upload = RateLimitConfig.from_env(
                env_prefix="IMAGE_UPLOAD",
                default_anon=60,
                default_auth=60,
                default_window_seconds=3600,
                test=test,
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
            image=image,
            redis=redis,
            auth=auth,
            contact=contact,
            cap=cap,
            signup=signup,
            password_reset=password_reset,
            item_create=item_create,
            image_upload=image_upload,
        )
