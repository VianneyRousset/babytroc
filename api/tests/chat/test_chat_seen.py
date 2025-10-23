from fastapi.testclient import TestClient
from starlette.testclient import WebSocketTestSession

from app.enums import ChatMessageType
from app.schemas.chat.read import ChatMessageRead
from app.schemas.loan.read import LoanRequestRead
from app.schemas.user.private import UserPrivateRead
from app.schemas.websocket import WebSocketMessageUpdatedChatMessage
from tests.fixtures.chat import ReceivedChatMessageChecker


class TestChatMessageSeen:
    """Tests seen status on chat messages."""

    def test_mark_message_as_seen(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_client: TestClient,
        bob_client: TestClient,
        alice_websocket: WebSocketTestSession,
        bob_websocket: WebSocketTestSession,
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
        message = ChatMessageRead.model_validate(
            alice_client.post(
                f"/v1/me/chats/{chat_id}/messages",
                json={"text": text},
            ).json()
        )

        with checker:
            bob_client.post(
                f"/v1/me/chats/{chat_id}/messages/{message.id}/see"
            ).raise_for_status()

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
        checker.check(
            chat_id=chat_id,
            expected_message=expected_message,
            expected_websocket_message=WebSocketMessageUpdatedChatMessage(
                type="updated_chat_message",
                message=expected_message,
            ),
        )
