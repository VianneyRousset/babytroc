import pytest
from fastapi.testclient import TestClient

from app.schemas.item.read import ItemRead


@pytest.mark.usefixtures("many_loan_requests_for_alice_items")
class TestLoanRequestRead:
    """Tests loan requests read."""

    def test_can_request_item(
        self,
        alice_new_item: ItemRead,
        alice_client: TestClient,
        bob_client: TestClient,
    ):
        """Check that a loan request can be created and appears in various lists."""

        # request item
        resp = bob_client.post(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # check loan request appears in borrower's borrowings requests
        resp = bob_client.get("/v1/me/borrowings/requests")
        print(resp.text)
        resp.raise_for_status()
        assert request["id"] in {req["id"] for req in resp.json()}
        bob_client.get(f"/v1/me/borrowings/requests/{request['id']}").raise_for_status()

        # check loan request appears in item's borrowings requests
        resp = alice_client.get(f"/v1/me/items/{alice_new_item.id}/requests")
        print(resp.text)
        resp.raise_for_status()
        assert request["id"] in {item["id"] for item in resp.json()}
        alice_client.get(
            f"/v1/me/items/{alice_new_item.id}/requests/{request['id']}"
        ).raise_for_status()

    def test_cannot_request_item_twice(
        self,
        alice_new_item: ItemRead,
        alice_client: TestClient,
        bob_client: TestClient,
    ):
        """Check that a client cannot request the same item twice."""

        # request item
        resp = bob_client.post(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        resp.raise_for_status()

        # request it again
        resp = bob_client.post(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        assert not resp.is_success

    def test_cannot_request_own_item(
        self,
        alice_new_item: ItemRead,
        alice_client: TestClient,
    ):
        """Check that a client cannot request an item owned by the latter."""

        resp = alice_client.post(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        assert not resp.is_success

    def test_can_request_after_cancelled(
        self,
        alice_new_item: ItemRead,
        bob_client: TestClient,
    ):
        """Check an item can be requested again after cancelled previous request."""

        # request item
        resp = bob_client.post(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        resp.raise_for_status()

        # cancel loan request
        bob_client.delete(f"/v1/items/{alice_new_item.id}/request").raise_for_status()

        # request item
        resp = bob_client.post(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        resp.raise_for_status()
