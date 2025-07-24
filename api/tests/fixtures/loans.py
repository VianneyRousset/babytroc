import random

import pytest
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import services
from app.schemas.item.read import ItemRead
from app.schemas.loan.query import LoanRequestQueryFilter
from app.schemas.loan.read import LoanRead, LoanRequestRead
from app.schemas.user.private import UserPrivateRead


@pytest.fixture
def bob_new_loan_request_for_alice_new_item(
    database: sqlalchemy.URL,
    alice: UserPrivateRead,
    alice_new_item: ItemRead,
    bob: UserPrivateRead,
) -> LoanRequestRead:
    """A new loan request made by Bob for the new alice of Alice.

    fixture scope: function.
    """

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return services.loan.create_loan_request(
            db=session,
            item_id=alice_new_item.id,
            borrower_id=bob.id,
        )


@pytest.fixture
def bob_new_loan_of_alice_new_item(
    database: sqlalchemy.URL,
    alice: UserPrivateRead,
    alice_new_item: ItemRead,
    bob: UserPrivateRead,
    bob_new_loan_request_for_alice_new_item: LoanRequestRead,
) -> LoanRead:
    """A new loan request made by Bob for the new alice of Alice.

    fixture scope: function.
    """

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        # execute loan request
        return services.loan.execute_loan_request(
            db=session,
            loan_request_id=bob_new_loan_request_for_alice_new_item.id,
            query_filter=LoanRequestQueryFilter(
                owner_id=alice.id,
                borrower_id=bob.id,
            ),
            check_state=False,
        )


@pytest.fixture(scope="class")
def many_loan_requests_for_alice_items(
    database: sqlalchemy.URL,
    many_items: list[ItemRead],
    alice: UserPrivateRead,
    bob: UserPrivateRead,
) -> list[LoanRequestRead]:
    """Many loan requests made by Bob for Alice's many items."""

    random.seed(0x32D1)

    # select 90% of the items owned by alice
    items_owned_by_alice = [item for item in many_items if item.owner_id == alice.id]
    items_to_request = random.sample(
        items_owned_by_alice,
        k=round(0.9 * len(items_owned_by_alice)),
    )

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        # create loan requests
        loan_requests = {
            loan_request.id: loan_request
            for loan_request in [
                services.loan.create_loan_request(
                    db=session,
                    item_id=item.id,
                    borrower_id=bob.id,
                )
                for item in items_to_request
            ]
        }

        # select 20% of the loan request to be either cancelled, rejected or accept
        n = round(0.2 * len(loan_requests))
        loan_request_ids_sample = random.sample(list(loan_requests.keys()), k=n)

        # cancel 1/3 of the selected loan requests
        for loan_request_id in loan_request_ids_sample[0 : n // 3]:
            loan_requests[loan_request_id] = services.loan.cancel_loan_request(
                db=session,
                loan_request_id=loan_request_id,
            )

        # reject 1/3 of the selected loan requests
        for loan_request_id in loan_request_ids_sample[n // 3 : 2 * n // 3]:
            loan_requests[loan_request_id] = services.loan.reject_loan_request(
                db=session,
                loan_request_id=loan_request_id,
            )

        # accept 1/3 of the selected loan requests
        for loan_request_id in loan_request_ids_sample[2 * n // 3 :]:
            loan_requests[loan_request_id] = services.loan.accept_loan_request(
                db=session,
                loan_request_id=loan_request_id,
            )

        # execute one loan request
        executed_loan_request_id = loan_request_ids_sample[-1]
        services.loan.execute_loan_request(
            db=session,
            loan_request_id=executed_loan_request_id,
        )

        # read updated loan request
        loan_requests[executed_loan_request_id] = services.loan.get_loan_request(
            db=session,
            loan_request_id=loan_request_id,
        )

        return list(loan_requests.values())


@pytest.fixture(scope="class")
def many_loan_requests_for_alice_special_item(
    database: sqlalchemy.URL,
    many_users: list[UserPrivateRead],
    alice: UserPrivateRead,
    alice_special_item: ItemRead,
) -> list[LoanRequestRead]:
    """Loan requests from many users for Alice new item."""

    random.seed(0x50E6)

    # select 90% of all the many users that will request Alice new item
    requesters = random.sample(many_users, k=round(0.9 * len(many_users)))

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        # create loan requests
        loan_requests = {
            loan_request.id: loan_request
            for loan_request in [
                services.loan.create_loan_request(
                    db=session,
                    item_id=alice_special_item.id,
                    borrower_id=requester.id,
                )
                for requester in requesters
            ]
        }

        # select 20% of the loan request to be either cancelled, rejected or accepted
        n = round(0.2 * len(loan_requests))
        loan_request_ids_sample = random.sample(list(loan_requests.keys()), k=n)

        # cancel 1/3 of the selected loan requests
        for loan_request_id in loan_request_ids_sample[0 : n // 3]:
            loan_requests[loan_request_id] = services.loan.cancel_loan_request(
                db=session,
                loan_request_id=loan_request_id,
            )

        # reject 1/3 of the selected loan requests
        for loan_request_id in loan_request_ids_sample[n // 3 : 2 * n // 3]:
            loan_requests[loan_request_id] = services.loan.reject_loan_request(
                db=session,
                loan_request_id=loan_request_id,
            )

        # accept 1/3 of the selected loan requests
        for loan_request_id in loan_request_ids_sample[2 * n // 3 :]:
            loan_requests[loan_request_id] = services.loan.accept_loan_request(
                db=session,
                loan_request_id=loan_request_id,
            )

        # execute one loan request
        executed_loan_request_id = loan_request_ids_sample[-1]
        services.loan.execute_loan_request(
            db=session,
            loan_request_id=executed_loan_request_id,
        )

        # read updated loan request
        loan_requests[executed_loan_request_id] = services.loan.get_loan_request(
            db=session,
            loan_request_id=loan_request_id,
        )

        return list(loan_requests.values())
