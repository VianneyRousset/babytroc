import os
from datetime import timedelta
from typing import NamedTuple, Self

import sqlalchemy


class DatabaseConfig(NamedTuple):
    url: sqlalchemy.URL
    async_url: sqlalchemy.URL

    @classmethod
    def from_env(
        cls,
        url: sqlalchemy.URL | None = None,
        async_url: sqlalchemy.URL | None = None,
    ) -> Self:
        if url is None:
            user = os.environ["POSTGRES_USER"]
            password = os.environ["POSTGRES_PASSWORD"]
            host = os.environ["POSTGRES_HOST"]
            port = int(os.environ["POSTGRES_PORT"])
            database = os.environ["POSTGRES_DATABASE"]

            url = sqlalchemy.URL.create(
                "postgresql+psycopg2",
                username=user,
                password=password,
                host=host,
                port=port,
                database=database,
            )

        if async_url is None:
            user = os.environ["POSTGRES_USER"]
            password = os.environ["POSTGRES_PASSWORD"]
            host = os.environ["POSTGRES_HOST"]
            port = int(os.environ["POSTGRES_PORT"])
            database = os.environ["POSTGRES_DATABASE"]

            async_url = sqlalchemy.URL.create(
                "postgresql+psycopg_async",
                username=user,
                password=password,
                host=host,
                port=port,
                database=database,
            )

        return cls(
            url=url,
            async_url=async_url,
        )


class PubsubConfig(NamedTuple):
    url: sqlalchemy.URL

    @classmethod
    def from_env(cls, url: sqlalchemy.URL | None = None) -> Self:
        if url is None:
            user = os.environ["POSTGRES_USER"]
            password = os.environ["POSTGRES_PASSWORD"]
            host = os.environ["POSTGRES_HOST"]
            port = int(os.environ["POSTGRES_PORT"])
            database = os.environ["POSTGRES_DATABASE"]

            url = sqlalchemy.URL.create(
                "postgresql",
                username=user,
                password=password,
                host=host,
                port=port,
                database=database,
            )

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
            server = os.environ["EMAIL_SERVER"]
        if port is None:
            port = int(os.environ["EMAIL_PORT"])
        if username is None:
            username = os.environ["EMAIL_USERNAME"]
        if password is None:
            password = os.environ["EMAIL_PASSWORD"]
        if from_email is None:
            from_email = os.environ["EMAIL_FROM_EMAIL"]
        if from_name is None:
            from_name = os.environ["EMAIL_FROM_NAME"]

        return cls(
            server=server,
            port=port,
            username=username,
            password=password,
            from_email=from_email,
            from_name=from_name,
        )


class ImgpushConfig(NamedTuple):
    url: str

    @classmethod
    def from_env(cls, url: str | None = None) -> Self:
        if url is None:
            imgpush_host = os.environ["IMGPUSH_HOST"]
            imgpush_port = int(os.environ["IMGPUSH_PORT"])
            url = f"http://{imgpush_host}:{imgpush_port}"

        return cls(url=url)


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
            algorithm = os.environ["JWT_ALGORITHM"]

        if secret_key is None:
            secret_key = os.environ["JWT_SECRET_KEY"]

        if refresh_token_duration is None:
            refresh_token_duration = timedelta(
                days=int(os.environ["JWT_REFRESH_TOKEN_DURATION_DAYS"])
            )

        if access_token_duration is None:
            access_token_duration = timedelta(
                minutes=int(os.environ["JWT_ACCESS_TOKEN_DURATION_MINUTES"])
            )

        if account_password_reset_authorization_duration is None:
            account_password_reset_authorization_duration = timedelta(
                minutes=int(
                    os.environ["ACCOUNT_PASSWORD_RESET_AUTHORIZATION_DURATION_MINUTES"]
                )
            )
        return cls(
            algorithm=algorithm,
            secret_key=secret_key,
            refresh_token_duration=refresh_token_duration,
            access_token_duration=access_token_duration,
            account_password_reset_authorization_duration=account_password_reset_authorization_duration,
        )


class Config(NamedTuple):
    app_name: str
    test: bool
    database: DatabaseConfig
    pubsub: PubsubConfig
    email: EmailConfig
    imgpush: ImgpushConfig
    auth: AuthConfig

    @classmethod
    def from_env(
        cls,
        *,
        app_name: str | None = None,
        test: bool | None = None,
        database: DatabaseConfig | None = None,
        pubsub: PubsubConfig | None = None,
        email: EmailConfig | None = None,
        imgpush: ImgpushConfig | None = None,
        auth: AuthConfig | None = None,
    ) -> Self:
        if app_name is None:
            app_name = os.environ["APP_NAME"]

        if test is None:
            test = "PYTEST_CURRENT_TEST" in os.environ

        if database is None:
            database = DatabaseConfig.from_env()

        if pubsub is None:
            pubsub = PubsubConfig.from_env()

        if email is None:
            email = EmailConfig.from_env()

        if imgpush is None:
            imgpush = ImgpushConfig.from_env()

        if auth is None:
            auth = AuthConfig.from_env()

        return cls(
            app_name=app_name,
            test=test,
            database=database,
            pubsub=pubsub,
            email=email,
            imgpush=imgpush,
            auth=auth,
        )
