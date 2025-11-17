from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.schemas.item.read import ItemRead
from app.schemas.loan.read import LoanRead, LoanRequestRead
from app.schemas.user.read import UserRead


class TestLoanCreate:
    """Tests loans create."""

    def test_execute_loan_request(
        self,
        bob_accepted_loan_request_for_alice_special_item: LoanRequestRead,
        alice: UserRead,
        bob: UserRead,
        alice_client: TestClient,
        bob_client: TestClient,
        carol_client: TestClient,
        alice_special_item: ItemRead,
    ):
        """Check an accepted loan request can be executed into a loan.
        - Check only Bob can execute the loan request
        """

        loan_request_id = bob_accepted_loan_request_for_alice_special_item.id

        # check only Bob can execute the loan request
        resp = alice_client.post(
            f"/v1/me/borrowings/requests/{loan_request_id}/execute"
        )
        assert resp.is_error
        resp = carol_client.post(
            f"/v1/me/borrowings/requests/{loan_request_id}/execute"
        )
        assert resp.is_error

        # accept loan request
        resp = bob_client.post(f"/v1/me/borrowings/requests/{loan_request_id}/execute")
        print(resp.text)
        resp.raise_for_status()
        loan = LoanRead.model_validate(resp.json())

        # check item
        assert loan.item.id == alice_special_item.id

        # check owner and borrower
        assert loan.owner.id == alice.id
        assert loan.borrower.id == bob.id

        # check chat
        assert loan.chat_id == bob_accepted_loan_request_for_alice_special_item.chat_id

        # check during and active
        start, stop = loan.during
        assert start is not None
        assert abs(start - datetime.now(UTC)) < timedelta(minutes=5)
        assert stop is None
        assert loan.active
