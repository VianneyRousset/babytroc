from fastapi.testclient import TestClient


def test_request_item(
    client: TestClient,
    items: list[int],
):
    item_id = items[1]

    # request item
    resp = client.post(f"/v1/items/{item_id}/request")

    read = resp.json()
    print(read)
    resp.raise_for_status()


def test_request_appears_in_borrowings_requests(
    client: TestClient,
    items: list[int],
    items_data: list[dict],
    users: list[int],
):
    item_id = items[1]

    # request item
    resp = client.post(f"/v1/items/{item_id}/request")
    resp.raise_for_status()

    # check request added to list
    resp = client.get("/v1/me/borrowings/requests")
    resp.raise_for_status()
    loan_request = resp.json()[0]

    assert loan_request["item"]["id"] == item_id
    assert loan_request["borrower"]["id"] == users[0]
