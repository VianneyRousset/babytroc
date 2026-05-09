import pytest
from httpx import AsyncClient
from httpx_ws import AsyncWebSocketSession

from app.domains.chat.enums import ChatMessageType
from app.domains.chat.schemas.read import ChatMessageRead
from app.domains.loan.schemas.read import LoanRequestRead
from app.domains.user.schemas.private import UserPrivateRead
from app.domains.chat.schemas.websocket import WebSocketMessageUpdatedChatMessage
from tests.fixtures.chat import ReceivedChatMessageChecker

pytestmark = pytest.mark.timeout(30)


class TestChatMessageSeen:
    """Tests seen status on chat messages."""

    async def test_mark_message_as_seen(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
        alice_websocket: AsyncWebSocketSession,
        bob_websocket: AsyncWebSocketSession,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Check that seeing a message mark it as read and emit a websocket message."""

        chat_id = bob_new_loan_request_for_alice_new_item.chat_id
        item_id = bob_new_loan_request_for_alice_new_item.item.id
        text = "hello"

        # prepare chat message checker
        checker = ReceivedChatMessageChecker(
            clients=[alice_client, bob_client],
            websockets=[alice_websocket, bob_websocket],
        )

        # send text message
        res = await alice_client.post(
            f"/api/v1/me/chats/{chat_id}/messages",
            json={"text": text},
        )
        message = ChatMessageRead.model_validate(res.json())

        # drain pending websocket messages from fixture setup and text send
        for ws in [alice_websocket, bob_websocket]:
            try:
                while True:
                    await ws.receive_text(timeout=0.5)
            except TimeoutError:
                pass

        async with checker:
            res = await bob_client.post(
                f"/api/v1/me/chats/{chat_id}/messages/{message.id}/see"
            )
            res.raise_for_status()

        # construct expected chat message
        expected_message = ChatMessageRead(
            id=message.id,
            chat_id=chat_id,
            message_type=ChatMessageType.text,
            sender_id=alice.id,
            creation_date=message.creation_date,
            seen=True,
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
            expected_websocket_message=WebSocketMessageUpdatedChatMessage(
                type="updated_chat_message",
                message=expected_message,
            ),
        )
