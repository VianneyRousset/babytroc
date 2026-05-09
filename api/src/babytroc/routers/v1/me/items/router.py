from fastapi import APIRouter

from . import loans

router = APIRouter()

router.include_router(
    router=loans.router,
    prefix="/{item_id}/loans",
)
