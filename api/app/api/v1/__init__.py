from fastapi import APIRouter

from . import items, users

__all__ = ["users", "items"]


router = APIRouter(
    prefix="/v1",
)

router.include_router(items.router)
router.include_router(users.router)
