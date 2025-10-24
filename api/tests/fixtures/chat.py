from contextlib import AbstractContextManager
from types import TracebackType

import pytest
import sqlalchemy
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from starlette.testclient import WebSocketTestSession

from app.schemas.chat.base import ChatId
from app.schemas.chat.query import ChatMessageReadQueryFilter
from app.schemas.chat.read import ChatMessageRead
from app.schemas.loan.read import LoanRequestRead
from app.schemas.user.read import UserRead
from app.schemas.websocket import (
    WebSocketMessageNewChatMessage,
    WebSocketMessageUpdatedChatMessage,
)
from app.services.chat import list_messages, send_message_text
from tests.fixtures.websockets import WebSocketRecorder


class ReceivedChatMessageChecker(AbstractContextManager):
    """Helper to check received message via websocket and the REST API."""

    def __init__(
        self,
        *,
        clients: list[TestClient],
        websockets: list[WebSocketTestSession],
    ):
        self.clients = clients
        self.websocket_recorders = [WebSocketRecorder(ws) for ws in websockets]

    def __enter__(self):
        for recorder in self.websocket_recorders:
            recorder.__enter__()

        return self

    def __exit__(
        self,
        type: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        for recorder in self.websocket_recorders:
            recorder.__exit__(None, None, None)

        return None

    def check(
        self,
        chat_id: ChatId,
        *,
        expected_message: ChatMessageRead,
        expected_websocket_message: WebSocketMessageNewChatMessage
        | WebSocketMessageUpdatedChatMessage
        | None = None,
        exclude: list[str] | None = None,
    ):
        """Check `expected_message` matched the websocket and REST message."""

        # construct expected websocket message
        if expected_websocket_message is None:
            expected_websocket_message = WebSocketMessageNewChatMessage(
                type="new_chat_message",
                message=expected_message,
            )

        # run checks
        self.check_websocket_message_content(
            expected_websocket_message,
            exclude=exclude,
        )
        self.check_client_message(
            chat_id,
            expected_message,
            exclude=exclude,
        )

    def check_websocket_message_content(
        self,
        expected_websocket_message: WebSocketMessageNewChatMessage
        | WebSocketMessageUpdatedChatMessage,
        *,
        exclude: list[str] | None = None,
    ):
        """Check `expected_message` with the websocket and REST message."""

        for recorder in self.websocket_recorders:
            assert isinstance(
                recorder.message,
                WebSocketMessageNewChatMessage | WebSocketMessageUpdatedChatMessage,
            ), "Unexpected websocket message type"
            assert {
                **recorder.message.model_dump(),
                "message": recorder.message.message.model_dump(
                    exclude=exclude,  # type: ignore[arg-type]
                ),
            } == {
                **expected_websocket_message.model_dump(),
                "message": expected_websocket_message.message.model_dump(
                    exclude=exclude,  # type: ignore[arg-type]
                ),
            }, "Unexpected websocket message"

    def check_client_message(
        self,
        chat_id: ChatId,
        expected_message: ChatMessageRead,
        *,
        exclude: list[str] | None = None,
    ):
        for client in self.clients:
            resp = client.get(f"/v1/me/chats/{chat_id}/messages")
            resp.raise_for_status()
            last_chat_message = ChatMessageRead.model_validate(resp.json()[0])
            assert last_chat_message.model_dump(
                exclude=exclude,  # type: ignore[arg-type]
            ) == expected_message.model_dump(
                exclude=exclude,  # type: ignore[arg-type]
            )


@pytest.fixture(scope="class")
def alice_many_messages_to_bob_text() -> list[str]:
    """Text of the many messages sent by Alice to Bob."""
    return [f"msg - {i}" for i in range(100)]


@pytest.fixture
def alice_many_messages_to_bob(
    database: sqlalchemy.URL,
    alice_many_messages_to_bob_text: list[str],
    alice: UserRead,
    bob_new_loan_request_for_alice_new_item: LoanRequestRead,
) -> list[ChatMessageRead]:
    chat_id = bob_new_loan_request_for_alice_new_item.chat_id

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        # get current messages
        messages: list[ChatMessageRead] = list_messages(
            db=session,
            query_filter=ChatMessageReadQueryFilter(
                chat_id=chat_id,
            ),
        ).data

        # create extra messages
        extra_messages: list[ChatMessageRead] = [
            send_message_text(
                db=session,
                chat_id=chat_id,
                sender_id=alice.id,
                text=text,
            )
            for text in alice_many_messages_to_bob_text
        ]

        return messages + extra_messages
