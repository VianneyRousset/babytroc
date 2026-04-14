import pytest
from httpx import AsyncClient

from app.schemas.item.read import ItemRead
from app.schemas.user.private import UserPrivateRead


@pytest.mark.usefixtures("alice")
class TestUserRead:
    """Test users read."""

    async def test_get_user(
        self,
        client: AsyncClient,
        alice: UserPrivateRead,
        alice_items: list[ItemRead],
    ):
        """Check that user info can be publicly retrieved."""

        # get user from global list
        resp = await client.get(f"/api/v1/users/{alice.id}")
        resp.raise_for_status()
        read = resp.json()

        assert read["id"] == alice.id
        assert read["name"] == alice.name
        assert read["avatar_seed"] == alice.avatar_seed
        assert read["items_count"] == len(alice_items)

    async def test_get_user_me(
        self,
        alice_client: AsyncClient,
        alice: UserPrivateRead,
        alice_items: list[ItemRead],
    ):
        """Check that user 'me' can be retrieved."""

        # get user from /me
        resp = await alice_client.get("/api/v1/me")
        resp.raise_for_status()
        read = resp.json()

        assert read["id"] == alice.id
        assert read["name"] == alice.name
        assert read["email"] == alice.email
        assert read["avatar_seed"] == alice.avatar_seed
        assert read["items_count"] == len(alice_items)
