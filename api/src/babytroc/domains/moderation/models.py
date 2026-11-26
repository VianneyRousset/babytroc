from sqlalchemy import (
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from babytroc.domains.moderation.enums import ModerationReportType
from babytroc.shared.models import Base, CreationDate, IntegerIdentifier


class ModerationReport(IntegerIdentifier, CreationDate, Base):
    __tablename__ = "moderation_report"

    description: Mapped[str] = mapped_column(
        String,
    )

    report_type: Mapped[ModerationReportType] = mapped_column(
        Enum(ModerationReportType),
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

    saved_info: Mapped[dict] = mapped_column(
        JSONB,
    )

    context: Mapped[dict] = mapped_column(
        JSONB,
    )
