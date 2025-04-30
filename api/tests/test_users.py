import pytest
from fastapi.testclient import TestClient

from app.schemas.item.read import ItemRead
from app.schemas.user.private import UserPrivateRead


@pytest.mark.usefixtures("alice")
class TestReadUser:
    """Test users read."""

    def test_get_user(
        self,
        client: TestClient,
        alice: UserPrivateRead,
        alice_items: list[ItemRead],
    ):
        """Check that user info can be publicaly retrieved."""

        # get user from global list
        resp = client.get(f"/v1/users/{alice.id}")
        resp.raise_for_status()
        read = resp.json()

        assert read["name"] == alice.name
        assert read["name"] == alice.name
        assert read["avatar_seed"] == alice.avatar_seed
        assert {item["id"] for item in read["items"]} == {
            item.id for item in alice_items
        }

    def test_get_user_me(
        self,
        alice_client: TestClient,
        alice: UserPrivateRead,
        alice_items: list[ItemRead],
    ):
        """Check that user 'me' can be retrieved."""

        # get user from /me
        resp = alice_client.get("/v1/me")
        resp.raise_for_status()
        read = resp.json()

        assert read["id"] == alice.id
        assert read["name"] == alice.name
        assert read["avatar_seed"] == alice.avatar_seed
        assert {item["id"] for item in read["items"]} == {
            item.id for item in alice_items
        }


class TestUpdateUser:
    """Test user update."""

    def test_update_user_name(
        self,
        client: TestClient,
        alice_client: TestClient,
        alice: UserPrivateRead,
    ):
        """Test updating user name."""

        resp = alice_client.post(
            "/v1/me",
            json={
                "name": "new_name",
            },
        )
        print(resp.text)
        resp.raise_for_status()

        # get item by id from global list
        resp = alice_client.get("/v1/me")
        resp.raise_for_status()
        read = resp.json()

        assert read["id"] == alice.id
        assert read["name"] == "new_name"
        assert read["avatar_seed"] == alice.avatar_seed


class TestDeleteUser:
    """Test user delete."""

    def test_delete_user(
        self,
        client: TestClient,
        alice_client: TestClient,
        alice: UserPrivateRead,
    ):
        """Check an user can delete the account."""

        # ensure user exists
        resp = client.get(f"/v1/users/{alice.id}")
        print(resp.text)
        resp.raise_for_status()

        # delete user
        resp = alice_client.delete("/v1/me")
        print(resp.text)
        resp.raise_for_status()

        # ensure user does not exist anymore
        resp = client.get(f"/v1/users/{alice.id}")
        print(resp.text)
        assert resp.status_code == 404
