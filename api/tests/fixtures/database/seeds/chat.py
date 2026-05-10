"""Chat seeds — alice_many_chats on top of many_items."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.item.models.item import Item
from babytroc.domains.loan import services as loan_services
from babytroc.domains.user.services import get_user_by_email_private
from tests.fixtures.database.infrastructure.chain import SeedContext


async def seed_alice_many_chats(db: AsyncSession, ctx: SeedContext) -> None:
    """Create one loan request per Alice/Bob item.

    Each loan request implicitly creates a chat (Alice↔Bob) and a
    loan-request-created chat message.
    """
    del ctx
    alice = await get_user_by_email_private(db=db, email="alice@babytroc.ch")
    bob = await get_user_by_email_private(db=db, email="bob@babytroc.ch")

    items = (
        (
            await db.execute(
                select(Item).where(Item.owner_id.in_({alice.id, bob.id})),
            )
        )
        .scalars()
        .all()
    )

    for item in items:
        borrower_id = alice.id if item.owner_id == bob.id else bob.id
        await loan_services.create_loan_request(
            db=db,
            item_id=item.id,
            borrower_id=borrower_id,
        )
