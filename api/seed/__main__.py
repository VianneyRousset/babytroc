import json
import logging
from collections.abc import Iterable
from pathlib import Path
from typing import Annotated


from cyclopts import App, Parameter

from .database import shared_session
from .items import (
    populate_items as _populate_items,
    check_items as _check_items,
)
from .regions import (
    Region,
    populate_regions as _populate_regions,
    check_regions as _check_regions,
)
from .users import (
    User,
    populate_users as _populate_users,
    check_users as _check_users,
)
from .validators import (
    validate_file_exists,
    validate_names_no_leading_or_trailing_whitespace,
    validate_names_not_empty,
)


class CustomFormatter(logging.Formatter):
    """Logging colored formatter.

    from https://alexandra-zaharia.github.io/posts/make-your-own-custom-color-formatter-with-python-logging/
    """

    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset,
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter("%(levelname)s - %(message)s"))
logger.addHandler(ch)

app = App(
    name="seed",
    help="Tool to handle database seeding.",
)

populate = App(
    name="populate",
    help="Populate database.",
)

app.command(populate)


@populate.command(name="all")
def populate_all():
    """Populate regions, users and items."""

    # open shared session here to ensure a rollback on all changes if any step fails
    with shared_session:
        populate_regions()
        populate_users()
        populate_items()


def read_regions(file: Path) -> list[Region]:
    with file.open() as f:
        data = json.load(f)
        return [Region.model_validate(reg) for reg in data["regions"]]


@populate.command(name="regions")
def populate_regions(
    fp: Annotated[
        Path,
        Parameter(
            name="--data-file",
            help="File containing all regions.",
            validator=[validate_file_exists],
        ),
    ] = Path("seed/data/data.json"),
    force: Annotated[
        bool,
        Parameter(
            name=["--force", "-f"],
            help="Try to populate even if already populated",
        ),
    ] = False,
):
    """Populate regions."""

    # read regions
    regions = read_regions(fp)
    logger.info("%i regions found in %s", len(regions), fp)

    with shared_session as db:
        # check state
        if _check_regions(db):
            logger.warning("Regions already populated.")

            if not force:
                msg = "Regions already populated."
                raise RuntimeError(msg)

        # populate
        _populate_regions(db, regions)


def read_users(file: Path) -> list[User]:
    with file.open() as f:
        data = json.load(f)
        return [User.model_validate(reg) for reg in data["users"]]


@populate.command(name="users")
def populate_users(
    fp: Annotated[
        Path,
        Parameter(
            name="--data-file",
            help="File containing all users.",
            validator=[validate_file_exists],
        ),
    ] = Path("seed/data/data.json"),
    force: Annotated[
        bool,
        Parameter(
            name=["--force", "-f"],
            help="Try to populate even if already populated",
        ),
    ] = False,
):
    """Populate users."""

    # read users
    users = read_users(fp)
    logger.info("%i users found in %s", len(users), fp)

    with shared_session as db:
        # check state
        if _check_users(db):
            logger.warning("Users already populated.")

            if not force:
                msg = "Users already populated."
                raise RuntimeError(msg)

        # populate
        _populate_users(db, users)


@populate.command(name="items")
def populate_items(
    n_items: Annotated[
        int,
        Parameter(
            name=["--items-count", "-n"],
            help="Number of items per user..",
        ),
    ] = 10,
    force: Annotated[
        bool,
        Parameter(
            name=["--force", "-f"],
            help="Try to populate even if already populated",
        ),
    ] = False,
):
    """Populate items."""

    with shared_session as db:
        # check state
        if _check_items(db):
            logger.warning("Users already populated.")

            if not force:
                msg = "Users already populated."
                raise RuntimeError(msg)

        # populate
        _populate_items(db, n_items)


if __name__ == "__main__":
    app()
