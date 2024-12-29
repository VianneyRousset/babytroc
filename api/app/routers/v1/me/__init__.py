from . import borrowings, chats, items, liked, loans, me, saved
from .router import router

router.include_router(
    router=items.router,
    prefix="/items",
)

router.include_router(
    router=chats.router,
    prefix="/chats",
)


__all__ = [
    "borrowings",
    "chats",
    "items",
    "liked",
    "loans",
    "me",
    "router",
    "router",
    "saved",
]
