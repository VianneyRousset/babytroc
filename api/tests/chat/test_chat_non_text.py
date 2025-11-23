from datetime import datetime

from fastapi.testclient import TestClient
from starlette.testclient import WebSocketTestSession

from app.enums import ChatMessageType
from app.schemas.chat.read import ChatMessageRead
from app.schemas.item.read import ItemRead
from app.schemas.loan.read import LoanRead, LoanRequestRead
from app.schemas.user.private import UserPrivateRead
from tests.fixtures.chat import ReceivedChatMessageChecker


class TestChatMessageLoanRequestCreated:
    def test_message_loan_request_created(
        self,
        bob: UserPrivateRead,
        alice_new_item: ItemRead,
        alice_client: TestClient,
        bob_client: TestClient,
        alice_websocket: WebSocketTestSession,
        bob_websocket: WebSocketTestSession,
    ):
        """Check that creating a loan request sends a chat message."""

        # prepare chat message checker
        checker = ReceivedChatMessageChecker(
            clients=[alice_client, bob_client],
            websockets=[alice_websocket, bob_websocket],
        )

        # request item
        with checker:
            resp = bob_client.post(f"/v1/items/{alice_new_item.id}/request")
            resp.raise_for_status()
            loan_request = LoanRequestRead.model_validate_json(resp.text)

        # construct expected chat message
        expected_message = ChatMessageRead(
            id=999,
            chat_id=loan_request.chat_id,
            message_type=ChatMessageType.loan_request_created,
            sender_id=bob.id,
            creation_date=datetime.now(),
            seen=False,
            text=None,
            loan_request_id=loan_request.id,
            loan_id=None,
            item_id=alice_new_item.id,
            borrower_id=bob.id,
        )

        # check received chat message
        checker.check(
            chat_id=loan_request.chat_id,
            expected_message=expected_message,
            exclude=["id", "creation_date"],
        )


class TestChatMessageLoanRequestCancelled:
    def test_loan_request_cancelled_message(
        self,
        bob: UserPrivateRead,
        alice_client: TestClient,
        bob_client: TestClient,
        alice_websocket: WebSocketTestSession,
        bob_websocket: WebSocketTestSession,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Check that cancelling a loan request sends a chat message."""

        item_id = bob_new_loan_request_for_alice_new_item.item.id
        chat_id = bob_new_loan_request_for_alice_new_item.chat_id
        loan_request_id = bob_new_loan_request_for_alice_new_item.id

        # prepare chat message checker
        checker = ReceivedChatMessageChecker(
            clients=[alice_client, bob_client],
            websockets=[alice_websocket, bob_websocket],
        )

        # cancel loan request
        with checker:
            bob_client.delete(f"/v1/items/{item_id}/request").raise_for_status()

        # construct expected chat message
        expected_message = ChatMessageRead(
            id=999,
            chat_id=chat_id,
            message_type=ChatMessageType.loan_request_cancelled,
            sender_id=bob.id,
            creation_date=datetime.now(),
            seen=False,
            text=None,
            loan_request_id=loan_request_id,
            loan_id=None,
            item_id=item_id,
            borrower_id=bob.id,
        )

        # check received chat message
        checker.check(
            chat_id=chat_id,
            expected_message=expected_message,
            exclude=["id", "creation_date"],
        )


class TestChatMessageLoanRequestRejected:
    def test_loan_request_rejected_message(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_client: TestClient,
        bob_client: TestClient,
        alice_websocket: WebSocketTestSession,
        bob_websocket: WebSocketTestSession,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Check that rejecting a loan request sends a chat message."""

        item_id = bob_new_loan_request_for_alice_new_item.item.id
        chat_id = bob_new_loan_request_for_alice_new_item.chat_id
        loan_request_id = bob_new_loan_request_for_alice_new_item.id

        # prepare chat message checker
        checker = ReceivedChatMessageChecker(
            clients=[alice_client, bob_client],
            websockets=[alice_websocket, bob_websocket],
        )

        # reject loan request
        with checker:
            alice_client.post(
                f"/v1/me/items/{item_id}/requests/{loan_request_id}/reject"
            ).raise_for_status()

        # construct expected chat message
        expected_message = ChatMessageRead(
            id=999,
            chat_id=chat_id,
            message_type=ChatMessageType.loan_request_rejected,
            sender_id=alice.id,
            creation_date=datetime.now(),
            seen=False,
            text=None,
            loan_request_id=loan_request_id,
            loan_id=None,
            item_id=item_id,
            borrower_id=bob.id,
        )

        # check received chat message
        checker.check(
            chat_id=bob_new_loan_request_for_alice_new_item.chat_id,
            expected_message=expected_message,
            exclude=["id", "creation_date"],
        )


class TestChatMessageLoanRequestAccepted:
    def test_loan_request_accepted_message(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_client: TestClient,
        bob_client: TestClient,
        alice_websocket: WebSocketTestSession,
        bob_websocket: WebSocketTestSession,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Check that accepting a loan request sends a chat message."""

        item_id = bob_new_loan_request_for_alice_new_item.item.id
        chat_id = bob_new_loan_request_for_alice_new_item.chat_id
        loan_request_id = bob_new_loan_request_for_alice_new_item.id

        # prepare chat message checker
        checker = ReceivedChatMessageChecker(
            clients=[alice_client, bob_client],
            websockets=[alice_websocket, bob_websocket],
        )

        # accept loan request
        with checker:
            alice_client.post(
                f"/v1/me/items/{item_id}/requests/{loan_request_id}/accept"
            ).raise_for_status()

        # construct expected chat message
        expected_message = ChatMessageRead(
            id=999,
            chat_id=chat_id,
            message_type=ChatMessageType.loan_request_accepted,
            sender_id=alice.id,
            creation_date=datetime.now(),
            seen=False,
            text=None,
            loan_request_id=loan_request_id,
            loan_id=None,
            item_id=item_id,
            borrower_id=bob.id,
        )

        # check received chat message
        checker.check(
            chat_id=bob_new_loan_request_for_alice_new_item.chat_id,
            expected_message=expected_message,
            exclude=["id", "creation_date"],
        )


class TestChatMessageLoanStarted:
    def test_loan_started_message(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_client: TestClient,
        bob_client: TestClient,
        alice_websocket: WebSocketTestSession,
        bob_websocket: WebSocketTestSession,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Check that executing a loan request sends a chat message."""

        item_id = bob_new_loan_request_for_alice_new_item.item.id
        chat_id = bob_new_loan_request_for_alice_new_item.chat_id
        loan_request_id = bob_new_loan_request_for_alice_new_item.id

        # prepare chat message checker
        checker = ReceivedChatMessageChecker(
            clients=[alice_client, bob_client],
            websockets=[alice_websocket, bob_websocket],
        )

        # accept loan request
        alice_client.post(
            f"/v1/me/items/{item_id}/requests/{loan_request_id}/accept"
        ).raise_for_status()

        # execute loan request
        with checker:
            loan = bob_client.post(
                f"/v1/me/borrowings/requests/{loan_request_id}/execute"
            ).json()

        # construct expected chat message
        expected_message = ChatMessageRead(
            id=999,
            chat_id=chat_id,
            message_type=ChatMessageType.loan_started,
            sender_id=bob.id,
            creation_date=datetime.now(),
            seen=False,
            text=None,
            loan_request_id=None,
            loan_id=loan["id"],
            item_id=item_id,
            borrower_id=bob.id,
        )

        # check received chat message
        checker.check(
            chat_id=bob_new_loan_request_for_alice_new_item.chat_id,
            expected_message=expected_message,
            exclude=["id", "creation_date"],
        )


class TestChatMessageLoanEnded:
    def test_loan_ended_message(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_client: TestClient,
        bob_client: TestClient,
        alice_websocket: WebSocketTestSession,
        bob_websocket: WebSocketTestSession,
        alice_new_item: ItemRead,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
        bob_new_loan_of_alice_new_item: LoanRead,
    ):
        """Check that ending a loan sends a chat message."""

        item_id = bob_new_loan_request_for_alice_new_item.item.id
        chat_id = bob_new_loan_request_for_alice_new_item.chat_id
        loan_id = bob_new_loan_of_alice_new_item.id

        # prepare chat message checker
        checker = ReceivedChatMessageChecker(
            clients=[alice_client, bob_client],
            websockets=[alice_websocket, bob_websocket],
        )

        # end loan
        with checker:
            alice_client.post(
                f"/v1/me/loans/{loan_id}/end",
            ).raise_for_status()

        # construct expected chat message
        expected_message = ChatMessageRead(
            id=999,
            chat_id=chat_id,
            message_type=ChatMessageType.loan_ended,
            sender_id=alice.id,
            creation_date=datetime.now(),
            seen=False,
            text=None,
            loan_request_id=None,
            loan_id=loan_id,
            item_id=item_id,
            borrower_id=bob.id,
        )

        # check received chat message
        checker.check(
            chat_id=bob_new_loan_request_for_alice_new_item.chat_id,
            expected_message=expected_message,
            exclude=["id", "creation_date"],
        )
