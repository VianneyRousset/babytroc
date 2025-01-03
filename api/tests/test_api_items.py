from fastapi.testclient import TestClient


ITEM = {
    "name": "candle",
    "description": "dwell into a flowerbed",
    "targeted_age_months": [None, None],
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


def test_created_item_can_be_read(client: TestClient, database_user: int):
    image_name = post_image(client)

    resp = client.post(
        "/v1/me/items",
        json=ITEM | {"images": [image_name]},
    )
    resp.raise_for_status()
    added = resp.json()
    item_id = added["id"]

    resp = client.get(f"/v1/items/{item_id}")
    resp.raise_for_status()
    read = resp.json()

    assert read["name"] == ITEM["name"]
    assert read["description"] == ITEM["description"]
    assert read["owner_id"] == database_user


def test_created_item_shows_up_in_global_list(client: TestClient, database_user: int):
    image_name = post_image(client)

    resp = client.post(
        "/v1/me/items",
        json=ITEM | {"images": [image_name]},
    )
    resp.raise_for_status()

    resp = client.get("/v1/items")
    resp.raise_for_status()
    items = resp.json()

    assert items[0]["name"] == ITEM["name"]
    assert items[0]["owner_id"] == database_user
