from datetime import UTC, datetime, timedelta

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.schemas.item.read import ItemRead
from app.schemas.loan.read import LoanRead, LoanRequestRead
from app.schemas.user.read import UserRead


class TestLoanCreate:
    """Tests loan requests create."""

    def test_execute_loan_request(
        self,
        bob_accepted_loan_request_for_alice_special_item: LoanRequestRead,
        alice: UserRead,
        bob: UserRead,
        bob_client: TestClient,
        alice_special_item: ItemRead,
    ):
        """Check an accepted loan request can be executed into a loan."""

        loan_request_id = bob_accepted_loan_request_for_alice_special_item.id

        # accept loan request
        resp = bob_client.post(f"/v1/me/borrowings/requests/{loan_request_id}/execute")
        print(resp.text)
        resp.raise_for_status()
        loan = LoanRead.model_validate(resp.json())

        # check item
        assert loan.item.id == bob_accepted_loan_request_for_alice_special_item.item.id

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
