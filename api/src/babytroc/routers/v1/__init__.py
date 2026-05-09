from fastapi import APIRouter

from . import auth, images, items, me, users, utils

__all__ = ["auth", "items", "me", "users", "utils"]


router = APIRouter()

router.include_router(
    router=auth.router,
    prefix="/auth",
)

router.include_router(
    router=items.router,
    prefix="/items",
)

router.include_router(
    router=me.router,
    prefix="/me",
)

router.include_router(
    router=users.router,
    prefix="/users",
)

router.include_router(
    router=utils.router,
    prefix="/utils",
)


router.include_router(
    router=images.router,
    prefix="/images",
)
