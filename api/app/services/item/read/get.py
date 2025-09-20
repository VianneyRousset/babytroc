from sqlalchemy import and_, or_, select, func
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.enums import LoanRequestState
from app.errors.item import ItemNotFoundError
from app.models.item import Item, ItemLike, ItemSave
from app.models.loan import LoanRequest, Loan
from app.schemas.item.query import ItemReadQueryFilter
from app.schemas.item.read import ItemRead
from app.schemas.loan.read import LoanRequestRead, LoanRead


def get_item(
    db: Session,
    item_id: int,
    *,
    query_filter: ItemReadQueryFilter | None = None,
    client_id: int | None = None,
) -> ItemRead:
    """Get item by id."""

    # default empty query filter
    query_filter = query_filter or ItemReadQueryFilter()

    # no client id
    if client_id is None:
        return _get_item_without_client_specific_fields(
            db=db,
            item_id=item_id,
            query_filter=query_filter,
        )

    # with client id
    return _get_item_with_client_specific_fields(
        db=db,
        item_id=item_id,
        query_filter=query_filter,
        client_id=client_id,
    )


def _get_item_without_client_specific_fields(
    db: Session,
    item_id: int,
    *,
    query_filter: ItemReadQueryFilter,
) -> ItemRead:
    """Get item tuned without client-specific fields."""

    stmt = select(Item).where(Item.id == item_id)

    # apply filtering
    stmt = query_filter.filter_read(stmt)

    try:
        item = db.execute(stmt).unique().scalars().one()

    except NoResultFound as error:
        key = query_filter.key | {"id": item_id}
        raise ItemNotFoundError(key) from error

    return ItemRead.model_validate(item)


def _get_item_with_client_specific_fields(
    db: Session,
    item_id: int,
    *,
    query_filter: ItemReadQueryFilter,
    client_id: int,
) -> ItemRead:
    """Get item tuned with client-specific fields."""

    stmt = (
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
        .where(Item.id == item_id)
    )

    # apply filtering
    stmt = query_filter.filter_read(stmt)

    try:
        item, like_id, save_id, loan_request, loan = db.execute(stmt).unique().one()

    except NoResultFound as error:
        key = query_filter.key | {"id": item_id}
        raise ItemNotFoundError(key) from error

    return ItemRead.model_validate(
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
