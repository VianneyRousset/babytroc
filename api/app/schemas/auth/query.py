from app.models.auth import AuthRefreshToken
from app.schemas.base import QueryFilter, StatementT


class AuthRefreshTokenQueryFilter(QueryFilter):
    """Filter auth refresh tokens by user."""

    user_id: int | None = None

    def _filter(self, stmt: StatementT) -> StatementT:
        return super()._filter(
            stmt.where(AuthRefreshToken.user_id == self.user_id)
            if self.user_id is not None
            else stmt
        )


class AuthRefreshTokenReadQueryFilter(AuthRefreshTokenQueryFilter):
    """Filter of the auth refresh token read query."""


class AuthRefreshTokenUpdateQueryFilter(AuthRefreshTokenQueryFilter):
    """Filter of the auth refresh token update query."""


class AuthRefreshTokenDeleteQueryFilter(AuthRefreshTokenQueryFilter):
    """Filter of the auth refresh token delete query."""
