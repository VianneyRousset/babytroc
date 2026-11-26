from dataclasses import dataclass
from typing import Self

from .enums import ModerationReportType
from .models import ModerationReport


@dataclass(frozen=True)
class ModerationReportCreated:
    moderation_report_id: int
    description: str
    report_type: ModerationReportType
    saved_info: dict
    context: dict

    @classmethod
    def from_report(cls, report: ModerationReport) -> Self:
        return cls(
            moderation_report_id=report.id,
            description=report.description,
            report_type=report.report_type,
            saved_info=report.saved_info,
            context=report.context,
        )
