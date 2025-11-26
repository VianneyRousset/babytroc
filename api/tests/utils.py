import asyncio
import random
from collections.abc import AsyncIterable, AsyncIterator, Iterable, Iterator
from string import ascii_letters
from typing import Any, Self, TypeVar, TypeVarTuple, overload

from app.schemas.item.base import MonthRange

T = TypeVar("T")
TP = TypeVarTuple("TP")
T0 = TypeVar("T0")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")


def split[T](array: list[T], n: int) -> Iterator[list[T]]:
    k, m = divmod(len(array), n)
    return (array[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(n))


def random_sample[T](population: list[T]) -> list[T]:
    return random.sample(population, k=random.randint(1, len(population)))


def random_str(length: int) -> str:
    return "".join(random.choices(ascii_letters, k=length))


def random_targeted_age_months() -> MonthRange:
    lower = random.randint(0, 32)
    upper = random.randint(lower, 33)
    return MonthRange.from_values(
        lower=None if lower == 0 else lower,
        upper=None if upper > 32 else upper,
    )


class CustomStopIteration(Exception):  # noqa: N818
    pass


class AsyncZip[*TP](
    AsyncIterator,
):
    @overload
    def __init__(
        self: "AsyncZip[tuple[T0]]",
        it0: Iterable[T0] | AsyncIterable[T0],
        /,
        *,
        strict: bool,
    ): ...

    @overload
    def __init__(
        self: "AsyncZip[tuple[T0, T1]]",
        it0: Iterable[T0] | AsyncIterable[T0],
        it1: Iterable[T1] | AsyncIterable[T1],
        /,
        *,
        strict: bool,
    ): ...

    @overload
    def __init__(
        self: "AsyncZip[tuple[T0, T1, T2]]",
        it0: Iterable[T0] | AsyncIterable[T0],
        it1: Iterable[T1] | AsyncIterable[T1],
        it2: Iterable[T2] | AsyncIterable[T2],
        /,
        *,
        strict: bool,
    ): ...

    @overload
    def __init__(
        self: "AsyncZip[tuple[T0, T1, T2, T3]]",
        it0: Iterable[T0] | AsyncIterable[T0],
        it1: Iterable[T1] | AsyncIterable[T1],
        it2: Iterable[T2] | AsyncIterable[T2],
        it3: Iterable[T3] | AsyncIterable[T3],
        /,
        *,
        strict: bool,
    ): ...

    @overload
    def __init__(
        self: "AsyncZip[tuple[T0, T1, T2, T3, T4]]",
        it0: Iterable[T0] | AsyncIterable[T0],
        it1: Iterable[T1] | AsyncIterable[T1],
        it2: Iterable[T2] | AsyncIterable[T2],
        it3: Iterable[T3] | AsyncIterable[T3],
        it4: Iterable[T4] | AsyncIterable[T4],
        /,
        *,
        strict: bool,
    ): ...

    def __init__(
        self,
        *its: Iterable[Any] | AsyncIterable[Any],
        strict: bool,
    ):
        # check types
        if invalid_objects := [
            it for it in its if not isinstance(it, (Iterable, AsyncIterable))
        ]:
            msg = f"Expected iterators, got: {type(next(iter(invalid_objects)))}"
            raise TypeError(msg)

        self.iterators = [self._aiter(it) for it in its]
        self.strict = strict

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> tuple[*TP]:
        try:
            async with asyncio.TaskGroup() as tg:
                tasks = [tg.create_task(self._anext(it)) for it in self.iterators]  # type: ignore[var-annotated]

        except ExceptionGroup as group:
            # raise exceptions if not stop iteration
            _, subgroup = group.split(CustomStopIteration)
            print("||subgroup||", subgroup, group.exceptions)
            if subgroup:
                raise subgroup from group

            if self.strict and len(group.exceptions) != len(self.iterators):
                msg = "Not all alguments are of the same length"
                raise ValueError(msg) from group

            raise StopAsyncIteration() from group

        return tuple([task.result() for task in tasks])

    @overload
    @staticmethod
    def _aiter(it: Iterable[T]) -> Iterator[T]: ...

    @overload
    @staticmethod
    def _aiter(it: AsyncIterable[T]) -> AsyncIterator[T]: ...

    @staticmethod
    def _aiter(it: Iterable[T] | AsyncIterable[T]) -> Iterator[T] | AsyncIterator[T]:
        if isinstance(it, AsyncIterable):
            return aiter(it)
        return iter(it)

    @staticmethod
    async def _anext(it: Iterator[T] | AsyncIterator[T]) -> T:
        try:
            if isinstance(it, AsyncIterator):
                return await anext(it)
            return next(it)

        except (StopIteration, StopAsyncIteration) as stopit:
            raise CustomStopIteration() from stopit


@overload
def azip(
    it0: Iterable[T0] | AsyncIterable[T0],
    /,
    *,
    strict: bool,
) -> AsyncZip[T0]: ...


@overload
def azip(
    it0: Iterable[T0] | AsyncIterable[T0],
    it1: Iterable[T1] | AsyncIterable[T1],
    /,
    *,
    strict: bool,
) -> AsyncZip[T0, T1]: ...


@overload
def azip(
    it0: Iterable[T0] | AsyncIterable[T0],
    it1: Iterable[T1] | AsyncIterable[T1],
    it2: Iterable[T2] | AsyncIterable[T2],
    /,
    *,
    strict: bool,
) -> AsyncZip[T0, T1, T2]: ...


@overload
def azip(
    it0: Iterable[T0] | AsyncIterable[T0],
    it1: Iterable[T1] | AsyncIterable[T1],
    it2: Iterable[T2] | AsyncIterable[T2],
    it3: Iterable[T3] | AsyncIterable[T3],
    /,
    *,
    strict: bool,
) -> AsyncZip[T0, T1, T2, T3]: ...


@overload
def azip(
    it0: Iterable[T0] | AsyncIterable[T0],
    it1: Iterable[T1] | AsyncIterable[T1],
    it2: Iterable[T2] | AsyncIterable[T2],
    it3: Iterable[T3] | AsyncIterable[T3],
    it4: Iterable[T4] | AsyncIterable[T4],
    /,
    *,
    strict: bool,
) -> AsyncZip[T0, T1, T2, T3, T4]: ...


def azip(*its: Iterable | AsyncIterable, strict: bool) -> AsyncZip:
    return aiter(AsyncZip(*its, strict=strict))
