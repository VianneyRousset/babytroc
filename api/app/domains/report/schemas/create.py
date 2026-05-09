from app.schemas.base import CreateBase

from .base import ReportBase


class ReportCreate(ReportBase, CreateBase):
    message: str
    context: str
