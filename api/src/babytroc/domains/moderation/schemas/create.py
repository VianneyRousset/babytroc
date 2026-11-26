from typing import Any

from babytroc.shared.schemas import CreateBase

from .base import ModerationReportBase


class ModerationReportCreate(ModerationReportBase, CreateBase):
    message: str
    context: dict[str, Any]
