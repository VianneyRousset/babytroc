from typing import Optional

from .base import Base


class RegionBase(Base):
    pass


class RegionCreate(RegionBase):
    id: Optional[int] = None
    name: str


class RegionRead(RegionBase):
    id: int
    name: str
