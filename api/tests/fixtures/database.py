import asyncio
import os
import warnings
from collections.abc import AsyncGenerator
from functools import partial
from io import BytesIO
from pathlib import Path
from uuid import uuid4

import pytest
from alembic.config import Config as AlembicConfig
from sqlalchemy import URL, text
from sqlalchemy.exc import SAWarning
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from alembic import command

from babytroc.domains.category.schemas.create import CategoryCreate
from babytroc.domains.category.services import create_many_categories
from babytroc.domains.image.services import upload_image
from babytroc.domains.region.schemas.create import RegionCreate
from babytroc.domains.region.services import create_region
from babytroc.domains.user.schemas.create import UserCreate
from babytroc.domains.user.services import (
    create_many_users_without_validation,
    get_user_by_email_private,
)
from babytroc.infrastructure.config import Config, S3Config

# make sqlalchemy warnings as errors
warnings.simplefilter("error", SAWarning)


def run_alembic_upgrade_head(url: URL):
    # apply alembic migrations
    app_root = Path(__file__).parent.parent.parent
    alembic_cfg = AlembicConfig(app_root / "alembic.ini")
    alembic_cfg.set_main_option("script_location", str(app_root / "alembic"))
    alembic_cfg.set_main_option(
        "sqlalchemy.url", url.render_as_string(hide_password=False)
    )
    command.upgrade(alembic_cfg, "head")


async def _seed_template(url: URL) -> None:
    """Seed the template database with reference data."""

    config = Config.from_env(
        s3=S3Config(
            endpoint_url="http://localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            bucket="test-bucket",
            public_url="http://localhost:9000/test-bucket",
        ),
    )

    engine = create_async_engine(url=url, echo=False, poolclass=NullPool)
    session_maker = async_sessionmaker(bind=engine)

    try:
        async with session_maker() as db, db.begin():
            # --- Users ---
            await create_many_users_without_validation(
                db=db,
                user_creates=[
                    UserCreate(
                        name="alice",
                        email="alice@babytroc.ch",
                        password="password-Alice-42",
                    ),
                    UserCreate(
                        name="bob",
                        email="bob@babytroc.ch",
                        password="password-Bob-42",
                    ),
                    UserCreate(
                        name="carol",
                        email="carol@babytroc.ch",
                        password="password-Carol-42",
                    ),
                ],
                validated=True,
            )

            # --- Regions ---
            await create_region(db=db, region_create=RegionCreate(id=1, name="region1"))
            await create_region(db=db, region_create=RegionCreate(id=2, name="region2"))

            # --- Categories ---
            parents = [
                CategoryCreate(slug="clothing", name="Vêtements"),
                CategoryCreate(slug="toys", name="Jouets"),
                CategoryCreate(slug="gear", name="Équipement"),
            ]
            await create_many_categories(db=db, category_creates=parents)

            children = [
                CategoryCreate(
                    slug="clothing-bodysuits",
                    name="Bodies",
                    parent_slug="clothing",
                ),
                CategoryCreate(
                    slug="clothing-sleepwear",
                    name="Pyjamas",
                    parent_slug="clothing",
                ),
                CategoryCreate(
                    slug="clothing-outerwear",
                    name="Manteaux",
                    parent_slug="clothing",
                ),
                CategoryCreate(
                    slug="clothing-accessories",
                    name="Accessoires",
                    parent_slug="clothing",
                ),
                CategoryCreate(
                    slug="toys-bath",
                    name="Jouets de bain",
                    parent_slug="toys",
                ),
                CategoryCreate(
                    slug="toys-soft",
                    name="Peluches",
                    parent_slug="toys",
                ),
                CategoryCreate(
                    slug="toys-educational",
                    name="Jouets éducatifs",
                    parent_slug="toys",
                ),
                CategoryCreate(
                    slug="gear-strollers",
                    name="Poussettes",
                    parent_slug="gear",
                ),
                CategoryCreate(
                    slug="gear-car-seats",
                    name="Sièges auto",
                    parent_slug="gear",
                ),
                CategoryCreate(
                    slug="gear-carriers",
                    name="Porte-bébés",
                    parent_slug="gear",
                ),
            ]
            await create_many_categories(db=db, category_creates=children)

            # --- Images ---
            alice = await get_user_by_email_private(db=db, email="alice@babytroc.ch")
            bob = await get_user_by_email_private(db=db, email="bob@babytroc.ch")

            alice_items_data = b"P1\n3 3\n101\n101\n010"
            alice_new_item_data = b"P1\n3 3\n000\n111\n000"
            alice_special_item_data = b"P1\n3 3\n101\n111\n010"
            bob_items_data = b"P1\n3 3\n101\n101\n010"

            # alice_items: 1 image
            await upload_image(
                config=config,
                db=db,
                owner_id=alice.id,
                fp=BytesIO(alice_items_data),
            )

            # alice_new_item: 3 images
            for _ in range(3):
                await upload_image(
                    config=config,
                    db=db,
                    owner_id=alice.id,
                    fp=BytesIO(alice_new_item_data),
                )

            # alice_special_item: 2 images
            for _ in range(2):
                await upload_image(
                    config=config,
                    db=db,
                    owner_id=alice.id,
                    fp=BytesIO(alice_special_item_data),
                )

            # bob_items: 1 image
            await upload_image(
                config=config,
                db=db,
                owner_id=bob.id,
                fp=BytesIO(bob_items_data),
            )

    finally:
        await engine.dispose()


@pytest.fixture(scope="session")
async def primary_database() -> AsyncGenerator[URL]:
    name = f"test-primary_database-{uuid4()}"

    # create URL
    url = URL.create(
        drivername="postgresql+asyncpg",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        database=name,
    )

    # create database
    await create_database(url)

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, partial(run_alembic_upgrade_head, url))

    # seed reference data
    await _seed_template(url)

    # yield database url
    yield url

    # destroy database
    await drop_database(url)


@pytest.fixture(scope="function")
async def database(
    primary_database: URL,
    testrun_uid: str,
) -> AsyncGenerator[URL]:
    """Create a temporary database with alembic migrations applied."""

    name = f"test-{uuid4()}-{testrun_uid}"

    # create URL
    url = URL.create(
        drivername=primary_database.drivername,
        username=primary_database.username,
        password=primary_database.password,
        host=primary_database.host,
        port=primary_database.port,
        database=name,
    )

    # create database
    await create_database(url, template=primary_database.database)

    # yield database url
    yield url

    # destroy database
    await drop_database(url)


@pytest.fixture(scope="function")
async def database_sessionmaker(
    database: URL,
) -> AsyncGenerator[async_sessionmaker]:
    from babytroc.infrastructure.database import init_db_session_dependency

    engine = create_async_engine(
        url=database,
        echo=False,
        poolclass=NullPool,
    )

    maker = async_sessionmaker(bind=engine)

    # Immediately swap the app's session maker so all HTTP requests
    # through the ASGI app use this test's database.
    init_db_session_dependency(maker)

    yield maker

    await engine.dispose()


async def create_database(
    url: URL,
    *,
    encoding="utf8",
    template=None,
) -> None:
    database = url.database
    url = url._replace(database="postgres")

    engine = create_async_engine(url, isolation_level="AUTOCOMMIT", poolclass=NullPool)

    # postgres default database template
    if template is None:
        template = "template1"

    try:
        async with engine.begin() as conn:
            stmt = text(
                f'CREATE DATABASE "{database}" '
                f"ENCODING '{encoding}' "
                f'TEMPLATE "{template}"'
            )
            await conn.execute(stmt)

    finally:
        await engine.dispose()


async def _set_datallowconn(url: URL, *, allow: bool) -> None:
    """Set datallowconn on the database."""
    database = url.database
    admin_url = url._replace(database="postgres")
    engine = create_async_engine(
        admin_url, isolation_level="AUTOCOMMIT", poolclass=NullPool,
    )
    try:
        async with engine.begin() as conn:
            val = "true" if allow else "false"
            await conn.execute(
                text(
                    f'ALTER DATABASE "{database}" '
                    f"WITH ALLOW_CONNECTIONS = {val}"
                ),
            )
    finally:
        await engine.dispose()


async def drop_database(url: URL) -> None:
    database = url.database
    url = url._replace(database="postgres")

    engine = create_async_engine(url, isolation_level="AUTOCOMMIT", poolclass=NullPool)

    try:
        async with engine.begin() as conn:
            stmt = text(f'DROP DATABASE "{database}"')
            await conn.execute(stmt)

    finally:
        await engine.dispose()
