from fastapi import Request, WebSocket

from .router import router


@router.websocket("/ws")
def get_client_chats_websocket(
    request: Request,
    websocket: WebSocket,
):
    """Get client's chats websocket with new messages."""
    # TODO subscribe and read redis new messages from clients
