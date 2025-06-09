import logging
from collections.abc import Iterable

import sqlalchemy
from tqdm import tqdm

import app
from app.schemas.user.create import UserCreate as User

logger = logging.getLogger("seed")


def check_users(db: sqlalchemy.orm.Session) -> bool:
    """Returns True if some users are present in the database."""

    logger.debug("Checking users: started")
    users = app.services.user.list_users(db)
    logger.debug("%i users found", len(users))
    res = len(users) > 0
    logger.debug("Checking users: done")

    return res


def populate_users(
    db: sqlalchemy.orm.Session,
    users: Iterable[User],
):
    """Populate users."""

    logger.debug("Populating users: started")

    for user in tqdm(users):
        app.services.user.create_user(
            db=db,
            user_create=user,
        )

    logger.debug("Populating users: done")
