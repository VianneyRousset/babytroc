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
        # accept loan request

        return services.loan.execute_loan_request(
            db=session,
            loan_request_id=bob_new_loan_request_for_alice_new_item.id,
            query_filter=LoanRequestQueryFilter(
                owner_id=alice.id,
                borrower_id=bob.id,
            ),
            force=True,
        )
