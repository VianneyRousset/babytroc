import pytest
from fastapi import status
from httpx import AsyncClient

from app.schemas.item.read import ItemRead


@pytest.mark.usefixtures("items")
class TestLoanRequestCreate:
    """Tests loan requests create."""

    async def test_can_request_item(
        self,
        alice_new_item: ItemRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
    ):
        """Check that a loan request can be created and appears in various lists."""

        # check Bob (borrower) sees the item as not requested
        resp = await bob_client.get(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}"
        )
        print(resp.text)
        resp.raise_for_status()
        item = resp.json()
        assert item["active_loan_request"] is None

        # Bob requests Alice's item
        resp = await bob_client.post(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}/request"
        )
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # check loan request appears in Bob's borrowings requests
        resp = await bob_client.get("https://babytroc.ch/api/v1/me/borrowings/requests")
        print(resp.text)
        resp.raise_for_status()
        assert request["id"] in {req["id"] for req in resp.json()}
        resp = await bob_client.get(
            f"https://babytroc.ch/api/v1/me/borrowings/requests/{request['id']}"
        )
        resp.raise_for_status()

        # check Bob (borrower) sees the item as requested
        resp = await bob_client.get(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}"
        )
        print(resp.text)
        resp.raise_for_status()
        item = resp.json()
        assert item["active_loan_request"]["id"] == request["id"]

        # check Bob (owner) does not see the item as requested
        resp = await alice_client.get(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}"
        )
        print(resp.text)
        resp.raise_for_status()
        item = resp.json()
        assert item["active_loan_request"] is None

        # check loan request appears in item's borrowings requests
        resp = await alice_client.get(
            f"https://babytroc.ch/api/v1/me/items/{alice_new_item.id}/requests"
        )
        print(resp.text)
        resp.raise_for_status()
        assert request["id"] in {item["id"] for item in resp.json()}
        resp = await alice_client.get(
            f"https://babytroc.ch/api/v1/me/items/{alice_new_item.id}/requests/{request['id']}"
        )
        resp.raise_for_status()


@pytest.mark.usefixtures("items")
class TestLoanRequestCreateRequestAfterCancelled:
    """Check an item can be requested again after cancelled previous request."""

    async def test_can_request_after_cancelled(
        self,
        alice_new_item: ItemRead,
        bob_client: AsyncClient,
    ):
        """Check an item can be requested again after cancelled previous request."""

        # request item
        resp = await bob_client.post(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}/request"
        )
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # check Bob (borrower) sees the item as requested
        resp = await bob_client.get(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}"
        )
        print(resp.text)
        resp.raise_for_status()
        item = resp.json()
        assert item["active_loan_request"]["id"] == request["id"]

        # cancel loan request
        resp = await bob_client.delete(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}/request"
        )
        resp.raise_for_status()

        # check Bob (borrower) does not see the item as requested anymore
        resp = await bob_client.get(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}"
        )
        print(resp.text)
        resp.raise_for_status()
        item = resp.json()
        assert item["active_loan_request"] is None, (
            "item should'nt have an active loan request anymore"
        )

        # request item
        resp = await bob_client.post(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}/request"
        )
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # check Bob (borrower) sees the item as requested
        resp = await bob_client.get(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}"
        )
        print(resp.text)
        resp.raise_for_status()
        item = resp.json()
        assert item["active_loan_request"]["id"] == request["id"]


@pytest.mark.usefixtures("items")
class TestLoanRequestCreateInvalidRequestTwice:
    """Check that a client cannot request the same item twice."""

    async def test_cannot_request_item_twice(
        self,
        alice_new_item: ItemRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
    ):
        """Check that a client cannot request the same item twice."""

        # request item
        resp = await bob_client.post(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}/request"
        )
        print(resp.text)
        resp.raise_for_status()

        # request it again
        resp = await bob_client.post(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}/request"
        )
        print(resp.text)
        assert resp.is_error
        assert resp.status_code == status.HTTP_409_CONFLICT


@pytest.mark.usefixtures("items")
class TestLoanRequestCreateInvalidRequestOwnItem:
    """Check that a client cannot request an item owned by the latter."""

    async def test_cannot_request_own_item(
        self,
        alice_new_item: ItemRead,
        alice_client: AsyncClient,
    ):
        """Check that a client cannot request an item owned by the latter."""

        resp = await alice_client.post(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}/request"
        )
        print(resp.text)
        assert resp.is_error
