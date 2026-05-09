from app.shared.schemas import ReadBase

from .base import RegionBase


class RegionRead(RegionBase, ReadBase):
    id: int
    name: str
