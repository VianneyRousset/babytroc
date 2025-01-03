import os
from typing import NamedTuple

import sqlalchemy


class Config(NamedTuple):
    class ImgPush(NamedTuple):
        url: str

        @staticmethod
        def from_env() -> "Config.ImgPush":
            imgpush_host = os.environ["IMGPUSH_HOST"]
            imgpush_port = int(os.environ["IMGPUSH_PORT"])

            return Config.ImgPush(
                url=f"http://{imgpush_host}:{imgpush_port}",
            )

    postgres_url: sqlalchemy.URL
    imgpush: ImgPush

    @staticmethod
    def from_env() -> "Config":
        postgres_user = os.environ["POSTGRES_USER"]
        postgres_password = os.environ["POSTGRES_PASSWORD"]
        postgres_host = os.environ["POSTGRES_HOST"]
        postgres_port = int(os.environ["POSTGRES_PORT"])
        postgres_database = os.environ["POSTGRES_DATABASE"]

        return Config(
            postgres_url=sqlalchemy.URL.create(
                "postgresql+psycopg2",
                username=postgres_user,
                password=postgres_password,
                host=postgres_host,
                port=postgres_port,
                database=postgres_database,
            ),
            imgpush=Config.ImgPush.from_env(),
        )
