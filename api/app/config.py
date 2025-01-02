import os
from typing import NamedTuple


class Config(NamedTuple):
    database_url: str
    imgpush_url: str

    @staticmethod
    def from_env() -> "Config":
        POSTGRES_USER = os.environ["POSTGRES_USER"]
        POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
        POSTGRES_HOST = os.environ["POSTGRES_HOST"]
        POSTGRES_PORT = int(os.environ["POSTGRES_PORT"])
        POSTGRES_DATABASE = os.environ["POSTGRES_DATABASE"]

        IMGPUSH_HOST = os.environ["IMGPUSH_HOST"]
        IMGPUSH_PORT = int(os.environ["IMGPUSH_PORT"])

        return Config(
            database_url=f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/${POSTGRES_DATABASE}",
            imgpush_url=f"http://{IMGPUSH_HOST}:{IMGPUSH_PORT}",
        )
