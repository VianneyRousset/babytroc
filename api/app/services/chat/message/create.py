from typing import cast

from sqlalchemy import (
    ColumnClause,
    Enum,
    Integer,
    Text,
    Values,
    case,
    column,
    insert,
    or_,
    select,
    values,
)
from sqlalchemy import (
    cast as sqlcast,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import ChatMessageType
from app.errors.chat import ChatNotFoundError
from app.models.chat import Chat, ChatMessage
from app.models.item import Item
from app.schemas.chat.read import ChatMessageRead
from app.schemas.chat.send import SendChatMessage, SendChatMessageText
from app.services.chat.chat.create import ensure_many_chats


async def send_chat_message(
    db: AsyncSession,
    message: SendChatMessage,
    *,
    ensure_chat: bool = False,
) -> ChatMessageRead:
    chat_messages = await send_many_chat_messages(
        db=db,
        messages=[message],
        ensure_chats=ensure_chat,
    )

    return chat_messages[0]


async def send_many_chat_messages(
    db: AsyncSession,
    messages: list[SendChatMessage],
    *,
    ensure_chats: bool = False,
) -> list[ChatMessageRead]:
    """
    Insert all the given chat messages.

    If `ensure_chats` is True, all chat refered by the messages `chat_id` are first
    created if not existing before sending any message.

    Implementation
    --------------
    - The data of the messages to send are converted into a SQL VALUES expression.
    - The `sender_id` value of the inserted row are computed using an SQL CASE
      expression depending on the value of `message_type` (e.g. for a
      `loan_request_created` message, the `sender_id` is set to be the `borrower_id`).
      Only `text` messages use the given `sender_id` in the inserted row.
    - The data also specifies a generated `order` column to preserve the order of the
      inserted rows.
    """

    # check membership for text messages (user-supplied sender_id)
    text_messages = [msg for msg in messages if isinstance(msg, SendChatMessageText)]
    if text_messages:
        await _check_sender_membership(db, text_messages)

    data = as_sql_values(messages)

    if ensure_chats:
        await ensure_many_chats(
            db=db,
            chat_ids={msg.chat_id for msg in messages},
        )

    sender_id_case_expr = case(
        (
            data.c.message_type == ChatMessageType.text,
            data.c.sender_id,
        ),
        (
            data.c.message_type == ChatMessageType.loan_request_created,
            data.c.borrower_id,
        ),
        (
            data.c.message_type == ChatMessageType.loan_request_cancelled,
            data.c.borrower_id,
        ),
        (
            data.c.message_type == ChatMessageType.loan_request_accepted,
            Item.owner_id,
        ),
        (
            data.c.message_type == ChatMessageType.loan_request_rejected,
            Item.owner_id,
        ),
        (
            data.c.message_type == ChatMessageType.loan_started,
            data.c.borrower_id,
        ),
        (
            data.c.message_type == ChatMessageType.loan_ended,
            Item.owner_id,
        ),
        (
            data.c.message_type == ChatMessageType.item_not_available,
            Item.owner_id,
        ),
        (
            data.c.message_type == ChatMessageType.item_available,
            Item.owner_id,
        ),
        else_=None,
    )

    # insert new message in chat messages
    stmt = (
        insert(ChatMessage)
        .from_select(
            [
                ChatMessage.item_id,  # type: ignore[list-item]
                ChatMessage.borrower_id,  # type: ignore[list-item]
                ChatMessage.message_type,  # type: ignore[list-item]
                ChatMessage.sender_id,  # type: ignore[list-item]
                ChatMessage.text,  # type: ignore[list-item]
                ChatMessage.loan_request_id,  # type: ignore[list-item]
                ChatMessage.loan_id,  # type: ignore[list-item]
            ],
            select(
                data.c.item_id,
                data.c.borrower_id,
                data.c.message_type,
                sender_id_case_expr,
                data.c.text,
                data.c.loan_request_id,
                data.c.loan_id,
            )
            .join(Item, Item.id == data.c.item_id)
            .order_by(data.c.order),
        )
        .returning(ChatMessage)
    )

    try:
        async with db.begin_nested():
            sent_messages = (await db.execute(stmt)).unique().scalars().all()

    # if an IntegrityError is raise, it means either:
    # 1. The refered Chat does not exists (equivalent to item and borrower)
    # 2. The sender user does not exist
    # 3. The loan request does not exist
    # 4. The loan does not exist
    except IntegrityError as error:
        from app.services.chat import get_many_chats
        from app.services.loan import get_many_loan_requests, get_many_loans
        from app.services.user import get_many_users

        # raise ChatNotFoundError if not all chats exist (1.)
        await get_many_chats(
            db=db,
            chat_ids={msg.chat_id for msg in messages},
        )

        # raise UserNotFoundError if not all senders exist (2.)
        await get_many_users(
            db=db,
            user_ids={
                msg.sender_id
                for msg in messages
                if msg.type == ChatMessageType.text and msg.sender_id is not None
            },
        )

        # raise LoanRequestNotFound if not all loan requests exist (3.)
        await get_many_loan_requests(
            db=db,
            loan_request_ids={
                msg.loan_request_id
                for msg in messages
                if msg.type
                in {
                    ChatMessageType.loan_request_created,
                    ChatMessageType.loan_request_cancelled,
                    ChatMessageType.loan_request_accepted,
                    ChatMessageType.loan_request_rejected,
                }
                and msg.loan_request_id is not None
            },
        )

        # raise LoanNotFound if not all loans exist (4.)
        await get_many_loans(
            db=db,
            loan_ids={
                msg.loan_id
                for msg in messages
                if msg.type
                in {
                    ChatMessageType.loan_started,
                    ChatMessageType.loan_ended,
                }
                and msg.loan_id is not None
            },
        )

        raise error

    return [ChatMessageRead.model_validate(msg) for msg in sent_messages]


async def _check_sender_membership(
    db: AsyncSession,
    messages: list[SendChatMessageText],
) -> None:
    """Verify each text message sender is a member of the target chat.

    A chat member is either the borrower or the item owner.
    Raises ChatNotFoundError if the sender is not a member (same semantics
    as the read path — non-members cannot see the chat).
    """

    for msg in messages:
        chat_id = msg.chat_id

        stmt = (
            select(Chat)
            .join(Item, Item.id == Chat.item_id)
            .where(
                Chat.item_id == chat_id.item_id,
                Chat.borrower_id == chat_id.borrower_id,
                or_(
                    Chat.borrower_id == msg.sender_id,
                    Item.owner_id == msg.sender_id,
                ),
            )
        )

        result = await db.execute(stmt)
        if result.first() is None:
            raise ChatNotFoundError(
                key={"chat_id": str(chat_id), "sender_id": msg.sender_id},
            )


def as_sql_values(messages: list[SendChatMessage]) -> Values:
    return values(
        column("order", Integer),
        cast("ColumnClause[int]", ChatMessage.item_id),
        cast("ColumnClause[int]", ChatMessage.borrower_id),
        cast("ColumnClause[ChatMessageType]", ChatMessage.message_type),
        cast("ColumnClause[int]", ChatMessage.sender_id),
        cast("ColumnClause[str]", ChatMessage.text),
        cast("ColumnClause[int]", ChatMessage.loan_request_id),
        cast("ColumnClause[int]", ChatMessage.loan_id),
        name="message_data",
    ).data(
        [
            (
                i,
                sqlcast(msg.chat_id.item_id, Integer),
                sqlcast(msg.chat_id.borrower_id, Integer),
                sqlcast(msg.type, Enum(ChatMessageType)),
                sqlcast(msg.sender_id, Integer),
                sqlcast(msg.text, Text),
                sqlcast(msg.loan_request_id, Integer),
                sqlcast(msg.loan_id, Integer),
            )
            for i, msg in enumerate(messages)
        ]
    )
