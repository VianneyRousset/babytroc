from fastapi import APIRouter

from . import borrowings, chats, items, loans

router = APIRouter()

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
