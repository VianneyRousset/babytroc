from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.enums import ReportType

from .base import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(alway=True),
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    description: Mapped[str] = mapped_column(
        String,
    )

    report_type: Mapped[ReportType] = mapped_column(
        Enum(ReportType),
    )

    created_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
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
