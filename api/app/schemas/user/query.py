from pydantic import EmailStr
from sqlalchemy import Select

from app.models.user import User
from app.schemas.base import QueryFilterBase


class UserQueryFilter(QueryFilterBase):
    """Filters of the user."""

    name: str | None = None
    email: EmailStr | None = None

    def apply(self, stmt: Select) -> Select:
        if self.name is not None:
            stmt = stmt.where(User.name == self.name)
        if self.email is not None:
            stmt = stmt.where(User.email == self.email)

        return stmt
