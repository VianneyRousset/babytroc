from itertools import zip_longest
from typing import Any
from urllib.parse import parse_qsl, urlparse

import pytest
from fastapi.testclient import TestClient

from app.enums import LoanRequestState
from app.schemas.item.read import ItemRead
from app.schemas.loan.read import LoanRequestRead


@pytest.mark.usefixtures("many_loan_requests_for_alice_items")
class TestLoanRequestRead:
    """Tests loan requests read."""

    @pytest.mark.parametrize("count", [None, 16, 7])
    @pytest.mark.parametrize("active", [None, True, False])
    def test_client_borrowing_requests_read_pages(
        self,
        alice_new_item: ItemRead,
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

        for i, expected_loan_requests in enumerate(
            self.grouper(all_expected_loan_requests[::-1], count or 32)
        ):
            print(f"page #{i} cursor:", params)

            # get next page
            resp = bob_client.get(
                url="/v1/me/borrowings/requests",
                params=params,
            )
            print(resp.json())
            resp.raise_for_status()
            params = dict(parse_qsl(urlparse(resp.links["next"]["url"]).query))

            assert [loan_request["id"] for loan_request in resp.json()] == [
                loan_request.id for loan_request in expected_loan_requests
            ]

        # ensure not loan requests are left
        resp = bob_client.get(
            url="/v1/me/borrowings/requests",
            params=params,
        )
        print(resp.json())
        resp.raise_for_status()
        assert resp.json() == []

    @pytest.mark.parametrize("count", [None, 16, 7])
    @pytest.mark.parametrize("active", [None, True, False])
    def test_client_loan_requests_read_pages(
        self,
        alice_new_item: ItemRead,
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

        for i, expected_loan_requests in enumerate(
            self.grouper(all_expected_loan_requests[::-1], count or 32)
        ):
            print(f"page #{i} cursor:", params)

            # get next page
            resp = alice_client.get(
                url="/v1/me/loans/requests",
                params=params,
            )
            print(resp.json())
            resp.raise_for_status()
            params = dict(parse_qsl(urlparse(resp.links["next"]["url"]).query))

            assert [loan_request["id"] for loan_request in resp.json()] == [
                loan_request.id for loan_request in expected_loan_requests
            ]

        # ensure not loan requests are left
        resp = alice_client.get(
            url="/v1/me/loans/requests",
            params=params,
        )
        print(resp.json())
        resp.raise_for_status()
        assert resp.json() == []

    @staticmethod
    def grouper(iterable, count):
        "grouper('abcdefgh', 3) --> ('a','b','c'), ('d','e','f'), ('g','h')"
        groups = zip_longest(*[iter(iterable)] * count)
        return [filter(lambda v: v is not None, group) for group in groups]

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
