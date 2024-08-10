import db
from fastapi import APIRouter, Request, Response

router = APIRouter(
    prefix="/items",
)


@router.get("")
def list_items() -> list[db.items.Item]:
    return db.items.list_items()


@router.get("{item_id:int}")
def get_item(request: Request, item_id: int) -> db.items.Item:
    return db.items.get_item(item_id)


@router.get("{item_id:int}/request")
def request_item(request: Request, item_id: int) -> db.loans.LoanRequest:
    return db.loans.request_item(item_id, 0)
