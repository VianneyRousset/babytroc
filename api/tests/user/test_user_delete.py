from fastapi.testclient import TestClient

from app.schemas.item.read import ItemRead
from app.schemas.user.private import UserPrivateRead


class TestUserDelete:
    """
    Test user delete.
    - Deletion should work even if user is owning items.
    - Deletion should work even if user has liked items.
    - Deletion should work even if user has saved items.
    - Deletion should work even if user has loan requests.
    - Deletion should work even if user has chat messages.
    """

    def test_delete_user(
        self,
        client: TestClient,
        alice_client: TestClient,
        alice: UserPrivateRead,
        alice_items: list[ItemRead],
        bob_items: list[ItemRead],
    ):
        """Check an user can delete the account."""

        # ensure user exists
        resp = client.get(f"/v1/users/{alice.id}")
        print(resp.text)
        resp.raise_for_status()

        # ensure user has a least one item
        assert len(alice_client.get("/v1/me/items").json()) > 0

        # add one of Bob's items to alice's liked and saved items
        alice_client.post(f"/v1/me/liked/{bob_items[0].id}").raise_for_status()
        alice_client.post(f"/v1/me/saved/{bob_items[0].id}").raise_for_status()

        # create a loan request
        resp = alice_client.post(f"/v1/items/{bob_items[0].id}/request")
        resp.raise_for_status()
        chat_id = resp.json()["chat_id"]

        # send a message to a chat
        alice_client.post(
            f"/v1/me/chats/{chat_id}/messages",
            json={
                "text": "hi",
            },
        )

        # TODO check that an active loan prevents the user to be deleted

        # delete user
        resp = alice_client.delete("/v1/me")
        print(resp.text)
        resp.raise_for_status()

        # ensure user does not exist anymore
        resp = client.get(f"/v1/users/{alice.id}")
        print(resp.text)
        assert resp.status_code == 404
