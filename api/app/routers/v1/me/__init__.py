from . import borrowings, chats, items, liked, loans, me, saved, websocket
from .router import router

router.include_router(
    router=items.router,
    prefix="/items",
)

router.include_router(
    router=chats.router,
    prefix="/chats",
)

router.include_router(
    router=loans.router,
    prefix="/loans",
)

router.include_router(
    router=borrowings.router,
    prefix="/borrowings",
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
    "websocket",
]
