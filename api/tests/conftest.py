import unittest.mock

import httpx_ws.transport as _ws_transport

# Monkey-patch the hardcoded 0.1s accept timeout in httpx-ws.
# Under test load the server can take longer to accept websocket connections.
# We wrap the original __aenter__ so that ``self.receive`` uses a 2s timeout
# instead of 0.1s during the accept handshake.
_original_aenter = _ws_transport.ASGIWebSocketAsyncNetworkStream.__aenter__


async def _patched_aenter(self):
    original_receive = self.receive

    async def _receive_with_longer_timeout(timeout=None):
        # Replace the 0.1s accept timeout with 2s; leave others untouched
        if timeout is not None and timeout <= 0.1:
            timeout = 2.0
        return await original_receive(timeout)

    with unittest.mock.patch.object(
        self, "receive", side_effect=_receive_with_longer_timeout
    ):
        return await _original_aenter(self)


_ws_transport.ASGIWebSocketAsyncNetworkStream.__aenter__ = _patched_aenter


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
]
