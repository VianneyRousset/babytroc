from fastapi.testclient import TestClient

ITEM = {
    "name": "candle",
    "description": "dwell into a flowerbed",
    "targeted_age_months": [4, 10],
    "regions": [],
}


def post_image(client: TestClient) -> str:
    # basic PBM image
    image = "\n".join(
        [
            "P1",
            "3 3",
            "101",
            "101",
            "010",
        ]
    )

    resp = client.post("/v1/images", files={"file": image})
    resp.raise_for_status()
    added = resp.json()

    return added["name"]


def test_request_item(client: TestClient, user_bob: int, item_candle: int):
    # request item
    resp = client.post(f"/v1/items/{item_candle}/request")

    read = resp.json()
    print(read)
    resp.raise_for_status()


def test_request_appears_in_borrowings_requests(
    client: TestClient, user_bob: int, item_candle: int
):
    # request item
    resp = client.post(f"/v1/items/{item_candle}/request")
    resp.raise_for_status()

    # check request added to list
    resp = client.get("/v1/me/borrowings/requests")
    resp.raise_for_status()
    loan_request = resp.json()[0]

    assert loan_request["item"]["id"] == item_candle
    assert loan_request["borrower"]["id"] == user_bob
