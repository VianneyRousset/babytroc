"""User seeds — baseline triple + bulk many_users."""

import random

from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.user.schemas.create import UserCreate
from babytroc.domains.user.services import create_many_users_without_validation
from babytroc.shared.hash import HashedStr
from tests.fixtures.database.infrastructure.chain import SeedContext
from tests.utils import random_str

_BASELINE_USERS = [
    UserCreate(name="alice", email="alice@babytroc.ch", password="password-Alice-42"),
    UserCreate(name="bob", email="bob@babytroc.ch", password="password-Bob-42"),
    UserCreate(name="carol", email="carol@babytroc.ch", password="password-Carol-42"),
]


async def seed_baseline_users(db: AsyncSession, ctx: SeedContext) -> None:
    """Insert alice, bob, carol with `validated=True`."""
    del ctx
    await create_many_users_without_validation(
        db=db,
        user_creates=_BASELINE_USERS,
        validated=True,
    )


async def seed_many_users(db: AsyncSession, ctx: SeedContext) -> None:
    """Create 256 random users. Random seed: 0x538D.

    All users share the same hashed password to keep seed time bounded.
    """
    del ctx
    n = 256
    random.seed(0x538D)
    password_hash = HashedStr("xyzXYZ123")

    user_creates = [
        UserCreate(
            name=random_str(8),
            email=f"{random_str(8)}@{random_str(8)}.com",
            password=password_hash,
        )
        for _ in range(n)
    ]

    await create_many_users_without_validation(
        db=db,
        user_creates=user_creates,
        validated=True,
    )
