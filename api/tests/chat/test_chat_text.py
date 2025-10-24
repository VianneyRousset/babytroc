from fastapi.testclient import TestClient
from starlette.testclient import WebSocketTestSession

from app.enums import ChatMessageType
from app.schemas.chat.read import ChatMessageRead
from app.schemas.item.read import ItemRead
from app.schemas.loan.read import LoanRequestRead
from app.schemas.user.private import UserPrivateRead
from tests.fixtures.chat import ReceivedChatMessageChecker


class TestChatTextMessages:
    """Tests text chat messages."""

    def test_message_text(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_client: TestClient,
        bob_client: TestClient,
        alice_websocket: WebSocketTestSession,
        bob_websocket: WebSocketTestSession,
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
        with checker:
            message = ChatMessageRead.model_validate(
                alice_client.post(
                    f"/v1/me/chats/{chat_id}/messages",
                    json={"text": text},
                ).json()
            )

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
        checker.check(
            chat_id=chat_id,
            expected_message=expected_message,
        )

    def test_invalid_text(
        self,
        alice_client: TestClient,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Check empty or too long messages cannot be sent."""

        chat_id = bob_new_loan_request_for_alice_new_item.chat_id

        empty_text = ""
        white_text = "\t \n \r"
        too_long_text = "x" * 1001

        assert alice_client.post(
            f"/v1/me/chats/{chat_id}/messages",
            json={"text": empty_text},
        ).is_error, "Empty text message should be invalid"
        assert alice_client.post(
            f"/v1/me/chats/{chat_id}/messages",
            json={"text": white_text},
        ).is_error, "White text message should be invalid"
        assert alice_client.post(
            f"/v1/me/chats/{chat_id}/messages",
            json={"text": too_long_text},
        ).is_error, "Too long text message should be invalid"
