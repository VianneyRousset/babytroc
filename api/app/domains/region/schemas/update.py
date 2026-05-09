from app.shared.schemas import UpdateBase

from .base import RegionBase


class RegionUpdate(RegionBase, UpdateBase):
    name: str
