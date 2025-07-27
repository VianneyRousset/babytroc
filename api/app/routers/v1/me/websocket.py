import asyncio
from typing import Annotated

from broadcaster import Broadcast
from fastapi import Depends, WebSocket

from app import services
from app.pubsub import get_broadcast
from app.routers.v1.auth import verify_websocket_credentials_no_validation_check
from app.schemas.chat.query import ChatMessageReadQueryFilter
from app.schemas.pubsub import (
    PubsubMessageNewChatMessage,
    PubsubMessageTypeAdapter,
    PubsubMessageUpdatedAccountValidation,
    PubsubMessageUpdatedChatMessage,
)
from app.schemas.websocket import (
    WebSocketMessageNewChatMessage,
    WebsocketMessageUpdatedAccountValidation,
    WebSocketMessageUpdatedChatMessage,
)

from .router import router


class TerminateTaskGroup(Exception):  # noqa: N818
    """Exception raised to terminate a task group."""


async def terminate_task_group_when_websocket_is_closed(
    websocket: WebSocket,
):
    """Raise TerminateTaskGroup when `websocket` is closed."""

    try:
        async for _ in websocket.iter_text():
            pass

    finally:
        raise TerminateTaskGroup()


async def relay_broacast_events_to_websocket(
    websocket: WebSocket,
    broadcast: Broadcast,
    client_id: int,
    *args,
    **kwargs,
):
    """Send events of `broadcast` to `websocket`."""

    # TODO add logging in case of error
    async with broadcast.subscribe(*args, **kwargs) as subscriber:
        async for event in subscriber:
            if event is None:
                continue

            pubsub_message = PubsubMessageTypeAdapter.validate_json(event.message)

            if isinstance(pubsub_message, PubsubMessageNewChatMessage):
                async with websocket.app.state.db_async_session_maker.begin() as db:
                    chat_message = await services.chat.get_message_async(
                        db=db,
                        message_id=pubsub_message.chat_message_id,
                        query_filter=ChatMessageReadQueryFilter(
                            member_id=client_id,
                        ),
                    )
                await websocket.send_text(
                    WebSocketMessageNewChatMessage(
                        message=chat_message,
                    ).model_dump_json()
                )

            elif isinstance(pubsub_message, PubsubMessageUpdatedChatMessage):
                async with websocket.app.state.db_async_session_maker.begin() as db:
                    chat_message = await services.chat.get_message_async(
                        db=db,
                        message_id=pubsub_message.chat_message_id,
                        query_filter=ChatMessageReadQueryFilter(
                            member_id=client_id,
                        ),
                    )
                await websocket.send_text(
                    WebSocketMessageUpdatedChatMessage(
                        message=chat_message,
                    ).model_dump_json()
                )

            elif isinstance(pubsub_message, PubsubMessageUpdatedAccountValidation):
                await websocket.send_text(
                    WebsocketMessageUpdatedAccountValidation(
                        validated=pubsub_message.validated,
                    ).model_dump_json()
                )

            else:
                msg = f"Unhandled pubsub message type {pubsub_message}"
                raise TypeError(msg)


@router.websocket("/websocket")
async def open_websocket(
    websocket: WebSocket,
    broadcast: Annotated[Broadcast, Depends(get_broadcast)],
):
    client_id = verify_websocket_credentials_no_validation_check(
        websocket,
    )

    try:
        await websocket.accept()

        async with asyncio.TaskGroup() as group:
            group.create_task(
                terminate_task_group_when_websocket_is_closed(
                    websocket=websocket,
                )
            )
            group.create_task(
                relay_broacast_events_to_websocket(
                    websocket=websocket,
                    broadcast=broadcast,
                    client_id=client_id,
                    channel=f"user{client_id}",
                )
            )

    except* TerminateTaskGroup:
        pass

    finally:
        try:
            await websocket.close()
        except RuntimeError:
            pass
