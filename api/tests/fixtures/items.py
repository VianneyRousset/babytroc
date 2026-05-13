import random
from typing import TypedDict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from babytroc.domains.image.schemas.read import ItemImageRead
from babytroc.domains.item import services as item_services
from babytroc.domains.item.models.image import ItemImage
from babytroc.domains.item.models.item import Item
from babytroc.domains.item.schemas.read import ItemRead
from babytroc.domains.region.schemas.read import RegionRead
from babytroc.domains.user.schemas.private import UserPrivateRead
from tests.utils import random_str


class UserData(TypedDict):
    name: str
    email: str
    password: str


class ItemData(TypedDict):
    name: str
    description: str
    targeted_age_months: str
    regions: list[int]
    images: list[str]
    cap_token: str


@pytest.fixture
async def alice_items_data(
    alice_items_image: ItemImageRead,
    regions: list[RegionRead],
) -> list[ItemData]:
    """Alice items data."""

    return [
        {
            "name": "candle",
            "description": "dwell into a flowerbed",
            "targeted_age_months": "4-10",
            "regions": [regions[0].id],
            "images": [alice_items_image.name],
            "cap_token": "valid",
        },
    ]


@pytest.fixture
async def alice_new_item_data(
    alice_new_item_images: list[ItemImageRead],
    regions: list[RegionRead],
) -> ItemData:
    """Alice new item data."""

    return {
        "name": "new-item",
        "description": "This is the latest new item created by alice.",
        "targeted_age_months": "7-",
        "regions": [regions[1].id],
        "images": [image.name for image in alice_new_item_images],
        "cap_token": "valid",
    }


@pytest.fixture
async def alice_special_item_data(
    alice_special_item_images: list[ItemImageRead],
    regions: list[RegionRead],
) -> ItemData:
    """Alice special item data."""

    return {
        "name": "Special item",
        "description": "This is the special item created by alice.",
        "targeted_age_months": "2-5",
        "regions": [regions[0].id],
        "images": [image.name for image in alice_special_item_images],
        "cap_token": "valid",
    }


@pytest.fixture
async def bob_items_data(
    bob_items_image: ItemImageRead,
    regions: list[RegionRead],
) -> list[ItemData]:
    """Bob items data."""

    return [
        {
            "name": "Dark side",
            "description": "Breathe, breathe in the air. Don't be afraid to care",
            "targeted_age_months": "16-",
            "regions": [regions[0].id, regions[1].id],
            "images": [bob_items_image.name],
            "cap_token": "valid",
        },
    ]


@pytest.fixture(scope="session")
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


@pytest.fixture(scope="session")
def alice_new_item_image_data() -> bytes:
    """Basic PBM image."""

    return "\n".join(
        [
            "P1",
            "3 3",
            "000",
            "111",
            "000",
        ]
    ).encode()


@pytest.fixture(scope="session")
def alice_special_item_image_data() -> bytes:
    """Basic PBM image."""

    return "\n".join(
        [
            "P1",
            "3 3",
            "101",
            "111",
            "010",
        ]
    ).encode()


@pytest.fixture(scope="session")
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


@pytest.fixture
async def alice_items_image(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
) -> ItemImageRead:
    """Reads Alice's first pre-seeded item image from DB."""

    async with database_sessionmaker.begin() as session:
        row = (
            await session.execute(
                select(ItemImage)
                .where(ItemImage.owner_id == alice.id)
                .order_by(ItemImage.name)
                .limit(1)
            )
        ).scalar_one()
        return ItemImageRead.model_validate(row)


@pytest.fixture
async def alice_new_item_images(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
) -> list[ItemImageRead]:
    """Reads Alice's 2nd-4th pre-seeded item images from DB."""

    async with database_sessionmaker.begin() as session:
        rows = (
            (
                await session.execute(
                    select(ItemImage)
                    .where(ItemImage.owner_id == alice.id)
                    .order_by(ItemImage.name)
                    .offset(1)
                    .limit(3)
                )
            )
            .scalars()
            .all()
        )
        return [ItemImageRead.model_validate(row) for row in rows]


@pytest.fixture
async def alice_special_item_images(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
) -> list[ItemImageRead]:
    """Reads Alice's 5th-6th pre-seeded item images from DB."""

    async with database_sessionmaker.begin() as session:
        rows = (
            (
                await session.execute(
                    select(ItemImage)
                    .where(ItemImage.owner_id == alice.id)
                    .order_by(ItemImage.name)
                    .offset(4)
                    .limit(2)
                )
            )
            .scalars()
            .all()
        )
        return [ItemImageRead.model_validate(row) for row in rows]


@pytest.fixture
async def bob_items_image(
    database_sessionmaker: async_sessionmaker,
    bob: UserPrivateRead,
) -> ItemImageRead:
    """Reads Bob's first pre-seeded item image from DB."""

    async with database_sessionmaker.begin() as session:
        row = (
            await session.execute(
                select(ItemImage)
                .where(ItemImage.owner_id == bob.id)
                .order_by(ItemImage.name)
                .limit(1)
            )
        ).scalar_one()
        return ItemImageRead.model_validate(row)


async def _select_items(
    database_sessionmaker: async_sessionmaker,
    *,
    owner_id: int,
    name: str | None = None,
) -> list[ItemRead]:
    async with database_sessionmaker.begin() as session:
        stmt = select(Item.id).where(Item.owner_id == owner_id)
        if name is not None:
            stmt = stmt.where(Item.name == name)
        ids = (await session.execute(stmt)).scalars().all()
        if not ids:
            return []
        return await item_services.get_many_items(db=session, item_ids=set(ids))


@pytest.fixture
async def alice_items(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
) -> list[ItemRead]:
    """SELECT every item Alice owns in the cloned DB.

    Includes alice_new_item and alice_special_item — same behavior as if
    those fixtures were also requested in the legacy build flow.
    """
    return await _select_items(database_sessionmaker, owner_id=alice.id)


@pytest.fixture
async def alice_new_item(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
) -> ItemRead:
    """SELECT Alice's new-item from the baseline_items template."""
    rows = await _select_items(
        database_sessionmaker,
        owner_id=alice.id,
        name="new-item",
    )
    return rows[0]


@pytest.fixture
async def alice_special_item(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
) -> ItemRead:
    """SELECT Alice's special-item from the baseline_items template."""
    rows = await _select_items(
        database_sessionmaker,
        owner_id=alice.id,
        name="Special item",
    )
    return rows[0]


@pytest.fixture
async def alice_many_items(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
) -> list[ItemRead]:
    """SELECT every Alice-owned item from the cloned DB.

    Backed by `tpl_alice_many_items` (256 + the baseline subset).
    """
    return await _select_items(database_sessionmaker, owner_id=alice.id)


@pytest.fixture
async def bob_items(
    database_sessionmaker: async_sessionmaker,
    bob: UserPrivateRead,
) -> list[ItemRead]:
    """SELECT every item Bob owns in the cloned DB."""
    return await _select_items(database_sessionmaker, owner_id=bob.id)


@pytest.fixture
async def items(
    alice_items: list[ItemRead],
    bob_items: list[ItemRead],
) -> list[ItemRead]:
    """All items."""

    return [
        *alice_items,
        *bob_items,
    ]


@pytest.fixture
async def many_items(
    database_sessionmaker: async_sessionmaker,
) -> list[ItemRead]:
    """SELECT every item from the cloned DB.

    Backed by `tpl_many_items` (~256 mixed Alice/Bob items + the 4 baseline
    items inherited from `tpl_baseline_items`).
    """
    async with database_sessionmaker.begin() as session:
        ids = (await session.execute(select(Item.id).order_by(Item.id))).scalars().all()
        if not ids:
            return []
        return await item_services.get_many_items(db=session, item_ids=set(ids))


@pytest.fixture(scope="session")
def some_item_french_names() -> list[str]:
    """Some item French names."""

    random.seed(0xA19F)

    return [
        "Le sénat du bien-être",
        "Le senat bleus",
        "Les sénats bleus",
        "L'importance du Bien être",
        "La Lettre bleu",
        "Les lettres bleus",
        "Les mots bleus",
        "Le sénat bleu",
        "Les leçons données",
        "La lecon de mon ami",
        "La caravane bleue",
        "L'écriture bleue",
        "La cerise bleue",
        *(f"{random_str(5)} bleu {random_str(5)}" for _ in range(40)),
    ]


@pytest.fixture
async def some_items_with_french_names(
    database_sessionmaker: async_sessionmaker,
    some_item_french_names: list[str],
) -> list[ItemRead]:
    """SELECT items whose name was seeded by `tpl_french_named_items`."""
    async with database_sessionmaker.begin() as session:
        ids = (
            (
                await session.execute(
                    select(Item.id)
                    .where(Item.name.in_(some_item_french_names))
                    .order_by(Item.id),
                )
            )
            .scalars()
            .all()
        )
        if not ids:
            return []
        return await item_services.get_many_items(db=session, item_ids=set(ids))
