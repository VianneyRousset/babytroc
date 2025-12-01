import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import UUID

from app.models.base import Base, CreationDate


class AuthRefreshToken(CreationDate, Base):
    __tablename__ = "auth_refresh_token"

    token: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        index=True,
        unique=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "user.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    invalidated: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("false"),
    )


class AuthAccountPasswordResetAuthorization(CreationDate, Base):
    __tablename__ = "auth_account_password_reset_authorization"

    authorization_code: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        index=True,
        unique=True,
        server_default=text("uuidv4()"),
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "user.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    invalidated: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("false"),
    )
