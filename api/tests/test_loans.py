from fastapi.testclient import TestClient

from .conftest import ItemData


def test_request_item(
    client0: TestClient,
    items_data: list[ItemData],
    items: list[int],
):
    """Check that an item can be requested."""

    item_index = 1
    item_id = items[item_index]

    # ensure chosen item is not owned by user making the request
    assert items_data[item_index]["owner_id"] != 0

    # request item
    resp = client0.post(f"/v1/items/{item_id}/request")

    read = resp.json()
    print(read)
    resp.raise_for_status()


def test_request_appears_in_borrowings_requests(
    client0: TestClient,
    items_data: list[ItemData],
    items: list[int],
    users: list[int],
):
    item_index = 1
    item_id = items[1]

    # ensure chosen item is not owned by user making the request
    assert items_data[item_index]["owner_id"] != 0

    # request item
    resp = client0.post(f"/v1/items/{item_id}/request")
    resp.raise_for_status()

    # check request added to borrowings list
    resp = client0.get("/v1/me/borrowings/requests")
    resp.raise_for_status()
    loan_request = resp.json()[0]

    assert loan_request["item"]["id"] == item_id
    assert loan_request["borrower"]["id"] == users[0]
