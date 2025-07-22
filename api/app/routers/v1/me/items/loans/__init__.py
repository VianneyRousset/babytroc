from . import annotations, read, requests, update
from .router import router

router.include_router(
    router=requests.router,
    prefix="/requests",
)

__all__ = [
    "annotations",
    "read",
    "requests",
    "router",
    "update",
]
