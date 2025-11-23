from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.schemas.loan.read import LoanRead
from app.utils.pagination import iter_chunks, iter_paginated_endpoint


class TestLoansRead:
    """Tests loans read."""

    @pytest.mark.parametrize("count", [None, 16, 7])
    @pytest.mark.parametrize("active", [None, True, False])
    def test_client_loans_read_pages(
        self,
        alice_client: TestClient,
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

        for loans, expected_loans in zip(
            iter_paginated_endpoint(
                url="/v1/me/loans",
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
