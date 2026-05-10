"""Baseline image seed — Alice and Bob's PBM item images."""

from io import BytesIO

from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.image.services import upload_image
from babytroc.domains.user.services import get_user_by_email_private
from tests.fixtures.database.infrastructure.chain import SeedContext

_ALICE_ITEMS_IMG = b"P1\n3 3\n101\n101\n010"
_ALICE_NEW_ITEM_IMG = b"P1\n3 3\n000\n111\n000"
_ALICE_SPECIAL_ITEM_IMG = b"P1\n3 3\n101\n111\n010"
_BOB_ITEMS_IMG = b"P1\n3 3\n101\n101\n010"


async def seed_baseline_images(db: AsyncSession, ctx: SeedContext) -> None:
    """Upload 7 PBM images.

    1 alice_items, 3 alice_new_item, 2 alice_special_item, 1 bob_items.

    Order matters — `alice_items_image`, `alice_new_item_images`,
    `alice_special_item_images`, `bob_items_image` fixtures select by
    `ItemImage.name` ordering.
    """
    config = ctx.config
    alice = await get_user_by_email_private(db=db, email="alice@babytroc.ch")
    bob = await get_user_by_email_private(db=db, email="bob@babytroc.ch")

    await upload_image(
        config=config,
        db=db,
        owner_id=alice.id,
        fp=BytesIO(_ALICE_ITEMS_IMG),
    )

    for _ in range(3):
        await upload_image(
            config=config,
            db=db,
            owner_id=alice.id,
            fp=BytesIO(_ALICE_NEW_ITEM_IMG),
        )

    for _ in range(2):
        await upload_image(
            config=config,
            db=db,
            owner_id=alice.id,
            fp=BytesIO(_ALICE_SPECIAL_ITEM_IMG),
        )

    await upload_image(
        config=config,
        db=db,
        owner_id=bob.id,
        fp=BytesIO(_BOB_ITEMS_IMG),
    )
