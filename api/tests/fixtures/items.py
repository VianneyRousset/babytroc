from io import BytesIO
from typing import TypedDict

import pytest
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import services
from app.config import Config
from app.schemas.image.read import ItemImageRead
from app.schemas.item.create import ItemCreate
from app.schemas.item.read import ItemRead
from app.schemas.region.read import RegionRead
from app.schemas.user.private import UserPrivateRead


class UserData(TypedDict):
    name: str
    email: str
    password: str


class ItemData(TypedDict):
    name: str
    description: str
    targeted_age_months: tuple[int | None, int | None]
    regions: list[int]
    images: list[str]


@pytest.fixture(scope="class")
def alice_items_data(
    alice_items_image: ItemImageRead,
    regions: list[RegionRead],
) -> list[ItemData]:
    """Alice items data."""

    return [
        {
            "name": "candle",
            "description": "dwell into a flowerbed",
            "targeted_age_months": (4, 10),
            "regions": [regions[0].id],
            "images": [alice_items_image.name],
        },
    ]


@pytest.fixture(scope="class")
def alice_new_item_data(
    alice_items_image: ItemImageRead,
    regions: list[RegionRead],
) -> ItemData:
    """Alice new item data."""

    return {
        "name": "new-item",
        "description": "This is the latest new item created by alice.",
        "targeted_age_months": (7, None),
        "regions": [regions[1].id],
        "images": [alice_items_image.name],
    }


@pytest.fixture(scope="class")
def bob_items_data(
    bob_items_image: ItemImageRead,
    regions: list[RegionRead],
) -> list[ItemData]:
    """Bob items data."""

    return [
        {
            "name": "Dark side",
            "description": "Breathe, breathe in the air. Don't be afraid to care",
            "targeted_age_months": (16, None),
            "regions": [regions[0].id, regions[1].id],
            "images": [bob_items_image.name],
        },
    ]


@pytest.fixture(scope="class")
def alice_items_image_data() -> bytes:
    """Basic PBM image."""

    return "\n".join(
        [
            "P1",
            "3 3",
            "101",
            "101",
            "010",
        ]
    ).encode()


@pytest.fixture(scope="class")
def bob_items_image_data() -> bytes:
    """Basic PBM image."""

    return "\n".join(
        [
            "P1",
            "3 3",
            "101",
            "101",
            "010",
        ]
    ).encode()


@pytest.fixture(scope="class")
def alice_items_image(
    app_config: Config,
    database: sqlalchemy.URL,
    alice: UserPrivateRead,
    alice_items_image_data: bytes,
) -> ItemImageRead:
    """Ensure Alice's item image exists."""

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return services.image.upload_image(
            db=session,
            config=app_config,
            owner_id=alice.id,
            fp=BytesIO(alice_items_image_data),
        )


@pytest.fixture(scope="class")
def bob_items_image(
    app_config: Config,
    database: sqlalchemy.URL,
    bob: UserPrivateRead,
    bob_items_image_data: bytes,
) -> ItemImageRead:
    """Ensure Bob's item image exists."""

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return services.image.upload_image(
            db=session,
            config=app_config,
            owner_id=bob.id,
            fp=BytesIO(bob_items_image_data),
        )


@pytest.fixture(scope="class")
def alice_items(
    database: sqlalchemy.URL,
    alice: UserPrivateRead,
    alice_items_data: list[ItemData],
) -> list[ItemRead]:
    """Ensures Alice's items exist."""

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return [
            services.item.create_item(
                db=session,
                owner_id=alice.id,
                item_create=ItemCreate(**item),
            )
            for item in alice_items_data
        ]


# scope function
@pytest.fixture
def alice_new_item(
    database: sqlalchemy.URL,
    alice: UserPrivateRead,
    alice_new_item_data: ItemData,
) -> ItemRead:
    """Alice's new items."""

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return services.item.create_item(
            db=session,
            owner_id=alice.id,
            item_create=ItemCreate(**alice_new_item_data),
        )


@pytest.fixture(scope="class")
def bob_items(
    database: sqlalchemy.URL,
    bob: UserPrivateRead,
    bob_items_data: list[ItemData],
) -> list[ItemRead]:
    """Ensures bob's items exist."""

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return [
            services.item.create_item(
                db=session,
                owner_id=bob.id,
                item_create=ItemCreate(**item),
            )
            for item in bob_items_data
        ]


@pytest.fixture(scope="class")
def items(
    alice_items: list[ItemRead],
    bob_items: list[ItemRead],
) -> list[ItemRead]:
    """All items."""

    return [
        *alice_items,
        *bob_items,
    ]
