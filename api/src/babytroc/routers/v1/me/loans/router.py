from fastapi import APIRouter

from . import requests

router = APIRouter()

# sub-router is included here to prevail on `/{loan_id}/` routes
router.include_router(
    router=requests.router,
    prefix="/requests",
)
