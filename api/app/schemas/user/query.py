from pydantic import EmailStr

from app.models.user import User
from app.schemas.base import QueryFilter, StatementT


class UserQueryFilterName(QueryFilter):
    """Filter users by name."""

    name: str | None = None

    def _filter(self, stmt: StatementT) -> StatementT:
        return super()._filter(
            stmt.where(User.name == self.name) if self.name is not None else stmt
        )


class UserQueryFilterEmail(QueryFilter):
    email: EmailStr | None = None

    def _filter(self, stmt: StatementT) -> StatementT:
        return super()._filter(
            stmt.where(User.email == self.email) if self.email is not None else stmt
        )


class UserReadQueryFilter(
    UserQueryFilterName,
    UserQueryFilterEmail,
):
    """Filters of the user read query."""


class UserUpdateQueryFilter(
    UserQueryFilterName,
    UserQueryFilterEmail,
):
    """Filters of the user update query."""


class UserDeleteQueryFilter(
    UserQueryFilterName,
    UserQueryFilterEmail,
):
    """Filters of the user delete query."""
