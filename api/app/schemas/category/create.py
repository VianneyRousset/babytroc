from app.schemas.base import CreateBase

from .base import CategoryBase


class CategoryCreate(CategoryBase, CreateBase):
    slug: str
    name: str
    parent_slug: str | None = None
