from sqlalchemy.orm import Session, selectinload

from app.clients import database
from app.enums import ReportType
from app.models.user import User
from app.models.item import Item
from app.schemas.report import ReportCreate
from app.schemas.user import UserPreviewRead, UserRead, UserUpdate


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
        options=[selectinload(User.items).selectinload(Item.images)],
    )

    return UserRead.from_orm(user)


async def update_user(
    db: Session,
    user_id: int,
    user_update: UserUpdate,
) -> UserRead:
    """Update user fields."""

    user = await database.user.update_user(
        db=db, user_id=user_id, **user_update.model_dump(exclude_none=True)
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
