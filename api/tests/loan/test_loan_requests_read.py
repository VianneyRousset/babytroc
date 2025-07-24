from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.enums import LoanRequestState
from app.schemas.item.read import ItemRead
from app.schemas.loan.read import LoanRequestRead
from app.utils.pagination import iter_chunks, iter_paginated_endpoint


@pytest.mark.usefixtures("many_loan_requests_for_alice_items")
class TestLoanRequestRead:
    """Tests loan requests read."""

    @pytest.mark.parametrize("count", [None, 16, 7])
    @pytest.mark.parametrize("active", [None, True, False])
    def test_client_borrowing_requests_read_pages(
        self,
        bob_client: TestClient,
        many_loan_requests_for_alice_items: list[LoanRequestRead],
        count: int | None,
        active: bool | None,
    ):
        params: dict[str, Any] = {
            **({"n": count} if count is not None else {}),
            **({"a": active} if active is not None else {}),
        }

        all_expected_loan_requests = sorted(
            [
                loan_request
                for loan_request in many_loan_requests_for_alice_items
                if self.check_loan_request_state_active(loan_request.state, active)
            ],
            key=lambda loan_request: loan_request.id,
        )

        assert len(all_expected_loan_requests) >= 5, "poor data for testing"

        for loan_requests, expected_loan_requests in zip(
            iter_paginated_endpoint(
                url="/v1/me/borrowings/requests",
                client=bob_client,
                params=params,
            ),
            iter_chunks(
                all_expected_loan_requests[::-1],
                count=count or 32,
                append_empty=True,
            ),
            strict=True,
        ):
            assert [loan_request["id"] for loan_request in loan_requests] == [
                loan_request.id for loan_request in expected_loan_requests
            ]

    @pytest.mark.parametrize("count", [None, 16, 7])
    @pytest.mark.parametrize("active", [None, True, False])
    def test_client_loan_requests_read_pages(
        self,
        alice_client: TestClient,
        many_loan_requests_for_alice_items: list[LoanRequestRead],
        count: int | None,
        active: bool | None,
    ):
        params: dict[str, Any] = {
            **({"n": count} if count is not None else {}),
            **({"a": active} if active is not None else {}),
        }

        all_expected_loan_requests = sorted(
            [
                loan_request
                for loan_request in many_loan_requests_for_alice_items
                if self.check_loan_request_state_active(loan_request.state, active)
            ],
            key=lambda loan_request: loan_request.id,
        )

        assert len(all_expected_loan_requests) >= 5, "poor data for testing"

        for loan_requests, expected_loan_requests in zip(
            iter_paginated_endpoint(
                url="/v1/me/loans/requests",
                client=alice_client,
                params=params,
            ),
            iter_chunks(
                all_expected_loan_requests[::-1],
                count=count or 32,
                append_empty=True,
            ),
            strict=True,
        ):
            assert [loan_request["id"] for loan_request in loan_requests] == [
                loan_request.id for loan_request in expected_loan_requests
            ]

    @pytest.mark.parametrize("count", [None, 16, 7])
    @pytest.mark.parametrize("active", [None, True, False])
    def test_item_loan_requests_read_pages(
        self,
        alice_special_item: ItemRead,
        alice_client: TestClient,
        many_loan_requests_for_alice_special_item: list[LoanRequestRead],
        count: int | None,
        active: bool | None,
    ):
        params: dict[str, Any] = {
            **({"n": count} if count is not None else {}),
            **({"a": active} if active is not None else {}),
        }

        all_expected_loan_requests = sorted(
            [
                loan_request
                for loan_request in many_loan_requests_for_alice_special_item
                if self.check_loan_request_state_active(loan_request.state, active)
            ],
            key=lambda loan_request: loan_request.id,
        )

        assert len(all_expected_loan_requests) >= 5, "poor data for testing"

        for loan_requests, expected_loan_requests in zip(
            iter_paginated_endpoint(
                url=f"/v1/me/items/{alice_special_item.id}/loans/requests",
                client=alice_client,
                params=params,
            ),
            iter_chunks(
                all_expected_loan_requests[::-1],
                count=count or 32,
                append_empty=True,
            ),
            strict=True,
        ):
            assert [loan_request["id"] for loan_request in loan_requests] == [
                loan_request.id for loan_request in expected_loan_requests
            ]

    @staticmethod
    def check_loan_request_state_active(
        state: LoanRequestState,
        active: bool | None,
    ) -> bool:
        active_states = {LoanRequestState.pending, LoanRequestState.accepted}

        if active is None:
            return True

        if active:
            return state in active_states

        return state not in active_states
