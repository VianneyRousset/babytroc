from app.schemas.base import ReadBase

from .base import RegionBase


class RegionRead(RegionBase, ReadBase):
    id: int
    name: str
