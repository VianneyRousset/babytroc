from fastapi import status
from httpx import AsyncClient

from app.domains.loan.schemas.read import LoanRequestRead


class TestMalformedInputs:
    """Test malformed inputs return proper error responses."""

    async def test_invalid_chat_id_format(
        self,
        alice_client: AsyncClient,
    ):
        """Invalid chat_id format should return 422."""
        resp = await alice_client.get("/api/v1/me/chats/invalid")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    async def test_non_integer_item_id(
        self,
        client: AsyncClient,
    ):
        """Non-integer item_id should return 422."""
        resp = await client.get("/api/v1/items/abc")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    async def test_empty_text_message(
        self,
        alice_client: AsyncClient,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Empty text message should be rejected."""
        chat_id = bob_new_loan_request_for_alice_new_item.chat_id
        resp = await alice_client.post(
            f"/api/v1/me/chats/{chat_id}/messages",
            json={"text": ""},
        )
        assert resp.is_error
