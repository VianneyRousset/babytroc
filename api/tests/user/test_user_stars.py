import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.domains.user.errors import UserNotFoundError
from app.domains.user.schemas.private import UserPrivateRead
from app.domains.user.services import get_user
from app.domains.user.services.star.update import (
    AddUserStars,
    add_many_stars_to_users,
    add_stars_to_user,
)
from app.domains.user.star import stars_gain_when_adding_item


class TestStarsDomain:
    """Test stars domain function."""

    def test_stars_gain_when_adding_item(self):
        assert stars_gain_when_adding_item(1) == 20
        assert stars_gain_when_adding_item(3) == 60
        assert stars_gain_when_adding_item(0) == 0

    def test_stars_gain_invalid_input(self):
        with pytest.raises(ValueError, match="must be an integer"):
            stars_gain_when_adding_item("not_an_int")  # type: ignore[arg-type]


class TestStarsService:
    """Test stars service."""

    async def test_add_stars_to_user(
        self,
        database_sessionmaker: async_sessionmaker,
        alice: UserPrivateRead,
    ):
        async with database_sessionmaker.begin() as session:
            user_before = await get_user(db=session, user_id=alice.id)
            old_count = user_before.stars_count

        async with database_sessionmaker.begin() as session:
            await add_stars_to_user(db=session, user_id=alice.id, count=10)

        async with database_sessionmaker.begin() as session:
            user_after = await get_user(db=session, user_id=alice.id)
            assert user_after.stars_count == old_count + 10

    async def test_add_many_stars_to_users(
        self,
        database_sessionmaker: async_sessionmaker,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
    ):
        async with database_sessionmaker.begin() as session:
            alice_before = await get_user(db=session, user_id=alice.id)
            bob_before = await get_user(db=session, user_id=bob.id)

        async with database_sessionmaker.begin() as session:
            await add_many_stars_to_users(
                db=session,
                stars=[
                    AddUserStars(user_id=alice.id, stars_count=5),
                    AddUserStars(user_id=bob.id, stars_count=15),
                ],
            )

        async with database_sessionmaker.begin() as session:
            alice_after = await get_user(db=session, user_id=alice.id)
            bob_after = await get_user(db=session, user_id=bob.id)
            assert alice_after.stars_count == alice_before.stars_count + 5
            assert bob_after.stars_count == bob_before.stars_count + 15

    async def test_add_stars_duplicate_user_raises(
        self,
        database_sessionmaker: async_sessionmaker,
        alice: UserPrivateRead,
    ):
        async with database_sessionmaker.begin() as session:
            with pytest.raises(ValueError, match="Non-unique user"):
                await add_many_stars_to_users(
                    db=session,
                    stars=[
                        AddUserStars(user_id=alice.id, stars_count=5),
                        AddUserStars(user_id=alice.id, stars_count=10),
                    ],
                )

    async def test_add_stars_non_existent_user_raises(
        self,
        database_sessionmaker: async_sessionmaker,
    ):
        async with database_sessionmaker.begin() as session:
            with pytest.raises(UserNotFoundError):
                await add_stars_to_user(db=session, user_id=999999, count=10)
