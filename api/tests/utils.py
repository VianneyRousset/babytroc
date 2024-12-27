from collections import Counter
from collections.abc import Coroutine, Mapping, Sequence
from contextlib import AbstractAsyncContextManager
from functools import wraps
from http import HTTPStatus
from typing import Any, Optional, Self

from deepdiff import DeepDiff
from httpx import AsyncClient


def async_partial(call: Coroutine, *args: Sequence[Any], **kwargs: Mapping[str, Any]):
    @wraps(call)
    async def wrapped():
        return await call(*args, **kwargs)

    return wrapped


class ChangesRecorder(AbstractAsyncContextManager):
    class Undefined:
        pass

    def __init__(self, call: Coroutine, **kwargs) -> Self:
        self.call = call
        self.start_value = self.Undefined()
        self.stop_value = self.Undefined()
        self.options = kwargs

    async def __aenter__(self) -> Self:
        self.start_value = await self.call()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.stop_value = await self.call()

    def diff(self) -> DeepDiff:
        self._check_start_stop_values_recorded()
        return DeepDiff(self.start_value, self.stop_value, **self.options)

    def _check_start_stop_values_recorded(self) -> None:
        if isinstance(self.start_value, self.Undefined):
            msg = "No start value set"
            raise RuntimeError(msg)

        if isinstance(self.stop_value, self.Undefined):
            msg = "No stop value set"
            raise RuntimeError(msg)


class EndpointChangesRecorder(ChangesRecorder):
    def __init__(
        self,
        client: AsyncClient,
        endpoint: str,
        *,
        dict_key: Optional[str] = None,
        **kwargs,
    ) -> Self:
        async def get():
            resp = await client.get(endpoint)

            if resp.status_code != HTTPStatus.OK:
                msg = f"GET request failed with status code {resp.status_code}"
                raise RuntimeError(msg)

            data = resp.json()

            if dict_key is None:
                return data

            data_dict = {row[dict_key]: row for row in data}

            if len(data) != len(data_dict):
                keys = [row[dict_key] for row in data]
                duplicated_keys = {k for k, v in Counter(keys).items() if v > 1}
                msg = f"Duplicate keys: {duplicated_keys!r}"
                raise ValueError(msg)

            return data_dict

        super().__init__(get, **kwargs)
