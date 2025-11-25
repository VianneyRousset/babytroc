import random
from collections.abc import Iterator
from string import ascii_letters
from typing import TypeVar

from app.schemas.item.base import MonthRange

T = TypeVar("T")


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
