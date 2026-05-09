from app.shared.schemas import CreateBase

from .base import CategoryBase


class CategoryCreate(CategoryBase, CreateBase):
    slug: str
    name: str
    parent_slug: str | None = None
