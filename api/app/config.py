import os
from typing import NamedTuple, Self

import sqlalchemy


class ImgPushConfig(NamedTuple):
    url: str

    @classmethod
    def from_env(cls) -> Self:
        imgpush_host = os.environ["IMGPUSH_HOST"]
        imgpush_port = int(os.environ["IMGPUSH_PORT"])

        return cls(
            url=f"http://{imgpush_host}:{imgpush_port}",
        )


class Config(NamedTuple):
    postgres_url: sqlalchemy.URL
    imgpush: ImgPushConfig

    @classmethod
    def from_env(cls) -> "Config":
        postgres_user = os.environ["POSTGRES_USER"]
        postgres_password = os.environ["POSTGRES_PASSWORD"]
        postgres_host = os.environ["POSTGRES_HOST"]
        postgres_port = int(os.environ["POSTGRES_PORT"])
        postgres_database = os.environ["POSTGRES_DATABASE"]

        return cls(
            postgres_url=sqlalchemy.URL.create(
                "postgresql+psycopg2",
                username=postgres_user,
                password=postgres_password,
                host=postgres_host,
                port=postgres_port,
                database=postgres_database,
            ),
            imgpush=ImgPushConfig.from_env(),
        )
