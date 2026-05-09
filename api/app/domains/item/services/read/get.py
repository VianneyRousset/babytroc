from typing import TYPE_CHECKING

from sqlalchemy import and_, func, literal, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload, undefer

from app.domains.item.errors import ItemNotFoundError
from app.domains.item.filters import (
    select_liked,
    select_owned,
    select_saved,
)
from app.domains.item.models import Item
from app.domains.item.schemas.query import ItemReadQueryFilter
from app.domains.item.schemas.read import ItemRead
from app.domains.loan.enums import LoanRequestState
from app.domains.loan.models import Loan, LoanRequest
from app.infrastructure.cache_keys import TTL_ITEM, key_item

if TYPE_CHECKING:
    from app.infrastructure.cache_client import Cache


async def get_item(
    db: AsyncSession,
    item_id: int,
    *,
    query_filter: ItemReadQueryFilter | None = None,
    client_id: int | None = None,
    cache: "Cache | None" = None,
) -> ItemRead:
    """Get item by id."""

    # Only use cache for anonymous (no client_id) requests
    if cache is not None and client_id is None:
        cached = await cache.get(key_item(item_id))
        if cached is not None:
            return ItemRead.model_validate_json(cached)

    items = await get_many_items(
        db=db,
        item_ids={item_id},
        query_filter=query_filter,
        client_id=client_id,
    )

    result = items[0]

    # Only cache if no client_id (core data without per-user flags)
    if cache is not None and client_id is None:
        await cache.set(key_item(item_id), result.model_dump_json(), ttl=TTL_ITEM)

    return result


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

    active_loan = (
        aliased(
            Loan,
            name="active_loan",
        )
        if client_id is not None
        else literal(None).label("active_loan")
    )

    stmt = select(
        Item,
        select_owned(client_id).label("owned_by_client"),
        select_liked(client_id).label("liked_by_client"),
        select_saved(client_id).label("saved_by_client"),
        active_loan_request_from_client,
        active_loan,
    ).select_from(Item)

    if client_id is not None:
        stmt = (
            stmt.outerjoin(
                active_loan_request_from_client,
                onclause=and_(
                    active_loan_request_from_client.item_id == Item.id,
                    active_loan_request_from_client.borrower_id == client_id,
                    active_loan_request_from_client.state.in_(
                        LoanRequestState.get_active_states()
                    ),
                ),
            )
            .outerjoin(
                active_loan,
                onclause=and_(
                    active_loan.item_id == Item.id,
                    or_(
                        active_loan.borrower_id == client_id,
                        Item.owner_id == client_id,
                    ),
                    func.upper(active_loan.during).is_(None),
                ),
            )
            .options(
                # active_loan_request_from_client -> item -> first_image_name
                selectinload(active_loan_request_from_client.item).undefer(
                    Item.first_image_name
                ),
                selectinload(active_loan_request_from_client.borrower),
                # active_loan -> item -> first_image_name
                selectinload(active_loan.item).undefer(Item.first_image_name),
                # active_loan -> borrower
                selectinload(active_loan.borrower),
                # active_loan -> loan_request -> item -> first_image_name
                selectinload(active_loan.loan_request)
                .selectinload(LoanRequest.item)
                .undefer(Item.first_image_name),
                # active_loan -> loan_request -> borrower
                selectinload(active_loan.loan_request).selectinload(
                    LoanRequest.borrower
                ),
            )
        )

    stmt = stmt.options(
        selectinload(Item.owner),
        selectinload(Item.regions),
        selectinload(Item.images),
        selectinload(Item.categories),
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
                "active_loan": row.active_loan,
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
