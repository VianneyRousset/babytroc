from fastapi import APIRouter

from . import categories, regions

router = APIRouter()
router.include_router(regions.router)
router.include_router(categories.router)
