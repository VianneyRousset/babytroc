from fastapi import APIRouter

from . import admins, moderators

router = APIRouter()

router.include_router(
    router=admins.router,
    prefix="/admins",
)

router.include_router(
    router=moderators.router,
    prefix="/moderators",
)
