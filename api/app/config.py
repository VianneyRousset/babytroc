import os
from datetime import timedelta
from typing import NamedTuple, Self

import sqlalchemy


class DatabaseConfig(NamedTuple):
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
                "postgresql+psycopg2",
                username=user,
                password=password,
                host=host,
                port=port,
                database=database,
            )

        return cls(url=url)


class PubsubConfig(NamedTuple):
    url: str

    @classmethod
    def from_env(cls, url: sqlalchemy.URL | str | None = None) -> Self:
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

        if isinstance(url, sqlalchemy.URL):
            url = str(url)

        return cls(url=url)


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

    @classmethod
    def from_env(
        cls,
        algorithm: str | None = None,
        secret_key: str | None = None,
        refresh_token_duration: timedelta | None = None,
        access_token_duration: timedelta | None = None,
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

        return cls(
            algorithm=algorithm,
            secret_key=secret_key,
            refresh_token_duration=refresh_token_duration,
            access_token_duration=access_token_duration,
        )


class Config(NamedTuple):
    test: bool
    database: DatabaseConfig
    pubsub: PubsubConfig
    imgpush: ImgpushConfig
    auth: AuthConfig

    @classmethod
    def from_env(
        cls,
        *,
        test: bool | None = None,
        database: DatabaseConfig | None = None,
        pubsub: PubsubConfig | None = None,
        imgpush: ImgpushConfig | None = None,
        auth: AuthConfig | None = None,
    ) -> Self:
        if test is None:
            test = "PYTEST_CURRENT_TEST" in os.environ

        if database is None:
            database = DatabaseConfig.from_env()

        if pubsub is None:
            pubsub = PubsubConfig.from_env()

        if imgpush is None:
            imgpush = ImgpushConfig.from_env()

        if auth is None:
            auth = AuthConfig.from_env()

        return cls(
            test=test,
            database=database,
            pubsub=pubsub,
            imgpush=imgpush,
            auth=auth,
        )
