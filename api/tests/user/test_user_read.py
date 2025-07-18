import pytest
from fastapi.testclient import TestClient

from app.schemas.item.read import ItemRead
from app.schemas.user.private import UserPrivateRead


@pytest.mark.usefixtures("alice")
class TestUserRead:
    """Test users read."""

    def test_get_user(
        self,
        client: TestClient,
        alice: UserPrivateRead,
        alice_items: list[ItemRead],
    ):
        """Check that user info can be publicly retrieved."""

        # get user from global list
        resp = client.get(f"/v1/users/{alice.id}")
        resp.raise_for_status()
        read = resp.json()

        assert read["id"] == alice.id
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
        assert read["email"] == alice.email
        assert read["avatar_seed"] == alice.avatar_seed
        assert {item["id"] for item in read["items"]} == {
            item.id for item in alice_items
        }
