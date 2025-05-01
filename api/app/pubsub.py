from typing import Annotated

from broadcaster import Broadcast
from fastapi import FastAPI, Request, WebSocket
from fastapi.params import Depends


# trick to get the app from either the request (http/https) or websocket (ws/wss)
def get_app(
    request: Request = None,  # type: ignore[assignment]
    websocket: WebSocket = None,  # type: ignore[assignment]
) -> FastAPI:
    if request is not None:
        return request.app

    if websocket is not None:
        return websocket.app

    msg = "Either request or websocket must be set."
    raise ValueError(msg)


def get_broadcast(app: Annotated[FastAPI, Depends(get_app)]) -> Broadcast:
    return app.state.broadcast
