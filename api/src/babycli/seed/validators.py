from collections.abc import Iterable
from pathlib import Path


def validate_file_exists(_type, fp: Path) -> None:
    """Raise an error if `fp` does not exists."""

    if not fp.exists():
        msg = f"File {fp} does not exist."
        raise ValueError(msg)


def validate_name_not_empty(_type, name: str) -> None:
    """Raise an error if `name` is empty."""

    if len(name) == 0:
        msg = "Invalid name {name!r}."
        raise ValueError(msg)


def validate_names_not_empty(_type, names: Iterable[str]) -> None:
    """Raise an error if any string in names is empty."""

    for name in names:
        validate_name_not_empty(str, name)


def validate_name_no_leading_or_trailing_whitespace(_type, name: str) -> None:
    """Raise an error if `s` has some leading or trailing whitespaces."""

    if len(name.strip()) != len(name):
        msg = "Invalid name {s!r}."
        raise ValueError(msg)


def validate_names_no_leading_or_trailing_whitespace(
    _type, names: Iterable[str]
) -> None:
    """Raise an error if any str in names has some leading or trailing whitespaces."""

    for name in names:
        validate_name_no_leading_or_trailing_whitespace(str, name)
