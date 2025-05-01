import asyncio
from typing import Annotated

from broadcaster import Broadcast
from fastapi import WebSocket
from fastapi.params import Depends

from app.pubsub import get_broadcast

from .router import router


class TerminateTaskGroup(Exception):  # noqa: N818
    """Exception raised to terminate a task group."""


async def terminate_task_group_when_websocket_is_closed(
    websocket: WebSocket,
):
    """Raise TerminateTaskGroup when `websocket` is closed."""

    try:
        async for _ in websocket.iter_bytes():
            pass

    finally:
        raise TerminateTaskGroup()


async def relay_broacast_events_to_websocket(
    websocket: WebSocket,
    broadcast: Broadcast,
    *args,
    **kwargs,
):
    """Send events of `broadcast` to `websocket`."""

    async with broadcast.subscribe(*args, **kwargs) as subscriber:
        async for event in subscriber:
            await websocket.send_text(event.message)  # type: ignore[union-attr]


@router.websocket("/websocket")
async def open_websocket(
    websocket: WebSocket,
    broadcast: Annotated[Broadcast, Depends(get_broadcast)],
):
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
                    channel="chat-messages",
                )
            )

    except* TerminateTaskGroup:
        pass
