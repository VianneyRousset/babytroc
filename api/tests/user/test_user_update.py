from fastapi.testclient import TestClient

from app.schemas.user.private import UserPrivateRead


class TestUpdateUser:
    """Test user update."""

    def test_update_user_name(
        self,
        client: TestClient,
        alice_client: TestClient,
        alice: UserPrivateRead,
    ):
        """Test updating user name."""

        new_name = "new_name"
        new_avatar_seed = "f76a4b3"

        resp = alice_client.post(
            "/v1/me",
            json={
                "name": new_name,
                "avatar_seed": new_avatar_seed,
            },
        )
        print(resp.text)
        resp.raise_for_status()

        # get item by id from global list
        resp = alice_client.get("/v1/me")
        resp.raise_for_status()
        read = resp.json()

        assert read["id"] == alice.id
        assert read["name"] == new_name
        assert read["avatar_seed"] == new_avatar_seed
