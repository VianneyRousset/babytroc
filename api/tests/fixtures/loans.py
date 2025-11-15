import random

import pytest
from sqlalchemy.orm import sessionmaker

from app import services
from app.schemas.item.read import ItemRead
from app.schemas.loan.query import LoanRequestReadQueryFilter
from app.schemas.loan.read import LoanRead, LoanRequestRead
from app.schemas.user.private import UserPrivateRead


@pytest.fixture
def bob_new_loan_request_for_alice_new_item(
    database_sessionmaker: sessionmaker,
    alice: UserPrivateRead,
    alice_new_item: ItemRead,
    bob: UserPrivateRead,
) -> LoanRequestRead:
    """A new loan request made by Bob for the new item of Alice.

    fixture scope: function.
    """

    with database_sessionmaker.begin() as session:
        return services.loan.create_loan_request(
            db=session,
            item_id=alice_new_item.id,
            borrower_id=bob.id,
        )


@pytest.fixture
def bob_new_loan_request_for_alice_special_item(
    database_sessionmaker: sessionmaker,
    alice: UserPrivateRead,
    alice_special_item: ItemRead,
    bob: UserPrivateRead,
) -> LoanRequestRead:
    """A new loan request made by Bob for the special item of Alice.

    fixture scope: function.
    """

    with database_sessionmaker.begin() as session:
        return services.loan.create_loan_request(
            db=session,
            item_id=alice_special_item.id,
            borrower_id=bob.id,
        )


@pytest.fixture
def carol_new_loan_request_for_alice_new_item(
    database_sessionmaker: sessionmaker,
    alice: UserPrivateRead,
    alice_new_item: ItemRead,
    carol: UserPrivateRead,
) -> LoanRequestRead:
    """A new loan request made by Carol for the new item of Alice.

    fixture scope: function.
    """

    with database_sessionmaker.begin() as session:
        return services.loan.create_loan_request(
            db=session,
            item_id=alice_new_item.id,
            borrower_id=carol.id,
        )


@pytest.fixture
def bob_new_loan_of_alice_new_item(
    database_sessionmaker: sessionmaker,
    alice: UserPrivateRead,
    alice_new_item: ItemRead,
    bob: UserPrivateRead,
    bob_new_loan_request_for_alice_new_item: LoanRequestRead,
) -> LoanRead:
    """A new loan request made by Bob for the new alice of Alice.

    fixture scope: function.
    """

    with database_sessionmaker.begin() as session:
        # execute loan request
        return services.loan.execute_loan_request(
            db=session,
            loan_request_id=bob_new_loan_request_for_alice_new_item.id,
            query_filter=LoanRequestReadQueryFilter(
                owner_id=alice.id,
                borrower_id=bob.id,
            ),
            check_state=False,
        )


@pytest.fixture(scope="class")
def many_loan_requests_for_alice_items(
    database_sessionmaker: sessionmaker,
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

    with database_sessionmaker.begin() as session:
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
    database_sessionmaker: sessionmaker,
    many_users: list[UserPrivateRead],
    alice: UserPrivateRead,
    alice_special_item: ItemRead,
) -> list[LoanRequestRead]:
    """Loan requests from many users for Alice new item.

    ~90% of the many users requests Alice's special item.
    ~25% of those loan requests are cancelled
    ~25% of those loan requests are rejected
    ~25% of those loan requests are accepted
    ~25% of those loan requests are still pending

    1 loan request is executed into a loan
    """

    random.seed(0x50E6)

    # select 90% of all the many users that will request Alice new item
    requesters = random.sample(many_users, k=round(0.9 * len(many_users)))

    with database_sessionmaker.begin() as session:
        # create loan requests (shuffled)
        loan_requests = [
            services.loan.create_loan_request(
                db=session,
                item_id=alice_special_item.id,
                borrower_id=requester.id,
            )
            for requester in requesters
        ]

        n = len(loan_requests)

        # cancel 1/4 of the selected loan requests
        cancelled_loan_requests = [
            services.loan.cancel_loan_request(
                db=session,
                loan_request_id=loan_request.id,
            )
            for loan_request in loan_requests[0 : n // 4]
        ]
        if not cancelled_loan_requests:
            msg = "At least one loan request should be cancelled"
            raise ValueError(msg)

        # reject 1/4 of the selected loan requests
        rejected_loan_requests = [
            services.loan.reject_loan_request(
                db=session,
                loan_request_id=loan_request.id,
            )
            for loan_request in loan_requests[n // 4 : 2 * n // 4]
        ]
        if not rejected_loan_requests:
            msg = "At least one loan request should be rejected"
            raise ValueError(msg)

        # accept 1/4 of the selected loan requests
        accepted_loan_requests = [
            services.loan.accept_loan_request(
                db=session,
                loan_request_id=loan_request.id,
            )
            for loan_request in loan_requests[2 * n // 4 : 3 * n // 4]
        ]
        if not accepted_loan_requests:
            msg = "At least one loan request should be accepted"
            raise ValueError(msg)

        # execute one loan request
        executed_loan_request_id = loan_requests[3 * n // 4].id
        services.loan.execute_loan_request(
            db=session,
            loan_request_id=executed_loan_request_id,
        )
        # read updated loan request
        executed_loan_request = services.loan.get_loan_request(
            db=session,
            loan_request_id=executed_loan_request_id,
        )

        # leave the remaining loan requests pending
        pending_loan_requests = loan_requests[3 * n // 4 + 1 :]

        return random.sample(
            [
                *cancelled_loan_requests,
                *rejected_loan_requests,
                *accepted_loan_requests,
                *pending_loan_requests,
                executed_loan_request,
            ],
            k=n,
        )


@pytest.fixture(scope="class")
def alice_many_loans(
    database_sessionmaker: sessionmaker,
    alice_many_items: list[ItemRead],
    alice: UserPrivateRead,
    bob: UserPrivateRead,
    carole: UserPrivateRead,
) -> list[LoanRead]:
    """Many loans made by Alice.

    90% of the many items owned by Alice are loaned to either Bob or Carole.
    Among those loans, 70% of them are ended.
    Among those ended loans, 50% of the loaned items are loaned again.
    Among those new loans, 50% of the loaned are ended again.
    """

    random.seed(0x50E6)

    # select 90% of all the many users that will request Alice new item
    items = random.sample(alice_many_items, k=round(0.9 * len(alice_many_items)))

    with database_sessionmaker.begin() as session:
        # create loan requests
        loan_requests = [
            services.loan.create_loan_request(
                db=session,
                item_id=item.id,
                borrower_id=requester.id,
            )
            for item, requester in zip(
                items,
                random.choices([bob, carole], k=len(items)),
                strict=True,
            )
        ]

        # accept and execute all loan requests
        loans = [
            services.loan.execute_loan_request(
                db=session,
                loan_request_id=services.loan.accept_loan_request(
                    db=session,
                    loan_request_id=loan_request.id,
                ).id,
            )
            for loan_request in loan_requests
        ]

        # end 70% of the loans
        ended_loans = [
            services.loan.end_loan(
                db=session,
                loan_id=loan.id,
            )
            for loan in loans
        ]

        # request 50% of the ended loans
        loan_requests = [
            services.loan.create_loan_request(
                db=session,
                item_id=loan.item.id,
                borrower_id=requester.id,
            )
            for loan, requester in zip(
                loans,
                random.choices([bob, carole], k=len(ended_loans)),
                strict=True,
            )
        ]

        # accept and execute all new loan requests
        restarted_loans = [
            services.loan.execute_loan_request(
                db=session,
                loan_request_id=services.loan.accept_loan_request(
                    db=session,
                    loan_request_id=loan_request.id,
                ).id,
            )
            for loan_request in loan_requests
        ]

        # end 50% of those restarted loans
        ended_twice_loans = [
            services.loan.end_loan(
                db=session,
                loan_id=loan.id,
            )
            for loan in restarted_loans[: len(restarted_loans) // 2]
        ]

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
