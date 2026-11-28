from sqlalchemy.ext.asyncio import async_sessionmaker

from babytroc.domains.moderation import services as moderation_services
from babytroc.domains.user.schemas.private import UserPrivateRead


class TestCreate:
    """
    Test admin create.
    - Created admin should appear in the list of all moderators.
    - Creation should not work if the client is not admin.
    - Creation should not work if the user does not exist.
    - Creation should not work if the user is already a moderator.
    """

    async def test_create_admin_service(
        self,
        alice: UserPrivateRead,
        database_sessionmaker: async_sessionmaker,
    ):
        """Check an user can delete the account."""

        # check not admins
        async with database_sessionmaker.begin() as db:
            admins = await moderation_services.get_all_admins(db)
            assert not admins

        # create alice as admin
        async with database_sessionmaker.begin() as db:
            await moderation_services.create_admin(db, alice.id)

        # check alice appears in the list of all admins
        async with database_sessionmaker.begin() as db:
            admins = await moderation_services.get_all_admins(db)
            assert admins[0].user_id == alice.id
