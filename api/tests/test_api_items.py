from fastapi import status
from fastapi.testclient import TestClient


def test_created_item_can_be_read(
    client: TestClient,
    users: list[int],
    items_data: list[dict],
):
    item_data = items_data[0]

    # create item
    resp = client.post(
        "/v1/me/items",
        json={k: v for k, v in item_data.items() if k != "owner_id"},
    )
    print(resp.text)
    resp.raise_for_status()
    added = resp.json()
    item_id = added["id"]

    # get item by id from global list
    resp = client.get(f"/v1/items/{item_id}")
    print(resp.text)
    resp.raise_for_status()
    read = resp.json()

    assert read["name"] == item_data["name"]
    assert read["description"] == item_data["description"]
    assert read["targeted_age_months"] == item_data["targeted_age_months"]
    assert read["owner_id"] == item_data["owner_id"]

    # get item by id from client list
    resp = client.get(f"/v1/me/items/{item_id}")
    print(resp.text)
    resp.raise_for_status()
    read = resp.json()

    assert read["name"] == item_data["name"]
    assert read["description"] == item_data["description"]
    assert read["targeted_age_months"] == item_data["targeted_age_months"]
    assert read["owner_id"] == item_data["owner_id"]


def test_created_item_can_be_updated(
    client: TestClient,
    users: list[int],
    items_data: list[dict],
    items: list[int],
):
    item_data = items_data[0]
    item_id = items[0]

    # update item name
    resp = client.post(
        f"/v1/me/items/{item_id}",
        json={"name": "forest"},
    )
    print(resp.text)
    resp.raise_for_status()

    # get item by id from global list
    resp = client.get(f"/v1/items/{item_id}")
    print(resp.text)
    resp.raise_for_status()
    read = resp.json()

    assert read["name"] == "forest"
    assert read["description"] == item_data["description"]
    assert read["targeted_age_months"] == item_data["targeted_age_months"]
    assert read["owner_id"] == item_data["owner_id"]


def test_created_item_can_be_deleted(
    client: TestClient,
    users: list[int],
    items: list[int],
):
    item_id = items[0]

    # check item exists
    resp = client.get(f"/v1/items/{item_id}")
    print(resp.text)
    resp.raise_for_status()

    # delete item by id
    resp = client.delete(f"/v1/me/items/{item_id}")
    print(resp.text)
    resp.raise_for_status()

    # check item does not exists
    resp = client.get(f"/v1/items/{item_id}")
    print(resp.text)
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_created_item_shows_up_in_global_list(
    client: TestClient,
    users: list[int],
    items_data: list[dict],
):
    item_data = items_data[0]

    # create item
    resp = client.post(
        "/v1/me/items",
        json={k: v for k, v in item_data.items() if k != "owner_id"},
    )
    print(resp.text)
    resp.raise_for_status()

    # get global items list
    resp = client.get("/v1/items")
    print(resp.text)
    resp.raise_for_status()
    items = resp.json()

    assert items[0]["name"] == item_data["name"]
    assert items[0]["owner_id"] == item_data["owner_id"]


def test_created_item_shows_up_in_client_list(
    client: TestClient,
    users: list[int],
    items_data: list[dict],
):
    item_data = items_data[0]

    # create item
    resp = client.post(
        "/v1/me/items",
        json={k: v for k, v in item_data.items() if k != "owner_id"},
    )
    print(resp.text)
    resp.raise_for_status()

    # get client items list
    resp = client.get("/v1/me/items")
    print(resp.text)
    resp.raise_for_status()
    items = resp.json()

    assert items[0]["name"] == item_data["name"]
    assert items[0]["owner_id"] == item_data["owner_id"]
