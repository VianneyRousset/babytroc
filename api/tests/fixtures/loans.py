import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from babytroc.domains.item.models.item import Item
from babytroc.domains.item.schemas.read import ItemRead
from babytroc.domains.loan import services as loan_services
from babytroc.domains.loan.models import Loan, LoanRequest
from babytroc.domains.loan.schemas.query import LoanRequestUpdateQueryFilter
from babytroc.domains.loan.schemas.read import LoanRead, LoanRequestRead
from babytroc.domains.user.schemas.private import UserPrivateRead


@pytest.fixture
async def bob_new_loan_request_for_alice_new_item(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
    alice_new_item: ItemRead,
    bob: UserPrivateRead,
) -> LoanRequestRead:
    """A new loan request made by Bob for the new item of Alice.

    fixture scope: function.
    """

    async with database_sessionmaker.begin() as session:
        return await loan_services.create_loan_request(
            db=session,
            item_id=alice_new_item.id,
            borrower_id=bob.id,
        )


@pytest.fixture
async def bob_new_loan_request_for_alice_special_item(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
    alice_special_item: ItemRead,
    bob: UserPrivateRead,
) -> LoanRequestRead:
    """A new loan request made by Bob for the special item of Alice.

    fixture scope: function.
    """

    async with database_sessionmaker.begin() as session:
        return await loan_services.create_loan_request(
            db=session,
            item_id=alice_special_item.id,
            borrower_id=bob.id,
        )


@pytest.fixture
async def bob_accepted_loan_request_for_alice_special_item(
    database_sessionmaker: async_sessionmaker,
    bob_new_loan_request_for_alice_special_item: LoanRequestRead,
) -> LoanRequestRead:
    """An accepted loan request made by Bob for the special item of Alice.

    fixture scope: function.
    """

    async with database_sessionmaker.begin() as session:
        return await loan_services.accept_loan_request(
            db=session,
            loan_request_id=bob_new_loan_request_for_alice_special_item.id,
        )


@pytest.fixture
async def bob_new_loan_for_alice_special_item(
    database_sessionmaker: async_sessionmaker,
    bob_accepted_loan_request_for_alice_special_item: LoanRequestRead,
) -> LoanRead:
    """An active loan to Bob for the special item of Alice.

    fixture scope: function.
    """

    async with database_sessionmaker.begin() as session:
        return await loan_services.execute_loan_request(
            db=session,
            loan_request_id=bob_accepted_loan_request_for_alice_special_item.id,
        )


@pytest.fixture
async def carol_new_loan_request_for_alice_new_item(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
    alice_new_item: ItemRead,
    carol: UserPrivateRead,
) -> LoanRequestRead:
    """A new loan request made by Carol for the new item of Alice.

    fixture scope: function.
    """

    async with database_sessionmaker.begin() as session:
        return await loan_services.create_loan_request(
            db=session,
            item_id=alice_new_item.id,
            borrower_id=carol.id,
        )


@pytest.fixture
async def bob_new_loan_of_alice_new_item(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
    alice_new_item: ItemRead,
    bob: UserPrivateRead,
    bob_new_loan_request_for_alice_new_item: LoanRequestRead,
) -> LoanRead:
    """A new loan request made by Bob for the new alice of Alice.

    fixture scope: function.
    """

    async with database_sessionmaker.begin() as session:
        # execute loan request
        return await loan_services.execute_loan_request(
            db=session,
            loan_request_id=bob_new_loan_request_for_alice_new_item.id,
            query_filter=LoanRequestUpdateQueryFilter(
                owner_id=alice.id,
                borrower_id=bob.id,
            ),
            check_state=False,
        )


async def _select_loan_request_ids(
    database_sessionmaker: async_sessionmaker,
    *,
    where,
) -> list[LoanRequestRead]:
    async with database_sessionmaker.begin() as session:
        ids = (
            (
                await session.execute(
                    select(LoanRequest.id).where(where).order_by(LoanRequest.id),
                )
            )
            .scalars()
            .all()
        )
        if not ids:
            return []
        return await loan_services.get_many_loan_requests(
            db=session,
            loan_request_ids=set(ids),
        )


@pytest.fixture
async def many_loan_requests_for_alice_items(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
) -> list[LoanRequestRead]:
    """SELECT every loan request on Alice-owned items.

    Backed by `tpl_many_loan_requests`.
    """
    async with database_sessionmaker.begin() as session:
        ids = (
            (
                await session.execute(
                    select(LoanRequest.id)
                    .join(Item, Item.id == LoanRequest.item_id)
                    .where(Item.owner_id == alice.id)
                    .order_by(LoanRequest.id),
                )
            )
            .scalars()
            .all()
        )
        if not ids:
            return []
        return await loan_services.get_many_loan_requests(
            db=session,
            loan_request_ids=set(ids),
        )


@pytest.fixture
async def many_loan_requests_for_alice_special_item(
    database_sessionmaker: async_sessionmaker,
    alice_special_item: ItemRead,
) -> list[LoanRequestRead]:
    """SELECT every loan request on Alice's special item.

    Backed by `tpl_alice_special_item_loan_requests`.
    """
    return await _select_loan_request_ids(
        database_sessionmaker,
        where=(LoanRequest.item_id == alice_special_item.id),
    )


@pytest.fixture
async def alice_many_loans(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
) -> list[LoanRead]:
    """SELECT every loan on an Alice-owned item.

    Backed by `tpl_alice_many_loans`.
    """
    async with database_sessionmaker.begin() as session:
        ids = (
            (
                await session.execute(
                    select(Loan.id)
                    .join(Item, Item.id == Loan.item_id)
                    .where(Item.owner_id == alice.id)
                    .order_by(Loan.id),
                )
            )
            .scalars()
            .all()
        )
        if not ids:
            return []
        return await loan_services.get_many_loans(db=session, loan_ids=set(ids))
