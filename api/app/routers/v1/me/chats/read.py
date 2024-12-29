from typing import Annotated

from fastapi import Query, Request, Response, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import database as db
from app import services
from app.schemas.chat.api import ChatApiQuery, ChatMessageApiQuery
from app.schemas.chat.base import ChatId
from app.schemas.chat.query import ChatMessageQueryFilter, ChatQueryFilter
from app.schemas.chat.read import ChatMessageRead, ChatRead
from app.schemas.query import QueryPageOptions
from app.utils import set_query_param

from .annotations import chat_id_annotation, message_id_annotation
from .router import router


@router.get("", status_code=status.HTTP_200_OK)
def list_client_chats(
    request: Request,
    response: Response,
    query: Annotated[ChatApiQuery, Query()],
    db: Session = Depends(db.get_db_session),
) -> list[ChatRead]:
    """List all chats where the client is a member."""

    cursor_chat_id = None if query.cid is None else ChatId.from_str(query.cid)

    client_user_id = services.auth.check_auth(request)

    result = services.chat.list_chats(
        db=db,
        query_filter=ChatQueryFilter(
            member_id=client_user_id,
            item_id=query.item,
            borrower_id=query.borrower,
            owner_id=query.owner,
        ),
        page_options=QueryPageOptions(
            limit=query.n,
            order=["last_message_id", "item_id", "borrower_id"],
            cursor={
                "last_message_id": query.clm,
                "item_id": cursor_chat_id.item_id if cursor_chat_id else None,
                "borrower_id": cursor_chat_id.borrower_id if cursor_chat_id else None,
            },
            desc=True,
        ),
    )

    query_params = request.query_params
    next_cursor = result.next_cursor()

    if "last_message_id" in next_cursor:
        query_params = set_query_param(
            query_params, "clm", next_cursor["last_message_id"]
        )

    if "item_id" in next_cursor:
        chat_id = ChatId(
            item_id=next_cursor["item_id"],
            borrower_id=next_cursor["borrower_id"],
        )
        query_params = set_query_param(query_params, "cid", str(chat_id))

    response.headers["Link"] = f'<{request.url.path}?{query_params}>; rel="next"'

    response.headers["X-Total-Count"] = str(result.total_count)

    return result.data


@router.get("/{chat_id}", status_code=status.HTTP_200_OK)
def get_client_chat(
    request: Request,
    chat_id: chat_id_annotation,
    db: Session = Depends(db.get_db_session),
) -> ChatRead:
    """Get client chat info by chat id."""

    client_user_id = services.auth.check_auth(request)

    return services.chat.get_chat(
        db=db,
        chat_id=ChatId.from_str(chat_id),
        query_filter=ChatQueryFilter(
            member_id=client_user_id,
        ),
    )


@router.get("/{chat_id}/messages", status_code=status.HTTP_200_OK)
def list_client_chat_messages(
    request: Request,
    response: Response,
    chat_id: chat_id_annotation,
    query: Annotated[ChatMessageApiQuery, Query()],
    db: Session = Depends(db.get_db_session),
) -> list[ChatMessageRead]:
    """List messages in the chat."""

    chat_id = ChatId.from_str(chat_id)

    client_user_id = services.auth.check_auth(request)

    # check that client is member of the chat
    chat = services.chat.get_chat(
        db=db,
        chat_id=chat_id,
        query_filter=ChatQueryFilter(
            member_id=client_user_id,
        ),
    )

    # get messages in the chat
    result = services.chat.list_messages(
        db=db,
        query_filter=ChatMessageQueryFilter(
            chat_id=chat.id,
            seen=query.seen,
        ),
        page_options=QueryPageOptions(
            limit=query.n,
            order=["message_id"],
            cursor={
                "message_id": query.cid,
            },
            desc=True,
        ),
    )

    query_params = request.query_params
    for k, v in result.next_cursor().items():
        # rename query parameters
        k = {
            "message_id": "cid",
        }[k]

        query_params = set_query_param(query_params, k, v)

    response.headers["Link"] = f'<{request.url.path}?{query_params}>; rel="next"'

    response.headers["X-Total-Count"] = str(result.total_count)

    return result.data


@router.get(
    "/{chat_id}/messages/{message_id}",
    status_code=status.HTTP_200_OK,
)
def get_client_chat_message_by_id(
    request: Request,
    chat_id: chat_id_annotation,
    message_id: message_id_annotation,
    db: Session = Depends(db.get_db_session),
) -> ChatMessageRead:
    """Get client's chat message by id."""

    chat_id = ChatId.from_str(chat_id)

    client_user_id = services.auth.check_auth(request)

    # check that client is member of the chat
    chat = services.chat.get_chat(
        db=db,
        chat_id=chat_id,
        query_filter=ChatQueryFilter(
            member_id=client_user_id,
        ),
    )

    return services.chat.get_message(
        db=db,
        message_id=message_id,
        query_filter=ChatMessageQueryFilter(
            chat_id=chat.id,
        ),
    )
