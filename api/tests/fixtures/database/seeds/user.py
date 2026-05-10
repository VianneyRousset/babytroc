"""User seeds — baseline triple. `seed_many_users` lands in Phase 4."""

from sqlalchemy.ext.asyncio import AsyncSession

from babytroc.domains.user.schemas.create import UserCreate
from babytroc.domains.user.services import create_many_users_without_validation
from tests.fixtures.database.infrastructure.chain import SeedContext

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
