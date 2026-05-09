from httpx import AsyncClient

from app.domains.item.schemas.read import ItemRead
from app.domains.user.schemas.private import UserPrivateRead


class TestUserDelete:
    """
    Test user delete.
    - Deletion should work even if user is owning items.
    - Deletion should work even if user has liked items.
    - Deletion should work even if user has saved items.
    - Deletion should work even if user has loan requests.
    - Deletion should work even if user has chat messages.
    """

    async def test_delete_user(
        self,
        client: AsyncClient,
        alice_client: AsyncClient,
        alice: UserPrivateRead,
        alice_items: list[ItemRead],
        bob_items: list[ItemRead],
    ):
        """Check an user can delete the account."""

        # ensure user exists
        resp = await client.get(f"/api/v1/users/{alice.id}")
        resp.raise_for_status()

        # ensure user has a least one item
        resp = await alice_client.get("/api/v1/me/items")
        assert len(resp.json()) > 0

        # add one of Bob's items to alice's liked and saved items
        resp = await alice_client.post(
            f"/api/v1/me/liked/{bob_items[0].id}"
        )
        resp.raise_for_status()
        resp = await alice_client.post(
            f"/api/v1/me/saved/{bob_items[0].id}"
        )
        resp.raise_for_status()

        # create a loan request
        resp = await alice_client.post(
            f"/api/v1/items/{bob_items[0].id}/request"
        )
        resp.raise_for_status()
        chat_id = resp.json()["chat_id"]

        # send a message to a chat
        await alice_client.post(
            f"/api/v1/me/chats/{chat_id}/messages",
            json={
                "text": "hi",
            },
        )

        # TODO check that an active loan prevents the user to be deleted

        # delete user
        resp = await alice_client.delete("/api/v1/me")
        resp.raise_for_status()

        # ensure user does not exist anymore
        resp = await client.get(f"/api/v1/users/{alice.id}")
        assert resp.status_code == 404
