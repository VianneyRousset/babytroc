from datetime import datetime

import pytest
from httpx import AsyncClient
from httpx_ws import AsyncWebSocketSession

from babytroc.domains.chat.enums import ChatMessageType
from babytroc.domains.chat.schemas.read import ChatMessageRead
from babytroc.domains.item.schemas.read import ItemRead
from babytroc.domains.loan.schemas.read import LoanRead, LoanRequestRead
from babytroc.domains.user.schemas.private import UserPrivateRead
from tests.fixtures.chat import ReceivedChatMessageChecker

# These tests use websockets + S3 uploads + broadcaster relay, which under
# parallel load (-n 8) can exceed the default 10s timeout.
pytestmark = pytest.mark.timeout(30)


class TestChatMessageLoanRequestCreated:
    async def test_message_loan_request_created(
        self,
        bob: UserPrivateRead,
        alice_new_item: ItemRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
        alice_websocket: AsyncWebSocketSession,
        bob_websocket: AsyncWebSocketSession,
    ):
        """Check that creating a loan request sends a chat message."""

        # prepare chat message checker
        checker = ReceivedChatMessageChecker(
            clients=[alice_client, bob_client],
            websockets=[alice_websocket, bob_websocket],
        )

        # request item
        async with checker:
            resp = await bob_client.post(
                f"/api/v1/items/{alice_new_item.id}/request"
            )
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
        await checker.check(
            chat_id=loan_request.chat_id,
            expected_message=expected_message,
            exclude=["id", "creation_date"],
        )


class TestChatMessageLoanRequestCancelled:
    async def test_loan_request_cancelled_message(
        self,
        bob: UserPrivateRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
        alice_websocket: AsyncWebSocketSession,
        bob_websocket: AsyncWebSocketSession,
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
        async with checker:
            res = await bob_client.delete(
                f"/api/v1/items/{item_id}/request"
            )
            res.raise_for_status()

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
        await checker.check(
            chat_id=chat_id,
            expected_message=expected_message,
            exclude=["id", "creation_date"],
        )


class TestChatMessageLoanRequestRejected:
    async def test_loan_request_rejected_message(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
        alice_websocket: AsyncWebSocketSession,
        bob_websocket: AsyncWebSocketSession,
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
        async with checker:
            res = await alice_client.post(
                f"/api/v1/me/items/{item_id}/requests/{loan_request_id}/reject"
            )
            res.raise_for_status()

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
        await checker.check(
            chat_id=bob_new_loan_request_for_alice_new_item.chat_id,
            expected_message=expected_message,
            exclude=["id", "creation_date"],
        )


class TestChatMessageLoanRequestAccepted:
    async def test_loan_request_accepted_message(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
        alice_websocket: AsyncWebSocketSession,
        bob_websocket: AsyncWebSocketSession,
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
        async with checker:
            res = await alice_client.post(
                f"/api/v1/me/items/{item_id}/requests/{loan_request_id}/accept"
            )
            res.raise_for_status()

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
        await checker.check(
            chat_id=bob_new_loan_request_for_alice_new_item.chat_id,
            expected_message=expected_message,
            exclude=["id", "creation_date"],
        )


class TestChatMessageLoanStarted:
    async def test_loan_started_message(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
        alice_websocket: AsyncWebSocketSession,
        bob_websocket: AsyncWebSocketSession,
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
        res = await alice_client.post(
            f"/api/v1/me/items/{item_id}/requests/{loan_request_id}/accept"
        )
        res.raise_for_status()

        # execute loan request
        async with checker:
            res = await bob_client.post(
                f"/api/v1/me/borrowings/requests/{loan_request_id}/execute"
            )
            loan = res.json()

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
        await checker.check(
            chat_id=bob_new_loan_request_for_alice_new_item.chat_id,
            expected_message=expected_message,
            exclude=["id", "creation_date"],
        )


class TestChatMessageLoanEnded:
    async def test_loan_ended_message(
        self,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
        alice_websocket: AsyncWebSocketSession,
        bob_websocket: AsyncWebSocketSession,
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
        async with checker:
            res = await alice_client.post(
                f"/api/v1/me/loans/{loan_id}/end",
            )
            res.raise_for_status()

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
        await checker.check(
            chat_id=bob_new_loan_request_for_alice_new_item.chat_id,
            expected_message=expected_message,
            exclude=["id", "creation_date"],
        )
