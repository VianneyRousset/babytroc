from collections.abc import Iterable
from itertools import repeat
from typing import cast

from sqlalchemy import ColumnClause, insert, select, values
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import LoanRequestState
from app.errors.loan import LoanRequestAlreadyExistsError, LoanRequestOwnItemError
from app.models.item import Item
from app.models.loan import LoanRequest
from app.schemas.chat.base import ChatId
from app.schemas.chat.send import SendChatMessageLoanRequestCreated
from app.schemas.loan.base import ItemBorrowerId
from app.schemas.loan.query import LoanRequestReadQueryFilter
from app.schemas.loan.read import LoanRequestRead
from app.services.chat import send_many_chat_messages
from app.services.item import get_item, get_many_items
from app.services.loan.request.read import list_loan_requests


async def create_loan_request(
    db: AsyncSession,
    *,
    item_id: int,
    borrower_id: int,
    send_message: bool = True,
) -> LoanRequestRead:
    """Create a loan request."""

    loan_requests = await create_many_loan_requests(
        db=db,
        item_ids=item_id,
        borrower_ids=borrower_id,
        send_messages=send_message,
    )

    return loan_requests[0]


async def create_many_loan_requests(
    db: AsyncSession,
    *,
    loan_requests: set[ItemBorrowerId] | None = None,
    item_ids: int | set[int] | None = None,
    borrower_ids: int | set[int] | None = None,
    send_messages: bool = True,
) -> list[LoanRequestRead]:
    """Create multiple loan requests with the same borrower."""

    loan_requests = _loan_request_creates(
        loan_requests=loan_requests,
        item_ids=item_ids,
        borrower_ids=borrower_ids,
    )

    data = values(
        cast("ColumnClause[int]", LoanRequest.item_id),
        cast("ColumnClause[int]", LoanRequest.borrower_id),
        name="loan_request_data",
    ).data([(req.item_id, req.borrower_id) for req in loan_requests])

    # insert loan request while preventing the borrower to be the owner of the object
    # (implemented using from_select where the source item owner must be different
    # than the borrower)
    stmt = (
        insert(LoanRequest)
        .from_select(
            [LoanRequest.item_id, LoanRequest.borrower_id],  # type: ignore[list-item]
            select(data.c.item_id, data.c.borrower_id)
            .join(Item, Item.id == data.c.item_id)
            .where(Item.owner_id != data.c.borrower_id),
        )
        .returning(LoanRequest)
    )

    # execute
    try:
        async with db.begin_nested():
            inserted_loan_requests = (await db.execute(stmt)).unique().scalars().all()

    # integrity error can be raise:
    # 1. if the borrower does not exist
    # 2. the item does not exist TODO
    # 3. if the loan requests aleady exists
    except IntegrityError as error:
        from app.services.user import get_many_users

        # raise UserNotFoundError if borrower does not exist (1.)
        await get_many_users(
            db=db,
            user_ids={req.borrower_id for req in loan_requests},
        )

        # raise ItemNotFoundError if item does not exist (2.)
        await get_many_items(
            db=db,
            item_ids={req.item_id for req in loan_requests},
        )

        # raise LoanRequestAlreadyExistsError if a loan request already exists (3.)
        existing_active_loan_requests = (
            await list_loan_requests(
                db=db,
                query_filter=LoanRequestReadQueryFilter(
                    item_borrower_id=loan_requests,
                    states=LoanRequestState.get_active_states(),
                ),
            )
        ).data

        if existing_active_loan_requests:
            raise LoanRequestAlreadyExistsError(
                {
                    ItemBorrowerId.from_values(
                        item_id=req.item.id,
                        borrower_id=req.borrower.id,
                    )
                    for req in existing_active_loan_requests
                }
            ) from error

        raise error

    # if not all items created a loan request, it means either:
    # 1. the item is owned by the borrower
    if len(inserted_loan_requests) != len(loan_requests):
        # find missing (item_id, borrower_id)
        missing_loan_requests = loan_requests - {
            ItemBorrowerId.from_values(
                item_id=req.item_id,
                borrower_id=req.borrower_id,
            )
            for req in inserted_loan_requests
        }
        first_missing_loan_request = next(iter(sorted(missing_loan_requests)))

        # raise ItemNotFoundError if the item does not exist
        item = await get_item(
            db=db,
            item_id=first_missing_loan_request.item_id,
        )

        # raise LoanRequestOwnItemError if the item is owned by the borrower (3.)
        if item.owner.id == first_missing_loan_request.borrower_id:
            raise LoanRequestOwnItemError(first_missing_loan_request.item_id)

        msg = (
            "The number of created loan requests does not match the number of given "
            "item ids. The reason is unexpected."
        )
        raise RuntimeError(msg)

    # create messages
    if send_messages:
        await send_many_chat_messages(
            db=db,
            messages=[
                SendChatMessageLoanRequestCreated(
                    chat_id=ChatId.from_values(
                        item_id=loan_request.item_id,
                        borrower_id=loan_request.borrower.id,
                    ),
                    loan_request_id=loan_request.id,
                )
                for loan_request in inserted_loan_requests
            ],
            ensure_chats=True,
        )

    return [
        LoanRequestRead.model_validate(loan_request)
        for loan_request in inserted_loan_requests
    ]


def _loan_request_creates(
    loan_requests: set[ItemBorrowerId] | None = None,
    item_ids: int | set[int] | None = None,
    borrower_ids: int | set[int] | None = None,
) -> set[ItemBorrowerId]:
    """Return a list of loan request creates from arguments."""

    if loan_requests is None:
        if isinstance(item_ids, int) and isinstance(borrower_ids, int):
            return {
                ItemBorrowerId.from_values(
                    item_id=item_ids,
                    borrower_id=borrower_ids,
                )
            }

        elif isinstance(item_ids, int) and isinstance(borrower_ids, Iterable):
            return {
                ItemBorrowerId.from_values(
                    item_id=item_id,
                    borrower_id=borrower_id,
                )
                for item_id, borrower_id in zip(
                    repeat(item_ids),
                    borrower_ids,
                    strict=False,
                )
            }

        elif isinstance(item_ids, Iterable) and isinstance(borrower_ids, int):
            return {
                ItemBorrowerId.from_values(
                    item_id=item_id,
                    borrower_id=borrower_id,
                )
                for item_id, borrower_id in zip(
                    item_ids,
                    repeat(borrower_ids),
                    strict=False,
                )
            }

        elif item_ids is None:
            msg = "Missing item_ids argument"
            raise ValueError(msg)

        elif borrower_ids is None:
            msg = "Missing borrower_ids argument"
            raise ValueError(msg)

        elif isinstance(item_ids, Iterable) and isinstance(borrower_ids, Iterable):
            msg = (
                "Ambiguous call, `item_ids` and `borrower_ids` cannot be both "
                "iterables. Please use `loan_requests` to specify multiple items and "
                "borrowers."
            )
            raise TypeError(msg)

        else:
            msg = (
                "Invalid input arguments `item_ids` and `borrower_ids`. Got "
                f"{item_ids} and {borrower_ids}"
            )
            raise TypeError(msg)

    return loan_requests
