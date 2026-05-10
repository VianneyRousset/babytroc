"""Loan seeds — bulk loan requests and loans on top of item-bearing templates."""

import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.item.models.item import Item
from babytroc.domains.loan import services as loan_services
from babytroc.domains.loan.enums import LoanRequestState
from babytroc.domains.loan.models import LoanRequest
from babytroc.domains.loan.schemas.base import ItemBorrowerId
from babytroc.domains.user.models import User
from babytroc.domains.user.services import get_user_by_email_private
from tests.fixtures.database.infrastructure.admin import session_against
from tests.fixtures.database.infrastructure.chain import SeedContext
from tests.utils import split


async def _alice_special_item(db: AsyncSession, *, alice_id: int) -> Item:
    return (
        await db.execute(
            select(Item)
            .where(Item.owner_id == alice_id)
            .where(Item.name == "Special item"),
        )
    ).scalar_one()


async def _check_min_states(
    db: AsyncSession,
    *,
    nmin: int = 10,
    skip: set[LoanRequestState] | None = None,
) -> None:
    skip = skip or {LoanRequestState.executed}
    rows = (await db.execute(select(LoanRequest))).scalars().all()
    for state in LoanRequestState:
        if state in skip:
            continue
        if sum(1 for r in rows if r.state == state) < nmin:
            msg = f"There must be at least {nmin} {state.name} loan requests"
            raise ValueError(msg)


async def seed_many_loan_requests_for_alice_items(
    db: AsyncSession,
    ctx: SeedContext,
) -> None:
    """Cancelled/rejected/accepted/executed/pending requests on alice's items.

    Random seed: 0x32D1. Mirrors the old `many_loan_requests_for_alice_items`
    class fixture exactly.
    """
    del ctx
    random.seed(0x32D1)

    alice = await get_user_by_email_private(db=db, email="alice@babytroc.ch")
    bob = await get_user_by_email_private(db=db, email="bob@babytroc.ch")
    carol = await get_user_by_email_private(db=db, email="carol@babytroc.ch")

    alice_items = (
        (await db.execute(select(Item).where(Item.owner_id == alice.id)))
        .scalars()
        .all()
    )

    items_to_request = random.sample(alice_items, k=round(0.9 * len(alice_items)))
    borrowers = [bob, carol]

    new_loan_requests = await loan_services.create_many_loan_requests(
        db=db,
        loan_requests={
            ItemBorrowerId.from_values(item_id=item.id, borrower_id=borrower.id)
            for item, borrower in zip(
                items_to_request,
                random.choices(borrowers, k=len(items_to_request)),
                strict=True,
            )
        },
    )

    selected, _remaining = split(
        random.sample(new_loan_requests, k=len(new_loan_requests)),
        2,
    )
    selected_list = list(selected)
    to_execute, selected_list = selected_list[:1], selected_list[1:]
    to_cancel, to_reject, to_accept = (list(g) for g in split(selected_list, 3))

    await loan_services.cancel_many_loan_requests(
        db=db,
        loan_request_ids={r.id for r in to_cancel},
        send_messages=False,
    )
    await loan_services.reject_many_loan_requests(
        db=db,
        loan_request_ids={r.id for r in to_reject},
        send_messages=False,
    )
    await loan_services.accept_many_loan_requests(
        db=db,
        loan_request_ids={r.id for r in to_accept},
        send_messages=False,
    )
    await loan_services.execute_many_loan_requests(
        db=db,
        loan_request_ids={r.id for r in to_execute},
        send_messages=False,
        check_state=False,
    )

    await _check_min_states(db)


async def seed_alice_special_item_loan_requests(
    db: AsyncSession,
    ctx: SeedContext,
) -> None:
    """Many users requesting alice's special item, varied states. Seed: 0x50E6."""
    del ctx
    random.seed(0x50E6)

    alice = await get_user_by_email_private(db=db, email="alice@babytroc.ch")
    special = await _alice_special_item(db, alice_id=alice.id)

    extra_users = (
        (
            await db.execute(
                select(User).where(
                    User.email.notin_(
                        [
                            "alice@babytroc.ch",
                            "bob@babytroc.ch",
                            "carol@babytroc.ch",
                        ],
                    ),
                ),
            )
        )
        .scalars()
        .all()
    )

    borrowers = random.sample(extra_users, k=round(0.9 * len(extra_users)))

    new_loan_requests = await loan_services.create_many_loan_requests(
        db=db,
        item_ids=special.id,
        borrower_ids={u.id for u in borrowers},
    )

    selected, _remaining = split(
        random.sample(new_loan_requests, k=len(new_loan_requests)),
        2,
    )
    selected_list = list(selected)
    to_execute, selected_list = selected_list[:1], selected_list[1:]
    to_cancel, to_reject, to_accept = (list(g) for g in split(selected_list, 3))

    await loan_services.cancel_many_loan_requests(
        db=db,
        loan_request_ids={r.id for r in to_cancel},
        send_messages=False,
    )
    await loan_services.reject_many_loan_requests(
        db=db,
        loan_request_ids={r.id for r in to_reject},
        send_messages=False,
    )
    await loan_services.accept_many_loan_requests(
        db=db,
        loan_request_ids={r.id for r in to_accept},
        send_messages=False,
    )
    await loan_services.execute_many_loan_requests(
        db=db,
        loan_request_ids={r.id for r in to_execute},
        send_messages=False,
        check_state=False,
    )


async def seed_alice_many_loans(db: AsyncSession, ctx: SeedContext) -> None:
    """Loans on alice's items, half ended, half restarted. Seed: 0x50E6.

    Each phase (create→execute, end, re-create→re-execute, end-twice) runs
    in its OWN transaction so postgres `now()` advances between them.
    Otherwise `end_many_loans` intersects `during` with
    `tstzrange(NULL, now())` using the same transaction-time `now()` as
    `execute`, producing empty ranges.
    """
    del db
    random.seed(0x50E6)

    async with session_against(ctx.db_url) as s:
        alice = await get_user_by_email_private(db=s, email="alice@babytroc.ch")
        bob = await get_user_by_email_private(db=s, email="bob@babytroc.ch")
        carol = await get_user_by_email_private(db=s, email="carol@babytroc.ch")
        borrowers = [bob, carol]

        alice_items = (
            (await s.execute(select(Item).where(Item.owner_id == alice.id)))
            .scalars()
            .all()
        )
        items = random.sample(alice_items, k=round(0.5 * len(alice_items)))

        loan_requests = await loan_services.create_many_loan_requests(
            db=s,
            loan_requests={
                ItemBorrowerId.from_values(
                    item_id=item.id,
                    borrower_id=borrower.id,
                )
                for item, borrower in zip(
                    items,
                    random.choices(borrowers, k=len(items)),
                    strict=True,
                )
            },
        )

        loans = await loan_services.execute_many_loan_requests(
            db=s,
            loan_request_ids={r.id for r in loan_requests},
            check_state=False,
        )
        loan_ids_first_batch = [loan.id for loan in loans]

    async with session_against(ctx.db_url) as s:
        ended_loan_ids = set(
            random.sample(
                loan_ids_first_batch,
                k=round(len(loan_ids_first_batch) * 0.7),
            ),
        )
        ended_loans = await loan_services.end_many_loans(
            db=s,
            loan_ids=ended_loan_ids,
        )
        ended_item_ids = [loan.item.id for loan in ended_loans]

    async with session_against(ctx.db_url) as s:
        items_to_request_again_ids = random.sample(
            ended_item_ids, k=len(ended_item_ids) // 2,
        )
        loan_requests = await loan_services.create_many_loan_requests(
            db=s,
            loan_requests={
                ItemBorrowerId.from_values(
                    item_id=item_id,
                    borrower_id=borrower.id,
                )
                for item_id, borrower in zip(
                    items_to_request_again_ids,
                    random.choices(borrowers, k=len(items_to_request_again_ids)),
                    strict=True,
                )
            },
        )
        restarted_loans = await loan_services.execute_many_loan_requests(
            db=s,
            loan_request_ids={r.id for r in loan_requests},
            check_state=False,
        )
        restarted_loan_ids = [loan.id for loan in restarted_loans]

    async with session_against(ctx.db_url) as s:
        _restarted, ended_twice = split(restarted_loan_ids, 2)
        await loan_services.end_many_loans(
            db=s,
            loan_ids=set(ended_twice),
        )
