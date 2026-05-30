import logging
from collections.abc import Sequence
from random import choice, randint, sample

from sqlalchemy.ext.asyncio import AsyncSession
from tqdm import tqdm
from trio import Path
from wonderwords import RandomSentence, RandomWord

from babytroc.domains.category.services import list_categories
from babytroc.domains.image.services import upload_image as _upload_image
from babytroc.domains.item.schemas.base import MonthRange
from babytroc.domains.item.schemas.constants import (
    DESCRIPTION_LENGTH,
    NAME_LENGTH,
)
from babytroc.domains.item.schemas.create import ItemCreate as Item
from babytroc.domains.item.services import create_item, list_items
from babytroc.domains.region.services import list_regions
from babytroc.domains.user.services import list_users
from babytroc.infrastructure.cache_client import NullCache
from babytroc.infrastructure.config import Config

from .config import get_config

logger = logging.getLogger("seed")

_cache = NullCache()

word_generator = RandomWord()
sentence_generator = RandomSentence()


async def check_items(
    db: AsyncSession,
) -> bool:
    """Returns True if some items are present in the database."""

    logger.debug("Checking items: started")
    result = await list_items(db)
    items = result.data
    logger.debug("%i (or more) items found", len(items))
    res = len(items) > 0
    logger.debug("Checking items: done")

    return res


async def upload_image(
    db: AsyncSession,
    config: Config,
    fp: Path,
    owner_id: int,
) -> str:
    """Upload image."""

    async with await fp.open(mode="rb") as f:
        image = await _upload_image(
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


def random_item_targeted_age_months() -> MonthRange:
    _lower = randint(0, 10)  # noqa: S311
    lower = None if _lower == 0 else _lower

    _upper = randint(10, 30)  # noqa: S311
    upper = None if _upper == 30 else _upper

    return MonthRange.from_values(
        lower=lower,
        upper=upper,
    )


def random_item_regions(regions: Sequence[int]) -> list[int]:
    return sample(regions, k=randint(1, 5))  # noqa: S311


def random_item_categories(categories: Sequence[str]) -> list[str]:
    return sample(categories, k=randint(1, min(3, len(categories))))  # noqa: S311


async def populate_items(
    db: AsyncSession,
    images_dir: Path,
    count: int,
) -> None:
    """Populate items."""

    logger.debug("Populating items: started")

    config = get_config()
    users = await list_users(db)
    regions = await list_regions(db, _cache)
    categories = await list_categories(db, _cache)
    child_category_slugs = [
        cat.slug for cat in categories if cat.parent_slug is not None
    ]

    images_fp = list(await images_dir.iterdir())

    images = {}

    # upload images
    logger.info("Uploading all images.")
    for user in tqdm(users, leave=False):
        # upload images
        logger.info("Uploading images for user %i (%s).", user.id, user.name)
        images[user.id] = [
            await upload_image(
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

        await create_item(
            db=db,
            owner_id=user.id,
            item_create=Item(
                name=random_item_name(),
                description=random_item_description(),
                images=random_item_images(images[user.id]),
                targeted_age_months=random_item_targeted_age_months(),
                regions=set(random_item_regions([reg.id for reg in regions])),
                categories=set(random_item_categories(child_category_slugs)),
                blocked=False,
            ),
        )

    logger.debug("Populating items: done")
