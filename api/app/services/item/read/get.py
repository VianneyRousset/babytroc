from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.enums import LoanRequestState
from app.errors.item import ItemNotFoundError
from app.models.item import Item
from app.models.loan import Loan, LoanRequest
from app.schemas.item.query import ItemReadQueryFilter
from app.schemas.item.read import ItemRead

from .selections import (
    select_has_active_loan,
    select_liked,
    select_likes_count,
    select_owned,
    select_saved,
)


async def get_item(
    db: AsyncSession,
    item_id: int,
    *,
    query_filter: ItemReadQueryFilter | None = None,
    client_id: int | None = None,
) -> ItemRead:
    """Get item by id."""

    items = await get_many_items(
        db=db,
        item_ids={item_id},
        query_filter=query_filter,
        client_id=client_id,
    )

    return items[0]


async def get_many_items(
    db: AsyncSession,
    item_ids: set[int],
    *,
    query_filter: ItemReadQueryFilter | None = None,
    client_id: int | None = None,
) -> list[ItemRead]:
    """Get all items with the given item ids.

    Raises ItemNotFoundError if not all items matching criterias exist.
    """

    # default empty query filter
    query_filter = query_filter or ItemReadQueryFilter()

    stmt = select(
        Item,
        select_likes_count().label("likes_count"),
        select_has_active_loan().label("has_active_loan"),
        *(
            [
                select_owned(client_id).label("owned"),
                select_liked(client_id).label("liked"),
                select_saved(client_id).label("saved"),
                LoanRequest,
                Loan,
            ]
            if client_id is not None
            else []
        ),
    )

    if client_id:
        stmt = (
            stmt.outerjoin(
                LoanRequest,
                and_(
                    LoanRequest.item_id == Item.id,
                    LoanRequest.borrower_id == client_id,
                    LoanRequest.state.in_(LoanRequestState.get_active_states()),
                ),
            )
            .outerjoin(
                Loan,
                and_(
                    Loan.item_id == Item.id,
                    Loan.borrower_id == client_id,
                    func.upper(Loan.during).is_(None),
                ),
            )
            .correlate(Item)
        )

    stmt = query_filter.filter_read(
        stmt.where(Item.id.in_(item_ids)).options(
            joinedload(Item.images),
            joinedload(Item.owner),
            joinedload(Item.regions),
        )
    )

    res = await db.execute(stmt)
    rows = res.unique().all()

    items = [
        ItemRead.model_validate(
            {
                "id": row.Item.id,
                "name": row.Item.name,
                "description": row.Item.description,
                "targeted_age_months": row.Item.targeted_age_months,
                "images": [img.name for img in row.Item.images],
                "available": not (row.Item.blocked or row.has_active_loan),
                "owner": row.Item.owner,
                "regions": {reg.id for reg in row.Item.regions},
                "likes_count": row.likes_count,
                "owned": getattr(row, "owned", None),
                "liked": getattr(row, "liked", None),
                "saved": getattr(row, "saved", None),
                "active_loan_request": getattr(row, "active_loan_request", None),
                "active_loan": getattr(row, "active_loan", None),
            }
        )
        for row in rows
    ]

    missing_item_ids = item_ids - {item.id for item in items}
    if missing_item_ids:
        key = {"item_ids": missing_item_ids}
        raise ItemNotFoundError(key)

    return items
