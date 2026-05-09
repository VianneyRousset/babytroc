from httpx import AsyncClient

from app.domains.user.schemas.private import UserPrivateRead


class TestUpdateUser:
    """Test user update."""

    async def test_update_user_name(
        self,
        client: AsyncClient,
        alice_client: AsyncClient,
        alice: UserPrivateRead,
    ):
        """Test updating user name."""

        new_name = "new_name"
        new_avatar_seed = "f76a4b3"

        resp = await alice_client.post(
            "/api/v1/me",
            json={
                "name": new_name,
                "avatar_seed": new_avatar_seed,
            },
        )
        resp.raise_for_status()

        # get item by id from global list
        resp = await alice_client.get("/api/v1/me")
        resp.raise_for_status()
        read = resp.json()

        assert read["id"] == alice.id
        assert read["name"] == new_name
        assert read["avatar_seed"] == new_avatar_seed
