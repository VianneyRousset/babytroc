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
from app import services
from app.app import create_app
from app.config import Config, ImgPushConfig
from app.schemas.item.create import ItemCreate
from app.schemas.region.create import RegionCreate
from app.schemas.user.create import UserCreate


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
def users_data() -> list[dict]:
    return [
        {
            "name": "alice",
            "email": "alice@ekindbaby.ch",
            "password": "password-alice",
        },
        {
            "name": "bob",
            "email": "bob@ekindbaby.ch",
            "password": "password-bob",
        },
    ]


@pytest.fixture
def users(database: sqlalchemy.URL, users_data: list[dict]) -> list[int]:
    # make sqlalchemy warnings as errors
    warnings.simplefilter("error", sqlalchemy.exc.SAWarning)

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return [
            services.user.create_user(
                session,
                UserCreate(**user),
            ).id
            for user in users_data
        ]


@pytest.fixture
def regions_data() -> list[dict]:
    return [
        {
            "id": 1,
            "name": "region1",
        },
        {
            "id": 2,
            "name": "region2",
        },
    ]


@pytest.fixture
def regions(database: sqlalchemy.URL, regions_data: list[dict]) -> list[int]:
    # make sqlalchemy warnings as errors
    warnings.simplefilter("error", sqlalchemy.exc.SAWarning)

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return [
            services.region.create_region(
                session,
                RegionCreate(**region),
            ).id
            for region in regions_data
        ]


@pytest.fixture
def image_data() -> str:
    # basic PBM image
    return "\n".join(
        [
            "P1",
            "3 3",
            "101",
            "101",
            "010",
        ]
    )


@pytest.fixture
def image(client: TestClient, users: list[int], image_data: str) -> str:
    resp = client.post("/v1/images", files={"file": image_data})
    resp.raise_for_status()
    added = resp.json()

    return added["name"]


@pytest.fixture
def items_data(
    image: str,
    regions: list[int],
    users: list[int],
) -> list[dict]:
    return [
        {
            "owner_id": users[0],
            "name": "candle",
            "description": "dwell into a flowerbed",
            "targeted_age_months": [4, 10],
            "regions": [regions[0]],
            "images": [image],
        },
        {
            "owner_id": users[1],
            "name": "Dark side",
            "description": "Breathe, breathe in the air. Don't be afraid to care",
            "targeted_age_months": [16, None],
            "regions": [regions[0], regions[1]],
            "images": [image],
        },
    ]


@pytest.fixture
def items(
    database: sqlalchemy.URL,
    items_data: list[dict],
) -> list[int]:
    # make sqlalchemy warnings as errors
    warnings.simplefilter("error", sqlalchemy.exc.SAWarning)

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return [
            services.item.create_item(
                db=session,
                owner_id=item["owner_id"],
                item_create=ItemCreate(
                    **{k: v for k, v in item.items() if k != "owner_id"}
                ),
            ).id
            for item in items_data
        ]
