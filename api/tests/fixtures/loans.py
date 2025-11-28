import random

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app import services
from app.enums import LoanRequestState
from app.schemas.item.read import ItemRead
from app.schemas.loan.base import ItemBorrowerId
from app.schemas.loan.query import LoanRequestUpdateQueryFilter
from app.schemas.loan.read import LoanRead, LoanRequestRead
from app.schemas.user.private import UserPrivateRead
from tests.utils import split


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
        return await services.loan.create_loan_request(
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
        return await services.loan.create_loan_request(
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
        return await services.loan.accept_loan_request(
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
        return await services.loan.execute_loan_request(
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
        return await services.loan.create_loan_request(
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
        return await services.loan.execute_loan_request(
            db=session,
            loan_request_id=bob_new_loan_request_for_alice_new_item.id,
            query_filter=LoanRequestUpdateQueryFilter(
                owner_id=alice.id,
                borrower_id=bob.id,
            ),
            check_state=False,
        )


@pytest.fixture(scope="class")
async def many_loan_requests_for_alice_items(
    database_sessionmaker: async_sessionmaker,
    many_items: list[ItemRead],
    alice: UserPrivateRead,
    bob: UserPrivateRead,
    carol: UserPrivateRead,
) -> list[LoanRequestRead]:
    """Many loan requests made by Bob and Carol for Alice's many items.

    90% of the items owned by Alice are requested
    50% of the loan requests are pending
    1/3 of the loan requests are cancelled
    1/3 of the loan requests are rejected
    1/3 of the loan requests are accepted
    1 loan request is executed
    """

    random.seed(0x32D1)

    # select 90% of the items owned by alice
    items_owned_by_alice = [item for item in many_items if item.owner.id == alice.id]
    items_to_request = random.sample(
        items_owned_by_alice,
        k=round(0.9 * len(items_owned_by_alice)),
    )

    borrowers = [bob, carol]

    # create all loan requests
    async with database_sessionmaker.begin() as session:
        # create loan requests
        new_loan_requests = await services.loan.create_many_loan_requests(
            db=session,
            loan_requests={
                ItemBorrowerId.from_values(
                    item_id=item.id,
                    borrower_id=borrower.id,
                )
                for item, borrower in zip(
                    items_to_request,
                    random.choices(borrowers, k=len(items_to_request)),
                    strict=True,
                )
            },
        )

    # select 50% of the loan request to be either cancelled, rejected or accept
    # select 1/3 of the selected loan requests to be cancelled
    # select 1/3 of the selected loan requests to be rejected
    # select 1/3 of the selected loan requests to be accepted
    # select 1 of the selected loan requests to be executed
    (
        selected_loan_requests,
        remaing_loan_requests,
    ) = split(random.sample(new_loan_requests, k=len(new_loan_requests)), 2)

    loan_requests_to_execute, selected_loan_requests = (
        selected_loan_requests[:1],
        selected_loan_requests[1:],
    )

    (
        loan_requests_to_cancel,
        loan_requests_to_reject,
        loan_requests_to_accept,
    ) = split(selected_loan_requests, 3)

    # cancel seleced loan
    async with database_sessionmaker.begin() as session:
        cancelled_loan_requests: list[
            LoanRequestRead
        ] = await services.loan.cancel_many_loan_requests(
            db=session,
            loan_request_ids={req.id for req in loan_requests_to_cancel},
            send_messages=False,
        )

    # reject seleced loan
    async with database_sessionmaker.begin() as session:
        rejected_loan_requests: list[
            LoanRequestRead
        ] = await services.loan.reject_many_loan_requests(
            db=session,
            loan_request_ids={req.id for req in loan_requests_to_reject},
            send_messages=False,
        )

    # accept seleced loan
    async with database_sessionmaker.begin() as session:
        accepted_loan_requests: list[
            LoanRequestRead
        ] = await services.loan.accept_many_loan_requests(
            db=session,
            loan_request_ids={req.id for req in loan_requests_to_accept},
            send_messages=False,
        )

    # execute one of the accepted loan request
    async with database_sessionmaker.begin() as session:
        executed_loan_requests: list[LoanRequestRead] = [
            loan.loan_request
            for loan in await services.loan.execute_many_loan_requests(
                db=session,
                loan_request_ids={req.id for req in loan_requests_to_execute},
                send_messages=False,
                check_state=False,
            )
        ]

    # merge loan requests
    loan_requests: list[LoanRequestRead] = [
        *cancelled_loan_requests,
        *accepted_loan_requests,
        *rejected_loan_requests,
        *executed_loan_requests,
        *remaing_loan_requests,
    ]

    if len(loan_requests) != len(new_loan_requests):
        msg = "Incoherent numbre of loan requests"
        raise ValueError(msg)

    # suffle loan requests
    random.shuffle(loan_requests)

    # check there is at least 10 loan request of each state except `executed`
    for state in LoanRequestState:
        nmin = 10
        if (
            state != LoanRequestState.executed
            and len([req for req in loan_requests if req.state == state]) < 10
        ):
            msg = f"There must be at least {nmin} {state.name} loan requests"
            raise ValueError(msg)

    return loan_requests


@pytest.fixture(scope="class")
async def many_loan_requests_for_alice_special_item(
    database_sessionmaker: async_sessionmaker,
    many_users: list[UserPrivateRead],
    alice: UserPrivateRead,
    alice_special_item: ItemRead,
) -> list[LoanRequestRead]:
    """Loan requests from many users for Alice new item.

    90% of the many users requests Alice's special item.
    50% of the loan requests are pending
    1/3 of the loan requests are cancelled
    1/3 of the loan requests are rejected
    1/3 of the loan requests are accepted
    1 of the loan requests is executed
    """

    random.seed(0x50E6)

    # select 90% of all the many users that will request Alice new item
    borrowers = random.sample(many_users, k=round(0.9 * len(many_users)))

    async with database_sessionmaker.begin() as session:
        # create loan requests (shuffled)
        new_loan_requests = await services.loan.create_many_loan_requests(
            db=session,
            item_ids=alice_special_item.id,
            borrower_ids={user.id for user in borrowers},
        )

    # select 50% of the loan request to be either cancelled, rejected or accept
    # select 1/3 of the selected loan requests to be cancelled
    # select 1/3 of the selected loan requests to be rejected
    # select 1/3 of the selected loan requests to be accepted
    # select 1 of the selected loan requests to be executed
    (
        selected_loan_requests,
        remaing_loan_requests,
    ) = split(random.sample(new_loan_requests, k=len(new_loan_requests)), 2)

    loan_requests_to_execute, selected_loan_requests = (
        selected_loan_requests[:1],
        selected_loan_requests[1:],
    )

    (
        loan_requests_to_cancel,
        loan_requests_to_reject,
        loan_requests_to_accept,
    ) = split(selected_loan_requests, 3)

    # cancel seleced loan
    async with database_sessionmaker.begin() as session:
        cancelled_loan_requests: list[
            LoanRequestRead
        ] = await services.loan.cancel_many_loan_requests(
            db=session,
            loan_request_ids={req.id for req in loan_requests_to_cancel},
            send_messages=False,
        )

    # reject seleced loan
    async with database_sessionmaker.begin() as session:
        rejected_loan_requests: list[
            LoanRequestRead
        ] = await services.loan.reject_many_loan_requests(
            db=session,
            loan_request_ids={req.id for req in loan_requests_to_reject},
            send_messages=False,
        )

    # accept seleced loan
    async with database_sessionmaker.begin() as session:
        accepted_loan_requests: list[
            LoanRequestRead
        ] = await services.loan.accept_many_loan_requests(
            db=session,
            loan_request_ids={req.id for req in loan_requests_to_accept},
            send_messages=False,
        )

    # execute one of the accepted loan request
    async with database_sessionmaker.begin() as session:
        executed_loan_requests: list[LoanRequestRead] = [
            loan.loan_request
            for loan in await services.loan.execute_many_loan_requests(
                db=session,
                loan_request_ids={req.id for req in loan_requests_to_execute},
                send_messages=False,
                check_state=False,
            )
        ]

    # merge loan requests
    loan_requests: list[LoanRequestRead] = [
        *cancelled_loan_requests,
        *accepted_loan_requests,
        *rejected_loan_requests,
        *executed_loan_requests,
        *remaing_loan_requests,
    ]

    if len(loan_requests) != len(new_loan_requests):
        msg = "Incoherent number of loan requests"
        raise ValueError(msg)

    # suffle loan requests
    random.shuffle(loan_requests)

    # check there is at least 10 loan request of each state except `executed`
    for state in LoanRequestState:
        nmin = 10
        if (
            state != LoanRequestState.executed
            and len([req for req in loan_requests if req.state == state]) < 10
        ):
            msg = f"There must be at least {nmin} {state.name} loan requests"
            raise ValueError(msg)

    return loan_requests


@pytest.fixture(scope="class")
async def alice_many_loans(
    database_sessionmaker: async_sessionmaker,
    alice_many_items: list[ItemRead],
    alice: UserPrivateRead,
    bob: UserPrivateRead,
    carol: UserPrivateRead,
) -> list[LoanRead]:
    """Many loans made by Alice.

    50% of the many items owned by Alice are loaned to either Bob or carol.
    Among those loans, 70% of them are ended.
    Among those ended loans, 50% of the loaned items are loaned again.
    Among those new loans, 50% of the loaned are ended again.
    """

    random.seed(0x50E6)
    borrowers = [bob, carol]

    # select 90% of all the many users that will request Alice new item
    items = random.sample(alice_many_items, k=round(0.5 * len(alice_many_items)))

    # create loan requests
    async with database_sessionmaker.begin() as session:
        # create loan requests
        loan_requests = await services.loan.create_many_loan_requests(
            db=session,
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

    # execute all loan requests
    async with database_sessionmaker.begin() as session:
        loans = await services.loan.execute_many_loan_requests(
            db=session,
            loan_request_ids={req.id for req in loan_requests},
            check_state=False,
        )

    # end 70% of the loans
    async with database_sessionmaker.begin() as session:
        ended_loans = await services.loan.end_many_loans(
            db=session,
            loan_ids={
                loan.id for loan in random.sample(loans, k=round(len(loans) * 0.7))
            },
        )

    # request 50% of the ended loans
    async with database_sessionmaker.begin() as session:
        items_to_request_again = [
            loan.item for loan in random.sample(ended_loans, k=len(ended_loans) // 2)
        ]

        loan_requests = await services.loan.create_many_loan_requests(
            db=session,
            loan_requests={
                ItemBorrowerId.from_values(
                    item_id=item.id,
                    borrower_id=borrower.id,
                )
                for item, borrower in zip(
                    items_to_request_again,
                    random.choices(
                        borrowers,
                        k=len(items_to_request_again),
                    ),
                    strict=True,
                )
            },
        )
    # execute all new loan requests
    async with database_sessionmaker.begin() as session:
        restarted_loans = await services.loan.execute_many_loan_requests(
            db=session,
            loan_request_ids={req.id for req in loan_requests},
            check_state=False,
        )

    # end 50% of those restarted loans
    restarted_loans, ended_twice_loans = split(restarted_loans, 2)
    async with database_sessionmaker.begin() as session:
        ended_twice_loans = await services.loan.end_many_loans(
            db=session,
            loan_ids={loan.id for loan in ended_twice_loans},
        )

    # merge
    loans = list(
        {
            **{loan.id: loan for loan in loans},
            **{loan.id: loan for loan in ended_loans},
            **{loan.id: loan for loan in restarted_loans},
            **{loan.id: loan for loan in ended_twice_loans},
        }.values()
    )
    return random.sample(loans, k=len(loans))
