from fastapi.testclient import TestClient


def test_get_user(client: TestClient, user_alice: int, user_bob: int):
    # get item by id from global list
    resp = client.get(f"/v1/users/{user_bob}")
    resp.raise_for_status()
    read = resp.json()

    assert read["name"] == "bob"
