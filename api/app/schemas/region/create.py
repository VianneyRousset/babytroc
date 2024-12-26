from typing import Optional

from app.schemas.base import CreateBase

from .base import RegionBase


class RegionCreate(RegionBase, CreateBase):
    id: Optional[int] = None
    name: str
