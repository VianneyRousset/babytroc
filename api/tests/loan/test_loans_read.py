from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient

from app.domains.loan.schemas.read import LoanRead
from app.utils.pagination import iter_chunks, iter_paginated_endpoint
from tests.utils import azip


class TestLoansRead:
    """Tests loans read."""

    @pytest.mark.parametrize("count", [None, 16, 7])
    @pytest.mark.parametrize("active", [None, True, False])
    async def test_client_loans_read_pages(
        self,
        alice_client: AsyncClient,
        alice_many_loans: list[LoanRead],
        count: int | None,
        active: bool | None,
    ):
        params: dict[str, Any] = {
            **({"n": count} if count is not None else {}),
            **({"a": active} if active is not None else {}),
        }

        all_expected_loans = sorted(
            [
                loan
                for loan in alice_many_loans
                if self.check_loan_state_active(loan.active, active)
            ],
            key=lambda loan: loan.id,
        )

        assert len(all_expected_loans) >= 5, "poor data for testing"

        async for loans, expected_loans in azip(
            iter_paginated_endpoint(
                url="/api/v1/me/loans",
                client=alice_client,
                params=params,
            ),
            iter_chunks(
                all_expected_loans[::-1],
                count=count or 32,
                append_empty=True,
            ),
            strict=True,
        ):
            assert [loan["id"] for loan in loans] == [
                loan.id for loan in expected_loans
            ]

    # TODO add test read /items/{item_id}/loans

    @staticmethod
    def check_loan_state_active(
        state: bool,
        active: bool | None,
    ) -> bool:
        if active is None:
            return True

        return state == active


class TestBorrowingsListRead:
    """Test borrowing list endpoint with active filter."""

    @pytest.mark.parametrize("count", [None, 16, 7])
    @pytest.mark.parametrize("active", [None, True, False])
    async def test_client_borrowings_read_pages(
        self,
        bob_client: AsyncClient,
        alice_many_loans: list[LoanRead],
        count: int | None,
        active: bool | None,
    ):
        params: dict[str, Any] = {
            **({"n": count} if count is not None else {}),
            **({"a": active} if active is not None else {}),
        }

        all_expected_loans = sorted(
            [
                loan
                for loan in alice_many_loans
                if loan.borrower.name == "bob"
                and self.check_loan_state_active(loan.active, active)
            ],
            key=lambda loan: loan.id,
        )

        assert len(all_expected_loans) >= 5, "poor data for testing"

        async for loans, expected_loans in azip(
            iter_paginated_endpoint(
                url="/api/v1/me/borrowings",
                client=bob_client,
                params=params,
            ),
            iter_chunks(
                all_expected_loans[::-1],
                count=count or 32,
                append_empty=True,
            ),
            strict=True,
        ):
            assert [loan["id"] for loan in loans] == [
                loan.id for loan in expected_loans
            ]

    @staticmethod
    def check_loan_state_active(
        state: bool,
        active: bool | None,
    ) -> bool:
        if active is None:
            return True

        return state == active


class TestBorrowingRead:
    """Test borrowing read endpoints."""

    async def test_get_single_borrowing(
        self,
        bob_client: AsyncClient,
        alice_many_loans: list[LoanRead],
    ):
        """Borrower can fetch their own borrowing."""
        bob_loan = next(
            loan for loan in alice_many_loans if loan.borrower.name == "bob"
        )
        resp = await bob_client.get(f"/api/v1/me/borrowings/{bob_loan.id}")
        resp.raise_for_status()
        assert resp.json()["id"] == bob_loan.id

    async def test_get_single_borrowing_not_borrower(
        self,
        carol_client: AsyncClient,
        bob_client: AsyncClient,
        alice_many_loans: list[LoanRead],
    ):
        """Non-borrower cannot fetch someone else's borrowing."""
        # find a loan where bob is the borrower
        bob_loan = next(
            (loan for loan in alice_many_loans if loan.borrower.name == "bob"),
            None,
        )
        if bob_loan is None:
            pytest.skip("No loan with bob as borrower found")

        # carol should not be able to access bob's borrowing
        resp = await carol_client.get(
            f"/api/v1/me/borrowings/{bob_loan.id}"
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
