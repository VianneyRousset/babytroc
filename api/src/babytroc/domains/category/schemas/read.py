from babytroc.shared.schemas import ReadBase

from .base import CategoryBase


class CategoryRead(CategoryBase, ReadBase):
    slug: str
    name: str
    parent_slug: str | None
