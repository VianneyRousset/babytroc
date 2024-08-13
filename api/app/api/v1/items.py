from fastapi import APIRouter, Request
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import database as db
from app import services
from app.schemas.item import Item
from app.schemas.loan import LoanRequest

router = APIRouter(
    prefix="/items",
)


@router.get("")
async def list_items(
    request: Request,
    session: Session = Depends(db.get_session),
) -> list[Item]:
    return await services.item.list_items(session)


@router.get("{item_id:int}")
def get_item(
    request: Request,
    item_id: int,
    session: Session = Depends(db.get_session),
) -> Item:
    return services.item.get_item(item_id)


@router.post("{item_id:int}/request")
def request_item(
    request: Request,
    item_id: int,
    session: Session = Depends(db.get_session),
) -> LoanRequest:
    return services.loan.request_item(item_id, 0)
