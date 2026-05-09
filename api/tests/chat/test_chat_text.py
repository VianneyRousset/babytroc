import pytest
from httpx import AsyncClient
from httpx_ws import AsyncWebSocketSession

from babytroc.domains.chat.enums import ChatMessageType
from babytroc.domains.chat.schemas.read import ChatMessageRead
from babytroc.domains.item.schemas.read import ItemRead
from babytroc.domains.loan.schemas.read import LoanRequestRead
from babytroc.domains.user.schemas.private import UserPrivateRead
from tests.fixtures.chat import ReceivedChatMessageChecker

pytestmark = pytest.mark.timeout(30)


class TestChatTextMessages:
    """Tests text chat messages."""

    async def test_message_text(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
        alice_websocket: AsyncWebSocketSession,
        bob_websocket: AsyncWebSocketSession,
        alice_new_item: ItemRead,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Check that text messages are transmitted."""

        item_id = bob_new_loan_request_for_alice_new_item.item.id
        chat_id = bob_new_loan_request_for_alice_new_item.chat_id
        text = "hello"

        # prepare chat message checker
        checker = ReceivedChatMessageChecker(
            clients=[alice_client, bob_client],
            websockets=[alice_websocket, bob_websocket],
        )

        # send text message
        async with checker:
            res = await alice_client.post(
                f"/api/v1/me/chats/{chat_id}/messages",
                json={"text": text},
            )
            res.raise_for_status()
            message = ChatMessageRead.model_validate(res.json())

        # construct expected chat message
        expected_message = ChatMessageRead(
            id=message.id,
            chat_id=chat_id,
            message_type=ChatMessageType.text,
            sender_id=alice.id,
            creation_date=message.creation_date,
            seen=False,
            text=text,
            loan_request_id=None,
            loan_id=None,
            item_id=item_id,
            borrower_id=bob.id,
        )

        # check received chat message
        await checker.check(
            chat_id=chat_id,
            expected_message=expected_message,
        )

    async def test_invalid_text(
        self,
        alice_client: AsyncClient,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Check empty or too long messages cannot be sent."""

        chat_id = bob_new_loan_request_for_alice_new_item.chat_id

        empty_text = ""
        white_text = "\t \n \r"
        too_long_text = "x" * 1001

        res = await alice_client.post(
            f"/api/v1/me/chats/{chat_id}/messages",
            json={"text": empty_text},
        )
        assert res.is_error, "Empty text message should be invalid"

        res = await alice_client.post(
            f"/api/v1/me/chats/{chat_id}/messages",
            json={"text": white_text},
        )
        assert res.is_error, "White text message should be invalid"

        res = await alice_client.post(
            f"/api/v1/me/chats/{chat_id}/messages",
            json={"text": too_long_text},
        )
        assert res.is_error, "Too long text message should be invalid"
