from .base import Base


class RegionBase(Base):
    pass


class RegionRead(RegionBase):
    id: int
    name: str
