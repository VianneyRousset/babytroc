from contextlib import (
    AbstractAsyncContextManager,
    AsyncExitStack,
)
from types import TracebackType

import pytest
from httpx import AsyncClient
from httpx_ws import AsyncWebSocketSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.domains.chat import services as chat_services
from app.domains.chat.schemas.base import ChatId
from app.domains.chat.schemas.query import ChatMessageReadQueryFilter
from app.domains.chat.schemas.read import ChatMessageRead, ChatRead
from app.domains.chat.schemas.send import SendChatMessageText
from app.domains.chat.schemas.websocket import (
    WebSocketMessageNewChatMessage,
    WebSocketMessageUpdatedChatMessage,
)
from app.domains.item.schemas.read import ItemRead
from app.domains.loan import services as loan_services
from app.domains.loan.schemas.read import LoanRequestRead
from app.domains.user.schemas.private import UserPrivateRead
from tests.fixtures.websockets import WebSocketRecorder


class ReceivedChatMessageChecker(AbstractAsyncContextManager):
    """Helper to check received message via websocket and the REST API."""

    def __init__(
        self,
        *,
        clients: list[AsyncClient],
        websockets: list[AsyncWebSocketSession],
    ):
        self.clients = clients
        self.websocket_recorders = [WebSocketRecorder(ws) for ws in websockets]
        self._stack: AsyncExitStack | None = None

    async def __aenter__(self):
        async with AsyncExitStack() as stack:
            for recorder in self.websocket_recorders:
                await stack.enter_async_context(recorder)
            self._stack = stack.pop_all()

        return self

    async def __aexit__(
        self,
        type: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        if self._stack is not None:
            await self._stack.aclose()

        return None

    async def check(
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
        await self.check_client_message(
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

        expected_type = type(expected_websocket_message)

        for recorder in self.websocket_recorders:
            # find the message matching the expected type
            matching = [
                msg
                for msg in recorder.messages
                if isinstance(msg, expected_type)
            ]
            assert matching, (
                f"No {expected_type.__name__} found in received messages: "
                f"{[type(m).__name__ for m in recorder.messages]}"
            )
            message = matching[-1]
            assert isinstance(
                message,
                (WebSocketMessageNewChatMessage, WebSocketMessageUpdatedChatMessage),
            )

            assert {
                **message.model_dump(),
                "message": message.message.model_dump(
                    exclude=exclude,  # type: ignore[arg-type]
                ),
            } == {
                **expected_websocket_message.model_dump(),
                "message": expected_websocket_message.message.model_dump(
                    exclude=exclude,  # type: ignore[arg-type]
                ),
            }, "Unexpected websocket message"

    async def check_client_message(
        self,
        chat_id: ChatId,
        expected_message: ChatMessageRead,
        *,
        exclude: list[str] | None = None,
    ):
        for client in self.clients:
            resp = await client.get(f"/api/v1/me/chats/{chat_id}/messages")
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
async def alice_many_messages_to_bob(
    database_sessionmaker: async_sessionmaker,
    alice_many_messages_to_bob_text: list[str],
    alice: UserPrivateRead,
    bob_new_loan_request_for_alice_new_item: LoanRequestRead,
) -> list[ChatMessageRead]:
    """Many messages in the same chat sent by Alice to Bob."""

    chat_id = bob_new_loan_request_for_alice_new_item.chat_id

    async with database_sessionmaker.begin() as session:
        # get current messages
        messages: list[ChatMessageRead] = (
            await chat_services.list_messages(
                db=session,
                query_filter=ChatMessageReadQueryFilter(
                    chat_id=chat_id,
                ),
            )
        ).data

        # create extra messages
        extra_messages: list[
            ChatMessageRead
        ] = await chat_services.send_many_chat_messages(
            db=session,
            messages=[
                SendChatMessageText(
                    chat_id=chat_id,
                    sender_id=alice.id,
                    text=text,
                )
                for text in alice_many_messages_to_bob_text
            ],
        )

        return messages + extra_messages


@pytest.fixture(scope="class")
async def alice_many_chats(
    database_sessionmaker: async_sessionmaker,
    alice: UserPrivateRead,
    bob: UserPrivateRead,
    many_items: list[ItemRead],
) -> list[ChatRead]:
    """Many chats between Alice and Bob."""

    async with database_sessionmaker.begin() as session:
        loan_requests = [
            await loan_services.create_loan_request(
                db=session,
                item_id=item.id,
                borrower_id=alice.id if item.owner.id == bob.id else bob.id,
            )
            for item in many_items
            if item.owner.id in [alice.id, bob.id]
        ]
        return [
            await chat_services.get_chat(
                db=session,
                chat_id=loan_request.chat_id,
            )
            for loan_request in loan_requests
        ]
