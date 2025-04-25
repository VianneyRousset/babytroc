from typing import TypedDict

import pytest
import sqlalchemy
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import services
from app.schemas.image.read import ItemImageRead
from app.schemas.item.create import ItemCreate
from app.schemas.item.preview import ItemPreviewRead
from app.schemas.region.read import RegionRead
from app.schemas.user.read import UserRead


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


@pytest.fixture
def alice_items_data(
    alice_client: TestClient,
    alice_items_image: ItemImageRead,
    regions: list[RegionRead],
) -> list[ItemData]:
    """Alice items data."""

    return [
        {
            "name": "candle",
            "description": "dwell into a flowerbed",
            "targeted_age_months": [4, 10],
            "regions": [regions[0].id],
            "images": [alice_items_image.name],
        },
    ]


@pytest.fixture
def bob_items_data(
    bob_client: TestClient,
    bob_items_image: ItemImageRead,
    regions: list[RegionRead],
) -> list[ItemData]:
    """Bob items data."""

    return [
        {
            "name": "Dark side",
            "description": "Breathe, breathe in the air. Don't be afraid to care",
            "targeted_age_months": [16, None],
            "regions": [regions[0].id, regions[1].id],
            "images": [bob_items_image.name],
        },
    ]


@pytest.fixture
def alice_item_image_data() -> str:
    """Basic PBM image."""

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
def bob_item_image_data() -> str:
    """Basic PBM image."""

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
def alice_items_image(
    alice_client: TestClient,
    alice_item_image_data: str,
) -> ItemImageRead:
    """Ensure Alice's item image exists."""

    resp = alice_client.post(
        "/v1/images",
        files={"file": alice_item_image_data},
    )
    resp.raise_for_status()
    return ItemImageRead(**resp.json())


@pytest.fixture
def bob_items_image(
    bob_client: TestClient,
    bob_item_image_data: str,
) -> ItemImageRead:
    """Ensure Bob's item image exists."""

    resp = bob_client.post(
        "/v1/images",
        files={"file": bob_item_image_data},
    )
    resp.raise_for_status()
    return ItemImageRead(**resp.json())


@pytest.fixture
def alice_items(
    database: sqlalchemy.URL,
    alice: UserRead,
    alice_items_data: list[ItemData],
) -> list[ItemPreviewRead]:
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


@pytest.fixture
def bob_items(
    database: sqlalchemy.URL,
    bob: UserRead,
    bob_items_data: list[ItemData],
) -> list[ItemPreviewRead]:
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
