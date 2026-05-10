"""Item seeds — baseline + bulk variants used by tests/item heavy templates."""

import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.image.schemas.read import ItemImageRead
from babytroc.domains.item import services as item_services
from babytroc.domains.item.models.image import ItemImage
from babytroc.domains.item.schemas.base import MonthRange
from babytroc.domains.item.schemas.create import ItemCreate
from babytroc.domains.region.services import list_regions
from babytroc.domains.user.services import get_user_by_email_private
from babytroc.infrastructure.cache_client import NullCache
from tests.fixtures.database.infrastructure.chain import SeedContext
from tests.utils import random_sample, random_str, random_targeted_age_months


async def _alice_image_at(
    db: AsyncSession,
    *,
    alice_id: int,
    offset: int,
) -> ItemImageRead:
    row = (
        await db.execute(
            select(ItemImage)
            .where(ItemImage.owner_id == alice_id)
            .order_by(ItemImage.name)
            .offset(offset)
            .limit(1),
        )
    ).scalar_one()
    return ItemImageRead.model_validate(row)


async def _alice_images_range(
    db: AsyncSession,
    *,
    alice_id: int,
    offset: int,
    limit: int,
) -> list[ItemImageRead]:
    rows = (
        (
            await db.execute(
                select(ItemImage)
                .where(ItemImage.owner_id == alice_id)
                .order_by(ItemImage.name)
                .offset(offset)
                .limit(limit),
            )
        )
        .scalars()
        .all()
    )
    return [ItemImageRead.model_validate(r) for r in rows]


async def _bob_image_at(db: AsyncSession, *, bob_id: int) -> ItemImageRead:
    row = (
        await db.execute(
            select(ItemImage)
            .where(ItemImage.owner_id == bob_id)
            .order_by(ItemImage.name)
            .limit(1),
        )
    ).scalar_one()
    return ItemImageRead.model_validate(row)


async def seed_baseline_items(db: AsyncSession, ctx: SeedContext) -> None:
    """Insert alice_items, bob_items, alice_new_item, alice_special_item.

    Uses the 7 PBM images already seeded by `seed_baseline_images`. Image
    ordering is deterministic so SELECT-by-name returns identical results
    across runs.
    """
    del ctx
    alice = await get_user_by_email_private(db=db, email="alice@babytroc.ch")
    bob = await get_user_by_email_private(db=db, email="bob@babytroc.ch")

    alice_items_image = await _alice_image_at(db, alice_id=alice.id, offset=0)
    alice_new_item_images = await _alice_images_range(
        db,
        alice_id=alice.id,
        offset=1,
        limit=3,
    )
    alice_special_item_images = await _alice_images_range(
        db,
        alice_id=alice.id,
        offset=4,
        limit=2,
    )
    bob_items_image = await _bob_image_at(db, bob_id=bob.id)

    await item_services.create_item(
        db=db,
        owner_id=alice.id,
        item_create=ItemCreate(
            name="candle",
            description="dwell into a flowerbed",
            targeted_age_months=MonthRange("4-10"),
            regions={1},
            images=[alice_items_image.name],
        ),
    )

    await item_services.create_item(
        db=db,
        owner_id=alice.id,
        item_create=ItemCreate(
            name="new-item",
            description="This is the latest new item created by alice.",
            targeted_age_months=MonthRange("7-"),
            regions={2},
            images=[img.name for img in alice_new_item_images],
        ),
    )

    await item_services.create_item(
        db=db,
        owner_id=alice.id,
        item_create=ItemCreate(
            name="Special item",
            description="This is the special item created by alice.",
            targeted_age_months=MonthRange("2-5"),
            regions={1},
            images=[img.name for img in alice_special_item_images],
        ),
    )

    await item_services.create_item(
        db=db,
        owner_id=bob.id,
        item_create=ItemCreate(
            name="Dark side",
            description="Breathe, breathe in the air. Don't be afraid to care",
            targeted_age_months=MonthRange("16-"),
            regions={1, 2},
            images=[bob_items_image.name],
        ),
    )


_FRENCH_NAMES = [
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
]


async def seed_many_items(db: AsyncSession, ctx: SeedContext) -> None:
    """Create 256 mixed Alice/Bob items. Random seed: 0xBDF81829.

    Mirrors the old class-scoped `many_items` fixture exactly.
    """
    del ctx
    n = 256
    random.seed(0xBDF81829)

    alice = await get_user_by_email_private(db=db, email="alice@babytroc.ch")
    bob = await get_user_by_email_private(db=db, email="bob@babytroc.ch")
    alice_image = await _alice_image_at(db, alice_id=alice.id, offset=0)
    bob_image = await _bob_image_at(db, bob_id=bob.id)
    regions = await list_regions(db, NullCache())

    owner_ids, images = (
        list(column)
        for column in zip(
            *random.choices(
                [(alice.id, alice_image), (bob.id, bob_image)],
                k=n,
            ),
            strict=True,
        )
    )

    await item_services.create_many_items(
        db=db,
        items=[
            item_services.create.CreateItem(
                owner_id=owner_id,
                item_create=ItemCreate(
                    name=random_str(8),
                    description=random_str(50),
                    targeted_age_months=random_targeted_age_months(),
                    regions=set(random_sample([reg.id for reg in regions])),
                    images=[image.name],
                    blocked=random.choice([False] * 3 + [True]),
                ),
            )
            for owner_id, image in zip(owner_ids, images, strict=True)
        ],
    )


async def seed_alice_many_items(db: AsyncSession, ctx: SeedContext) -> None:
    """Create 256 Alice-owned items, all `blocked=False`. Random seed: 0x25D4."""
    del ctx
    n = 256
    random.seed(0x25D4)

    alice = await get_user_by_email_private(db=db, email="alice@babytroc.ch")
    alice_image = await _alice_image_at(db, alice_id=alice.id, offset=0)
    regions = await list_regions(db, NullCache())

    await item_services.create_many_items(
        db=db,
        items=[
            item_services.create.CreateItem(
                owner_id=alice.id,
                item_create=ItemCreate(
                    name=random_str(8),
                    description=random_str(50),
                    targeted_age_months=random_targeted_age_months(),
                    regions=set(random_sample([reg.id for reg in regions])),
                    images=[alice_image.name],
                    blocked=False,
                ),
            )
            for _ in range(n)
        ],
    )


async def seed_french_named_items(db: AsyncSession, ctx: SeedContext) -> None:
    """Create ~53 mixed Alice/Bob items with French-style names.

    Random seed: 0xA19F (names) + 0x15976 (assignments).
    """
    del ctx
    random.seed(0xA19F)
    names = [
        *_FRENCH_NAMES,
        *(f"{random_str(5)} bleu {random_str(5)}" for _ in range(40)),
    ]

    random.seed(0x15976)

    alice = await get_user_by_email_private(db=db, email="alice@babytroc.ch")
    bob = await get_user_by_email_private(db=db, email="bob@babytroc.ch")
    alice_image = await _alice_image_at(db, alice_id=alice.id, offset=0)
    bob_image = await _bob_image_at(db, bob_id=bob.id)
    regions = await list_regions(db, NullCache())

    owner_ids, images = (
        list(column)
        for column in zip(
            *random.choices(
                [(alice.id, alice_image), (bob.id, bob_image)],
                k=len(names),
            ),
            strict=True,
        )
    )

    await item_services.create_many_items(
        db=db,
        items=[
            item_services.create.CreateItem(
                owner_id=owner_id,
                item_create=ItemCreate(
                    name=name,
                    description=random_str(50),
                    targeted_age_months=random_targeted_age_months(),
                    regions=set(random_sample([reg.id for reg in regions])),
                    images=[image.name],
                    blocked=random.choice([False] * 3 + [True]),
                ),
            )
            for name, owner_id, image in zip(names, owner_ids, images, strict=True)
        ],
    )
