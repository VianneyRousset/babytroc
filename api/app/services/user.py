from sqlalchemy.orm import Session, selectinload

from app.clients import database
from app.enums import ReportType
from app.models.item import Item
from app.models.user import User
from app.schemas.report import ReportCreate
from app.schemas.user.create import UserCreate
from app.schemas.user.preview import UserPreviewRead
from app.schemas.user.read import UserRead
from app.schemas.user.update import UserUpdate


async def create_user(
    db: Session,
    user_create: UserCreate,
) -> UserRead:
    """Create a user."""

    # TODO password hash

    user = await database.user.create_user(
        db=db,
        email=user_create.email,
        name=user_create.name,
        password_hash=user_create.password,
        avatar_seed=user_create.avatar_seed,
        load_attributes=[User.likes_count, User.items],
        options=[
            selectinload(User.items).selectinload(Item.images),
            selectinload(User.items).selectinload(Item.active_loans),
        ],
    )

    return UserRead.from_orm(user)


async def list_users(
    db: Session,
) -> list[UserPreviewRead]:
    """List all users."""

    users = await database.user.list_users(db=db)

    return [UserPreviewRead.from_orm(user) for user in users]


async def get_user(
    db: Session,
    user_id: int,
) -> UserRead:
    """Get user with ID `user_id`."""

    user = await database.user.get_user(
        db=db,
        user_id=user_id,
        load_attributes=[User.likes_count, User.items],
        options=[
            selectinload(User.items).selectinload(Item.images),
            selectinload(User.items).selectinload(Item.active_loans),
        ],
    )

    return UserRead.from_orm(user)


async def update_user(
    db: Session,
    user_id: int,
    user_update: UserUpdate,
) -> UserRead:
    """Update user fields."""

    user = await database.user.update_user(
        db=db,
        user_id=user_id,
        attributes=user_update.model_dump(
            exclude_none=True,
        ),
        load_attributes=[User.likes_count, User.items],
        options=[
            selectinload(User.items).selectinload(Item.images),
            selectinload(User.items).selectinload(Item.active_loans),
        ],
    )

    return UserRead.from_orm(user)


async def delete_user(
    db: Session,
    user_id: int,
) -> None:
    """Mark user as deleted."""

    await database.user.delete_user(
        db=db,
        user_id=user_id,
    )


async def report_user(
    db: Session,
    user_id: int,
    reported_by_user_id: int,
    report_create: ReportCreate,
) -> None:
    """Create a report for the user with `user_id`.

    A maximum of info about the user is saved as well as the given client provided
    description and context.
    """

    user = await database.item.get_user_for_report()

    await database.report.insert_report(
        report_type=ReportType.user,
        reported_by_user_id=reported_by_user_id,
        saved_info=user.json(),
        description=report_create.description,
        context=report_create.context,
    )

    # TODO send an email to moderators
