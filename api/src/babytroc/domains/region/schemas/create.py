from babytroc.shared.schemas import CreateBase

from .base import RegionBase


class RegionCreate(RegionBase, CreateBase):
    id: int | None = None
    name: str
