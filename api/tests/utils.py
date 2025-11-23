from collections.abc import Iterator
from typing import TypeVar

T = TypeVar("T")


def split[T](array: list[T], n: int) -> Iterator[list[T]]:
    k, m = divmod(len(array), n)
    return (array[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(n))
