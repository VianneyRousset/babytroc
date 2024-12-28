from fastapi import Request, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import database as db
from app import services
from app.schemas.chat.query import ChatMessageQueryFilter, ChatQueryFilter
from app.schemas.chat.read import ChatMessageRead, ChatRead
from app.schemas.query import QueryPageOptions

from .annotations import chat_id_annotation, chat_message_id_annotation
from .router import router


# TODO check pagination parameters
@router.get("", status_code=status.HTTP_200_OK)
def list_client_chats(
    request: Request,
    page_options: QueryPageOptions,
    db: Session = Depends(db.get_db_session),
) -> list[ChatRead]:
    """List all chats where the client is a member."""

    client_user_id = services.auth.check_auth(request)

    return services.chat.list_chats(
        db=db,
        query_filter=ChatQueryFilter(
            member_id=client_user_id,
        ),
    )


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
        item_id=chat_id.item_id,
        borrower_id=chat_id.borrower_id,
        query_filter=ChatQueryFilter(
            member_id=client_user_id,
        ),
    )


@router.get("/chat_id}/messages", status_code=status.HTTP_200_OK)
def list_client_chat_messages(
    request: Request,
    chat_id: chat_id_annotation,
    page_options: QueryPageOptions,
    db: Session = Depends(db.get_db_session),
) -> list[ChatMessageRead]:
    """List messages in the chat."""

    client_user_id = services.auth.check_auth(request)

    result = services.chat.list_messages(
        db=db,
        query_filter=ChatMessageQueryFilter(
            item_id=chat_id.item_id,
            borrower_id=chat_id.borrower_id,
            member_id=client_user_id,
        ),
        page_options=page_options,
    )

    return result.data


@router.get(
    "/{chat_id}/messages/{message_id}",
    status_code=status.HTTP_200_OK,
)
def get_client_chat_message_by_id(
    request: Request,
    chat_id: chat_id_annotation,
    message_id: chat_message_id_annotation,
    db: Session = Depends(db.get_db_session),
) -> ChatMessageRead:
    """Get client's chat message by id."""

    client_user_id = services.auth.check_auth(request)

    return services.chat.get_message(
        db=db,
        chat_id=message_id.chat_id,
        query_filter=ChatMessageQueryFilter(
            item_id=chat_id.item_id,
            borrower_id=chat_id.borrower_id,
            member_id=client_user_id,
        ),
    )
