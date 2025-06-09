import logging

import sqlalchemy

logger = logging.getLogger(__name__)


def check_items(
    db: sqlalchemy.orm.Session,
) -> bool:
    """Returns True if some items are present in the database."""

    logger.debug("Checking items: started")
    res = False
    logger.debug("Checking items: done")

    return res


def populate_items(
    db: sqlalchemy.orm.Session,
    n: int,
) -> None:
    """Populate items."""

    logger.debug("Populating items: started")

    logger.debug("Populating items: done")
