from sqlalchemy import and_, func, literal, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload, undefer

from app.enums import LoanRequestState
from app.errors.item import ItemNotFoundError
from app.models.item import Item
from app.models.loan import Loan, LoanRequest
from app.schemas.item.query import ItemReadQueryFilter
from app.schemas.item.read import ItemRead

from .selections import (
    select_liked,
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

    active_loan_request_from_client = (
        aliased(
            LoanRequest,
            name="active_loan_request_from_client",
        )
        if client_id is not None
        else literal(None).label("active_loan_request_from_client")
    )

    active_loan_from_client = (
        aliased(
            Loan,
            name="active_loan_from_client",
        )
        if client_id is not None
        else literal(None).label("active_loan_from_client")
    )

    stmt = select(
        Item,
        select_owned(client_id).label("owned_by_client"),
        select_liked(client_id).label("liked_by_client"),
        select_saved(client_id).label("saved_by_client"),
        active_loan_request_from_client,
        active_loan_from_client,
    ).select_from(Item)

    if client_id is not None:
        stmt = stmt.outerjoin(
            active_loan_request_from_client,
            onclause=and_(
                active_loan_request_from_client.item_id == Item.id,
                active_loan_request_from_client.borrower_id == client_id,
                active_loan_request_from_client.state.in_(
                    LoanRequestState.get_active_states()
                ),
            ),
        ).outerjoin(
            active_loan_from_client,
            onclause=and_(
                active_loan_from_client.item_id == Item.id,
                active_loan_from_client.borrower_id == client_id,
                func.upper(active_loan_from_client.during).is_(None),
            ),
        )

    stmt = stmt.options(
        selectinload(Item.owner),
        selectinload(Item.regions),
        selectinload(Item.images),
    )

    stmt = query_filter.filter_read(stmt.where(Item.id.in_(item_ids)))

    stmt = stmt.options(undefer(Item.likes_count))

    res = await db.execute(stmt)

    items = [
        ItemRead.model_validate(
            {
                **{
                    k: getattr(row.Item, k)
                    for k in ItemRead.model_fields
                    if hasattr(row.Item, k)
                },
                "owned_by_client": row.owned_by_client,
                "liked_by_client": row.liked_by_client,
                "saved_by_client": row.saved_by_client,
                "active_loan_request_from_client": row.active_loan_request_from_client,
                "active_loan_from_client": row.active_loan_from_client,
                "blocked": row.Item.blocked
                if client_id is not None and row.Item.owner.id == client_id
                else None,
            }
        )
        for row in res.unique()
    ]

    missing_item_ids = item_ids - {item.id for item in items}
    if missing_item_ids:
        key = {"item_ids": missing_item_ids}
        raise ItemNotFoundError(key)

    return items
