import os
import random
import string
import warnings
from collections.abc import Generator
from pathlib import Path

import pytest
import sqlalchemy
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, drop_database

from alembic import command
from alembic.config import Config as AlembicConfig
from app.app import create_app
from app.config import Config, ImgPushConfig
from app.schemas.item.create import ItemCreate
from app.schemas.user.create import UserCreate
from app.services.item import create_item
from app.services.user import create_user


def random_string(length: int):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


@pytest.fixture
def database() -> Generator[sqlalchemy.URL]:
    database = random_string(4)

    postgres_url = sqlalchemy.URL.create(
        "postgresql+psycopg2",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        database=database,
    )

    create_database(postgres_url)

    app_root = Path(__file__).parent.parent
    alembic_cfg = AlembicConfig(app_root / "alembic.ini")
    alembic_cfg.set_main_option("script_location", str(app_root / "alembic"))
    alembic_cfg.set_main_option(
        "sqlalchemy.url", postgres_url.render_as_string(hide_password=False)
    )
    command.upgrade(alembic_cfg, "head")

    yield postgres_url

    drop_database(postgres_url)


@pytest.fixture
def client(database: sqlalchemy.URL) -> TestClient:
    config = Config(
        postgres_url=database,
        imgpush=ImgPushConfig.from_env(),
    )

    return TestClient(create_app(config))


@pytest.fixture
def user_alice_data() -> dict:
    return {
        "name": "alice",
        "email": "alice@ekindbaby.ch",
        "password": "password-alice",
    }


@pytest.fixture
def user_bob_data() -> dict:
    return {
        "name": "bob",
        "email": "bob@ekindbaby.ch",
        "password": "password-bob",
    }


@pytest.fixture
def user_alice(database: sqlalchemy.URL, user_alice_data: dict) -> int:
    # make sqlalchemy warnings as errors
    warnings.simplefilter("error", sqlalchemy.exc.SAWarning)

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        user = create_user(
            session,
            UserCreate(**user_alice_data),
        )

        return user.id


@pytest.fixture
def user_bob(database: sqlalchemy.URL, user_bob_data: dict) -> int:
    # make sqlalchemy warnings as errors
    warnings.simplefilter("error", sqlalchemy.exc.SAWarning)

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        user = create_user(
            session,
            UserCreate(**user_bob_data),
        )

        return user.id


@pytest.fixture
def image(client: TestClient) -> str:
    # basic PBM image
    image = "\n".join(
        [
            "P1",
            "3 3",
            "101",
            "101",
            "010",
        ]
    )

    resp = client.post("/v1/images", files={"file": image})
    resp.raise_for_status()
    added = resp.json()

    return added["name"]


@pytest.fixture
def item_candle_data(image: str) -> dict:
    return {
        "name": "candle",
        "description": "dwell into a flowerbed",
        "targeted_age_months": [4, 10],
        "regions": [],
        "images": [image],
    }


@pytest.fixture
def item_candle(
    database: sqlalchemy.URL,
    user_alice: int,
    item_candle_data: dict,
) -> int:
    # make sqlalchemy warnings as errors
    warnings.simplefilter("error", sqlalchemy.exc.SAWarning)

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        item = create_item(
            db=session,
            owner_id=user_alice,
            item_create=ItemCreate(**item_candle_data),
        )

        return item.id
