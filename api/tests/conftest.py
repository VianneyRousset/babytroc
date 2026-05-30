import unittest.mock

import anyio
import httpx_ws._api as _ws_api
import httpx_ws.transport as _ws_transport

# Monkey-patch the hardcoded 0.1s accept timeout in httpx-ws.
# Under test load the server can take longer to accept websocket connections.
# We wrap the original __aenter__ so that ``self.receive`` uses a 2s timeout
# instead of 0.1s during the accept handshake.
_original_aenter = _ws_transport.ASGIWebSocketAsyncNetworkStream.__aenter__


async def _patched_aenter(self):
    original_receive = self.receive

    async def _receive_with_longer_timeout(timeout=None):  # noqa: ASYNC109
        # Replace the 0.1s accept timeout with 2s; leave others untouched
        if timeout is not None and timeout <= 0.1:
            timeout = 2.0
        return await original_receive(timeout)

    with unittest.mock.patch.object(
        self, "receive", side_effect=_receive_with_longer_timeout
    ):
        return await _original_aenter(self)


_ws_transport.ASGIWebSocketAsyncNetworkStream.__aenter__ = _patched_aenter  # type: ignore[method-assign]


# Workaround for upstream httpx-ws bug: AsyncWebSocketSession._background_receive
# in httpx_ws/_api.py catches the LOCAL httpx_ws.EndOfStream but not
# anyio.EndOfStream. When the ASGI server-side queue closes during teardown,
# anyio raises EndOfStream from the memory stream, which escapes the receive
# loop and surfaces as an unhandled ExceptionGroup on aconnect_ws exit.
# We wrap the bound method so that the additional exception class is treated
# the same as the local one — no other semantics change.
_original_background_receive = _ws_api.AsyncWebSocketSession._background_receive


async def _background_receive_catching_anyio_eos(self, max_bytes):
    try:
        await _original_background_receive(self, max_bytes)
    except anyio.EndOfStream:
        # Same shape of cleanup as the original except clause for the local
        # EndOfStream: signal the user-side that the stream is done.
        # The _send_event may already be closed at this point — that's fine,
        # the user-side has already moved on.
        try:
            await self._send_event.send(_ws_api.WebSocketNetworkError())
        except anyio.ClosedResourceError:
            pass


_ws_api.AsyncWebSocketSession._background_receive = (  # type: ignore[method-assign]
    _background_receive_catching_anyio_eos
)


pytest_plugins = [
    "tests.fixtures.database",
    "tests.fixtures.app",
    "tests.fixtures.regions",
    "tests.fixtures.users",
    "tests.fixtures.clients",
    "tests.fixtures.items",
    "tests.fixtures.loans",
    "tests.fixtures.websockets",
    "tests.fixtures.chat",
    "tests.fixtures.categories",
    "tests.fixtures.s3",
    "tests.fixtures.antibot",
]
