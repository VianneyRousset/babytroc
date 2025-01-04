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


def test_created_item_can_be_read(client: TestClient, user_alice: int):
    # create image
    image_name = post_image(client)

    # create item
    resp = client.post(
        "/v1/me/items",
        json=ITEM | {"images": [image_name]},
    )
    resp.raise_for_status()
    added = resp.json()
    item_id = added["id"]

    # get item by id from global list
    resp = client.get(f"/v1/items/{item_id}")
    resp.raise_for_status()
    read = resp.json()

    assert read["name"] == ITEM["name"]
    assert read["description"] == ITEM["description"]
    assert read["targeted_age_months"] == ITEM["targeted_age_months"]
    assert read["owner_id"] == user_alice

    # get item by id from client list
    resp = client.get(f"/v1/me/items/{item_id}")
    resp.raise_for_status()
    read = resp.json()

    assert read["name"] == ITEM["name"]
    assert read["description"] == ITEM["description"]
    assert read["targeted_age_months"] == ITEM["targeted_age_months"]
    assert read["owner_id"] == user_alice


def test_created_item_can_be_updated(client: TestClient, user_alice: int):
    # create image
    image_name = post_image(client)

    # create item
    resp = client.post(
        "/v1/me/items",
        json=ITEM | {"images": [image_name]},
    )
    resp.raise_for_status()
    added = resp.json()
    item_id = added["id"]

    # create item
    resp = client.post(
        f"/v1/me/items/{item_id}",
        json={"name": "forest"},
    )
    resp.raise_for_status()

    # get item by id from global list
    resp = client.get(f"/v1/items/{item_id}")
    resp.raise_for_status()
    read = resp.json()

    assert read["name"] == "forest"
    assert read["description"] == ITEM["description"]
    assert read["targeted_age_months"] == ITEM["targeted_age_months"]
    assert read["owner_id"] == user_alice


def test_created_item_can_be_deleted(client: TestClient, user_alice: int):
    # create image
    image_name = post_image(client)

    # create item
    resp = client.post(
        "/v1/me/items",
        json=ITEM | {"images": [image_name]},
    )
    resp.raise_for_status()
    added = resp.json()
    item_id = added["id"]

    # get item by id
    resp = client.delete(f"/v1/me/items/{item_id}")
    resp.raise_for_status()

    # get global items list
    resp = client.get("/v1/items")
    resp.raise_for_status()
    items = resp.json()
    assert items == []


def test_created_item_shows_up_in_global_list(client: TestClient, user_alice: int):
    # create image
    image_name = post_image(client)

    # create item
    resp = client.post(
        "/v1/me/items",
        json=ITEM | {"images": [image_name]},
    )
    resp.raise_for_status()

    # get global items list
    resp = client.get("/v1/items")
    resp.raise_for_status()
    items = resp.json()

    assert items[0]["name"] == ITEM["name"]
    assert items[0]["owner_id"] == user_alice


def test_created_item_shows_up_in_client_list(client: TestClient, user_alice: int):
    # create image
    image_name = post_image(client)

    # create item
    resp = client.post(
        "/v1/me/items",
        json=ITEM | {"images": [image_name]},
    )
    resp.raise_for_status()

    # get client items list
    resp = client.get("/v1/me/items")
    resp.raise_for_status()
    items = resp.json()

    assert items[0]["name"] == ITEM["name"]
    assert items[0]["owner_id"] == user_alice
