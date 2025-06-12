from sqlalchemy import Select

from app.models.auth import AuthRefreshToken
from app.schemas.base import QueryFilterBase


class AuthRefreshTokenQueryFilter(QueryFilterBase):
    """Filters of the auth refresh_token."""

    user_id: int | None = None

    def apply(self, stmt: Select) -> Select:
        # if user_id is provided, select token with given user_id
        if self.user_id is not None:
            stmt = stmt.where(AuthRefreshToken.user_id == self.user_id)

        return stmt
