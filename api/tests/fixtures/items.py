import random
from io import BytesIO
from string import ascii_letters
from typing import TypedDict, TypeVar

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


def random_str(length: int) -> str:
    return "".join(random.choices(ascii_letters, k=length))


def random_targeted_age_months() -> tuple[int | None, int | None]:
    lower = random.randint(0, 32)
    upper = random.randint(lower, 33)
    return None if lower == 0 else lower, None if upper > 32 else upper


T = TypeVar("T")


def random_sample(population: list[T]) -> list[T]:
    return random.sample(population, k=random.randint(1, len(population)))


def create_random_item(
    db: sqlalchemy.orm.Session,
    alice: UserPrivateRead,
    bob: UserPrivateRead,
    alice_items_image: ItemImageRead,
    bob_items_image: ItemImageRead,
    regions: list[RegionRead],
) -> ItemRead:
    owner, image = random.choice(
        [
            (alice, alice_items_image),
            (bob, bob_items_image),
        ]
    )

    return services.item.create_item(
        db=db,
        owner_id=owner.id,
        item_create=ItemCreate(
            name=random_str(8),
            description=random_str(50),
            targeted_age_months=random_targeted_age_months(),
            regions=random_sample([reg.id for reg in regions]),
            images=[image.name],
        ),
    )


@pytest.fixture(scope="class")
def many_items(
    database: sqlalchemy.URL,
    alice: UserPrivateRead,
    bob: UserPrivateRead,
    alice_items_image: ItemImageRead,
    bob_items_image: ItemImageRead,
    regions: list[RegionRead],
) -> list[ItemRead]:
    """Many items."""

    n = 256
    random.seed(0xBDF81829)

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return [
            create_random_item(
                db=session,
                alice=alice,
                bob=bob,
                alice_items_image=alice_items_image,
                bob_items_image=bob_items_image,
                regions=regions,
            )
            for _ in range(n)
        ]
