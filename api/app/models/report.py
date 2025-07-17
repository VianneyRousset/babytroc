from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.enums import ReportType

from .base import Base, CreationDate, IntegerIdentifier


class Report(IntegerIdentifier, CreationDate, Base):
    __tablename__ = "report"

    description: Mapped[str] = mapped_column(
        String,
    )

    report_type: Mapped[ReportType] = mapped_column(
        Enum(ReportType),
    )

    created_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "user.id",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
    )

    creation_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    saved_info: Mapped[str] = mapped_column(
        String,
    )

    context: Mapped[str] = mapped_column(
        String,
    )
