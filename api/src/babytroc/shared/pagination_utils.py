from collections.abc import AsyncGenerator, Generator, Iterable
from itertools import count, zip_longest
from typing import Any, TypeVar, cast
from urllib.parse import parse_qsl, urlparse

from httpx import AsyncClient

T = TypeVar("T")


def _parse_query(query: str) -> dict[str, str | list[str]]:
    """Like `dict(parse_qsl(...))` but groups repeated keys into a list.

    Preserves multi-value query params (e.g. `?reg=1&reg=2`) when building
    the next request's `params` dict; httpx will resend them as repeated
    query parameters.
    """
    grouped: dict[str, list[str]] = {}
    for key, value in parse_qsl(query):
        grouped.setdefault(key, []).append(value)
    return {k: v[0] if len(v) == 1 else v for k, v in grouped.items()}


async def iter_paginated_endpoint(
    client: AsyncClient,
    url: str,
    *,
    max_iteration: int | None = 1000,
    params: dict[str, Any] | None = None,
    **kwargs,
) -> AsyncGenerator[dict]:
    """Iter over all pages available at `url`."""

    params = params or {}

    for i in count():
        # check iteration count;w
        if max_iteration and i == max_iteration:
            msg = "Reached max iterations count"
            raise RuntimeError(msg)

        # get page
        resp = await client.get(
            url=url,
            params=params,
            **kwargs,
        )

        resp.raise_for_status()

        yield resp.json()

        # exit if no next url is provided
        try:
            next_url = resp.links["next"]["url"]

        except KeyError:
            return

        # parse next params (preserves repeated keys like ?reg=1&reg=2)
        params = _parse_query(urlparse(next_url).query)


class IterChunksStop:
    pass


def iter_chunks[T](
    iterable: Iterable[T],
    count: int,
    *,
    append_empty: bool = False,
) -> Generator[list[T]]:
    "grouper('abcdefgh', 3) --> ['a','b','c'], ['d','e','f'], ['g','h']"

    for chunk in zip_longest(*[iter(iterable)] * count, fillvalue=IterChunksStop):
        yield cast("list[T]", [v for v in chunk if v is not IterChunksStop])

    if append_empty:
        yield []
