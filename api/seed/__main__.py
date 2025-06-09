from collections.abc import Iterable
from pathlib import Path
from typing import Annotated

from cyclopts import App, Parameter

from .items import populate_items as _populate_items
from .regions import populate_regions as _populate_regions
from .users import poppulate_users as _populate_users
from .validators import (
    validate_file_exists,
    validate_name_no_leading_or_trailing_whitespace,
    validate_name_not_empty,
)

app = App(
    name="seed",
    help="Tool to handle database seeding.",
)

populate = App(
    name="populate",
    help="Populate database.",
)

app.command(populate)

check = App(
    name="check",
    help="Check if the database is populated.",
)

app.command(check)


@populate.command(name="all")
def populate_all():
    """Populate regions, users and items."""
    populate_regions()
    populate_users()
    populate_items()


@populate.command(name="regions")
def populate_regions(
    file: Annotated[
        Path,
        Parameter(
            name="--regions-file",
            help="File containing all regions.",
            validator=[validate_file_exists],
        ),
    ],
):
    """Populate regions."""

    # TODO open database
    _populate_regions(
        file=file,
    )


@populate.command(name="users")
def populate_users(
    users: Annotated[
        Iterable[str],
        Parameter(
            name=["--user", "-u"],
            help="User name (can be specified mulitple times).",
            validator=[
                validate_name_not_empty,
                validate_name_no_leading_or_trailing_whitespace,
            ],
        ),
    ] = ("alice", "bob"),
):
    """Populate users."""

    # TODO open database
    _populate_users(
        users=users,
    )


@populate.command(name="items")
def populate_items():
    """Populate items."""

    # TODO open database
    _populate_items()


if __name__ == "__main__":
    app()
