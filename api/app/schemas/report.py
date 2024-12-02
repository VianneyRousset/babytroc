from .base import Base


class ReportBase(Base):
    pass


class ReportCreate(ReportBase):
    message: str
    context: str
