from collections.abc import Generator, Iterable
from itertools import count, zip_longest
from typing import Any, TypeVar, cast
from urllib.parse import parse_qsl, urlparse

from httpx import Client

T = TypeVar("T")


def iter_paginated_endpoint(
    client: Client,
    url: str,
    *,
    max_iteration: int | None = 1000,
    params: dict[str, Any] | None = None,
    **kwargs,
) -> Generator[dict]:
    """Iter over all pages available at `url`."""

    params = params or {}

    for i in count():
        # check iteration count;w
        if max_iteration and i == max_iteration:
            msg = "Reached max iterations count"
            raise RuntimeError(msg)

        # get page
        resp = client.get(
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

        # parse next params
        params = dict(parse_qsl(urlparse(next_url).query))


class IterChunksStop:
    pass


def iter_chunks(
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
