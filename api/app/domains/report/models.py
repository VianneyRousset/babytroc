from sqlalchemy import (
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.domains.report.enums import ReportType
from app.shared.models import Base, CreationDate, IntegerIdentifier


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

    saved_info: Mapped[str] = mapped_column(
        String,
    )

    context: Mapped[str] = mapped_column(
        String,
    )
