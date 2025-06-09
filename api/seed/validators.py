from pathlib import Path


def validate_file_exists(_type, fp: Path) -> None:
    """Raise an error if `fp` does not exists."""

    if not fp.exists():
        msg = f"File {fp} does not exist."
        raise ValueError(msg)


def validate_name_not_empty(_type, s: str) -> None:
    """Raise an error if `s` is empty."""

    if len(s) == 0:
        msg = "Invalid name {s!r}."
        raise ValueError(msg)


def validate_name_no_leading_or_trailing_whitespace(_type, s: str) -> None:
    """Raise an error if `s` has some leading or trailing whitespaces."""

    if len(s.strip()) != len(s):
        msg = "Invalid name {s!r}."
        raise ValueError(msg)
