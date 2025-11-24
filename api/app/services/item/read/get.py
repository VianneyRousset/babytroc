from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import LoanRequestState
from app.errors.item import ItemNotFoundError
from app.models.item import Item, ItemLike, ItemSave
from app.models.loan import Loan, LoanRequest
from app.schemas.item.query import ItemReadQueryFilter
from app.schemas.item.read import ItemRead
from app.schemas.loan.read import LoanRead, LoanRequestRead


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

    # no client id
    if client_id is None:
        return await _get_many_items_without_client_specific_fields(
            db=db,
            item_ids=item_ids,
            query_filter=query_filter,
        )

    # with client id
    return await _get_many_items_with_client_specific_fields(
        db=db,
        item_ids=item_ids,
        query_filter=query_filter,
        client_id=client_id,
    )


async def _get_many_items_without_client_specific_fields(
    db: AsyncSession,
    item_ids: set[int],
    *,
    query_filter: ItemReadQueryFilter,
) -> list[ItemRead]:
    """Get item tuned without client-specific fields."""

    stmt = query_filter.filter_read(select(Item).where(Item.id.in_(item_ids)))

    items = (await db.execute(stmt)).unique().scalars().all()

    missing_item_ids = item_ids - {item.id for item in items}
    if missing_item_ids:
        key = {"item_ids": missing_item_ids}
        raise ItemNotFoundError(key)

    return [ItemRead.model_validate(item) for item in items]


async def _get_many_items_with_client_specific_fields(
    db: AsyncSession,
    item_ids: set[int],
    *,
    query_filter: ItemReadQueryFilter,
    client_id: int,
) -> list[ItemRead]:
    """Get item tuned with client-specific fields."""

    stmt = query_filter.filter_read(
        select(Item, ItemLike.id, ItemSave.id, LoanRequest, Loan)
        .outerjoin(
            ItemLike, and_(ItemLike.item_id == Item.id, ItemLike.user_id == client_id)
        )
        .outerjoin(
            ItemSave, and_(ItemSave.item_id == Item.id, ItemSave.user_id == client_id)
        )
        .outerjoin(
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
                or_(
                    Loan.borrower_id == client_id,
                    Item.owner_id == client_id,
                ),
                func.upper(Loan.during).is_(None),
            ),
        )
        .where(Item.id.in_(item_ids))
    )

    rows = (await db.execute(stmt)).unique().all()

    items = [
        ItemRead.model_validate(
            {
                **ItemRead.model_validate(item).model_dump(),
                "owned": item.owner_id == client_id,
                "liked": like_id is not None,
                "saved": save_id is not None,
                "active_loan_request": (
                    loan_request and LoanRequestRead.model_validate(loan_request)
                ),
                "active_loan": (loan and LoanRead.model_validate(loan)),
            }
        )
        for item, like_id, save_id, loan_request, loan in rows
    ]

    missing_item_ids = item_ids - {item.id for item in items}
    if missing_item_ids:
        key = {"item_ids": missing_item_ids}
        raise ItemNotFoundError(key)

    return items
