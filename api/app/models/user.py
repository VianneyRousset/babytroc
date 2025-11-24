import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    validates,
)
from sqlalchemy.types import UUID, TypeDecorator

from app.utils.hash import HashedStr

from .base import Base, CreationDate, IntegerIdentifier


class HashedString(TypeDecorator):
    """
    String representation of a hashed string.

    Returns a HashedStr when reading.

    Ensure the string is converted to HashedStr
    """

    impl = String
    cache_ok = True

    def process_bind_param(self, value: str | HashedStr | None, dialect) -> str | None:
        if value is None:
            return value
        else:
            return str(HashedStr(value))

    def process_result_value(self, value: str | None, dialect) -> HashedStr | None:
        if value is None:
            return value
        else:
            return HashedStr(hashed=value)


class User(IntegerIdentifier, CreationDate, Base):
    __tablename__ = "user"

    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
    )
    validated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    validation_code: Mapped[uuid.UUID] = mapped_column(
        UUID,
        index=True,
        unique=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
    )
    password_hash: Mapped[HashedStr] = mapped_column(
        HashedString,
    )
    avatar_seed: Mapped[str] = mapped_column(
        String,
        server_default=func.md5(text("random()::text")),
    )

    stars_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    __table_args__ = (CheckConstraint(stars_count >= 0, name="positive_stars_count"),)

    @validates("email")
    def validate_email(self, key, email):
        if "@" not in email:
            msg = f"Invalid email format: {email!r}"
            raise ValueError(msg)
        return email

    def __repr__(self):
        return f"<{self.__class__.__name__} #{self.id!r} {self.email!r} {self.name!r}>"
