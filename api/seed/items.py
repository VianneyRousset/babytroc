import logging
from collections.abc import Sequence
from pathlib import Path
from random import choice, randint, sample

import sqlalchemy
from tqdm import tqdm
from wonderwords import RandomSentence, RandomWord

import app
from app.schemas.item.constants import (
    DESCRIPTION_LENGTH,
    NAME_LENGTH,
)
from app.schemas.item.create import ItemCreate as Item

from .config import get_config

logger = logging.getLogger("seed")

word_generator = RandomWord()
sentence_generator = RandomSentence()


def check_items(
    db: sqlalchemy.orm.Session,
) -> bool:
    """Returns True if some items are present in the database."""

    logger.debug("Checking items: started")
    items = app.services.item.list_items(db).data
    logger.debug("%i (or more) items found", len(items))
    res = len(items) > 0
    logger.debug("Checking items: done")

    return res


def upload_image(
    db: sqlalchemy.orm.Session,
    config: app.config.Config,
    fp: Path,
    owner_id: int,
) -> str:
    """Upload image."""

    with fp.open(mode="rb") as f:
        image = app.services.image.upload_image(
            config=config,
            db=db,
            owner_id=owner_id,
            fp=f,
        )

        return image.name


def random_item_name() -> str:
    name = " ".join(word_generator.word() for _ in range(randint(2, 3))).capitalize()  # noqa: S311

    # min length
    while len(name) < NAME_LENGTH.start:
        name = name + " voila"

    # max length
    name = name[: NAME_LENGTH.stop]

    return name


def random_item_description() -> str:
    description = " ".join(sentence_generator.sentence() for _ in range(randint(3, 5)))  # noqa: S311

    # min length
    while len(description) < DESCRIPTION_LENGTH.start:
        description = description + " voila"

    # max length
    description = description[: DESCRIPTION_LENGTH.stop]

    return description


def random_item_images(names: Sequence[str]) -> list[str]:
    return sample(names, k=randint(1, 5))  # noqa: S311


def random_item_targeted_age_months() -> tuple[int | None, int | None]:
    _lower = randint(0, 10)  # noqa: S311
    lower = None if _lower == 0 else _lower

    _upper = randint(10, 30)  # noqa: S311
    upper = None if _upper == 30 else _upper

    return lower, upper


def random_item_regions(regions: Sequence[int]) -> list[int]:
    return sample(regions, k=randint(1, 5))  # noqa: S311


def populate_items(
    db: sqlalchemy.orm.Session,
    images_dir: Path,
    count: int,
) -> None:
    """Populate items."""

    logger.debug("Populating items: started")

    config = get_config()
    users = app.services.user.list_users(db)
    regions = app.services.region.list_regions(db)

    images_fp = list(images_dir.iterdir())

    images = {}

    # upload images
    logger.info("Uploading all images.")
    for user in tqdm(users, leave=False):
        # upload images
        logger.info("Uploading images for user %i (%s).", user.id, user.name)
        images[user.id] = [
            upload_image(
                db=db,
                config=config,
                fp=fp,
                owner_id=user.id,
            )
            for fp in tqdm(images_fp)
        ]

    # create items
    logger.debug("Generating %i items", count)
    for _ in tqdm(list(range(count))):
        user = choice(users)  # noqa: S311

        app.services.item.create_item(
            db=db,
            owner_id=user.id,
            item_create=Item(
                name=random_item_name(),
                description=random_item_description(),
                images=random_item_images(images[user.id]),
                targeted_age_months=random_item_targeted_age_months(),
                regions=random_item_regions([reg.id for reg in regions]),
                blocked=False,
            ),
        )

    logger.debug("Populating items: done")
