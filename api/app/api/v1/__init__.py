from fastapi import APIRouter

from . import items, users

__all__ = ["users", "items"]


router = APIRouter()

router.include_router(
    router=items.router,
    prefix="/items",
)
router.include_router(
    router=users.router,
    prefix="/users",
)
