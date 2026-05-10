"""Item seeds — baseline items per Alice/Bob; bulk variants in Phase 3."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.image.schemas.read import ItemImageRead
from babytroc.domains.item import services as item_services
from babytroc.domains.item.models.image import ItemImage
from babytroc.domains.item.schemas.base import MonthRange
from babytroc.domains.item.schemas.create import ItemCreate
from babytroc.domains.user.services import get_user_by_email_private
from tests.fixtures.database.infrastructure.chain import SeedContext


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
