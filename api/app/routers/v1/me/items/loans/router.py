from fastapi import APIRouter

from . import requests

router = APIRouter()
router.include_router(
    router=requests.router,
    prefix="/requests",
)
