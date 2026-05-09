from app.schemas.base import UpdateBase

from .base import RegionBase


class RegionUpdate(RegionBase, UpdateBase):
    name: str
