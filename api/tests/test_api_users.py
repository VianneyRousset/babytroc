from fastapi.testclient import TestClient


def test_get_user(client: TestClient, users: list[int], users_data: list[dict]):
    user_id = users[0]
    user_data = users_data[0]

    # get item by id from global list
    resp = client.get(f"/v1/users/{user_id}")
    resp.raise_for_status()
    read = resp.json()

    assert read["name"] == user_data["name"]
