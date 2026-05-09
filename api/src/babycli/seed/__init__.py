import json
import logging
from importlib.resources import files
from pathlib import Path

from .categories import (
    Category as Category,
)
from .categories import (
    check_categories as _check_categories,
)
from .categories import (
    populate_categories as _populate_categories,
)
from .database import shared_session
from .items import (
    check_items as _check_items,
)
from .items import (
    populate_items as _populate_items,
)
from .regions import (
    Region,
)
from .regions import (
    check_regions as _check_regions,
)
from .regions import (
    populate_regions as _populate_regions,
)
from .users import (
    User,
)
from .users import (
    check_users as _check_users,
)
from .users import (
    populate_users as _populate_users,
)

logger = logging.getLogger("babycli.seed")


def _default_data_file() -> Path:
    return Path(str(files("babycli.resources.seed").joinpath("data.json")))


def _default_images_dir() -> Path:
    return Path(str(files("babycli.resources.seed").joinpath("images")))


def read_regions(file: Path) -> list[Region]:
    with file.open() as f:
        data = json.load(f)
        return [Region.model_validate(reg) for reg in data["regions"]]


def read_categories(file: Path) -> list[Category]:
    with file.open() as f:
        data = json.load(f)
        return [Category.model_validate(cat) for cat in data["categories"]]


def read_users(file: Path) -> list[User]:
    with file.open() as f:
        data = json.load(f)
        return [User.model_validate(reg) for reg in data["users"]]


async def populate_all(
    fp: Path | None = None,
    items_count: int = 50,
    force: bool = False,
) -> None:
    if fp is None:
        fp = _default_data_file()
    logger.info("Starting populate all")
    async with shared_session:
        await populate_regions_cmd(fp=fp, force=force)
        await populate_categories_cmd(fp=fp, force=force)
        await populate_users_cmd(fp=fp, force=force)
        await populate_items_cmd(items_count=items_count, force=force)


async def populate_regions_cmd(
    fp: Path | None = None,
    force: bool = False,
) -> None:
    if fp is None:
        fp = _default_data_file()
    logger.info("Starting populate regions")
    regions = read_regions(fp)
    logger.info("%i regions found in %s", len(regions), fp)
    async with shared_session as db:
        if await _check_regions(db):
            logger.warning("Regions already populated.")
            if not force:
                msg = "Regions already populated."
                raise RuntimeError(msg)
        await _populate_regions(db, regions)


async def populate_categories_cmd(
    fp: Path | None = None,
    force: bool = False,
) -> None:
    if fp is None:
        fp = _default_data_file()
    logger.info("Starting populate categories")
    categories = read_categories(fp)
    logger.info("%i categories found in %s", len(categories), fp)
    async with shared_session as db:
        if await _check_categories(db):
            logger.warning("Categories already populated.")
            if not force:
                msg = "Categories already populated."
                raise RuntimeError(msg)
        await _populate_categories(db, categories)


async def populate_users_cmd(
    fp: Path | None = None,
    force: bool = False,
) -> None:
    if fp is None:
        fp = _default_data_file()
    logger.info("Starting populate users")
    users = read_users(fp)
    logger.info("%i users found in %s", len(users), fp)
    async with shared_session as db:
        if await _check_users(db):
            logger.warning("Users already populated.")
            if not force:
                msg = "Users already populated."
                raise RuntimeError(msg)
        await _populate_users(db, users)


async def populate_items_cmd(
    items_count: int = 20,
    force: bool = False,
) -> None:
    logger.info("Starting populate items")
    logger.info("%i items will be generated", items_count)
    async with shared_session as db:
        if await _check_items(db):
            logger.warning("Items already populated.")
            if not force:
                msg = "Items already populated."
                raise RuntimeError(msg)
        await _populate_items(
            db=db,
            images_dir=_default_images_dir(),
            count=items_count,
        )
