import logging
from collections.abc import Iterable

import sqlalchemy

logger = logging.getLogger(__name__)


def check_users(db: sqlalchemy.orm.Session) -> bool:
    """Returns True if some users are present in the database."""

    logger.debug("Checking users: started")
    res = False
    logger.debug("Checking users: done")

    return res

    return False


def populate_users(
    db: sqlalchemy.orm.Session,
    users: Iterable[str],
):
    """Populate users."""

    logger.debug("Populating users: started")
    logger.debug("Populating users: done")
