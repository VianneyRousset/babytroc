import os
from typing import NamedTuple

from sqlalchemy import URL as sqlURL


class Config(NamedTuple):
    class ImgPush(NamedTuple):
        url: str

        @staticmethod
        def from_env() -> "Config.ImgPush":
            IMGPUSH_HOST = os.environ["IMGPUSH_HOST"]
            IMGPUSH_PORT = int(os.environ["IMGPUSH_PORT"])

            return Config.ImgPush(
                url=f"http://{IMGPUSH_HOST}:{IMGPUSH_PORT}",
            )

    postgres_url: sqlURL
    imgpush: ImgPush

    @staticmethod
    def from_env() -> "Config":
        POSTGRES_USER = os.environ["POSTGRES_USER"]
        POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
        POSTGRES_HOST = os.environ["POSTGRES_HOST"]
        POSTGRES_PORT = int(os.environ["POSTGRES_PORT"])
        POSTGRES_DATABASE = os.environ["POSTGRES_DATABASE"]

        return Config(
            postgres_url=sqlURL.create(
                "postgresql+psycopg2",
                username=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                database=POSTGRES_DATABASE,
            ),
            imgpush=Config.ImgPush.from_env(),
        )
