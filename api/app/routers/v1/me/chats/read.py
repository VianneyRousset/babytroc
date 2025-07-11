from typing import Annotated

from fastapi import Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db_session
from app.routers.v1.auth import client_id_annotation
from app.schemas.chat.api import ChatApiQuery, ChatMessageApiQuery
from app.schemas.chat.query import ChatMessageQueryFilter, ChatQueryFilter
from app.schemas.chat.read import ChatMessageRead, ChatRead

from .annotations import chat_id_annotation, message_id_annotation
from .router import router


@router.get("", status_code=status.HTTP_200_OK)
def list_client_chats(
    client_id: client_id_annotation,
    request: Request,
    response: Response,
    query: Annotated[ChatApiQuery, Query()],
    db: Annotated[Session, Depends(get_db_session)],
) -> list[ChatRead]:
    """List all chats where the client is a member."""

    result = services.chat.list_chats(
        db=db,
        query_filter=ChatQueryFilter.model_validate(
            {
                **query.chat_query_filter.model_dump(),
                "member_id": client_id,
            }
        ),
        page_options=query.chat_query_page_options,
    )

    result.set_response_headers(response, request)

    return result.data


@router.get("/{chat_id}", status_code=status.HTTP_200_OK)
def get_client_chat(
    client_id: client_id_annotation,
    chat_id: chat_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
) -> ChatRead:
    """Get client chat info by chat id."""

    return services.chat.get_chat(
        db=db,
        chat_id=chat_id,
        query_filter=ChatQueryFilter(
            member_id=client_id,
        ),
    )


@router.get("/{chat_id}/messages", status_code=status.HTTP_200_OK)
def list_client_chat_messages(
    client_id: client_id_annotation,
    request: Request,
    response: Response,
    chat_id: chat_id_annotation,
    query: Annotated[ChatMessageApiQuery, Query()],
    db: Annotated[Session, Depends(get_db_session)],
) -> list[ChatMessageRead]:
    """List messages in the chat."""

    # check that client is member of the chat
    chat = services.chat.get_chat(
        db=db,
        chat_id=chat_id,
        query_filter=ChatQueryFilter(
            member_id=client_id,
        ),
    )

    # get messages in the chat
    result = services.chat.list_messages(
        db=db,
        query_filter=ChatMessageQueryFilter.model_validate(
            {
                **query.chat_message_query_filter.model_dump(),
                "chat_id": chat.id,
            }
        ),
        page_options=query.chat_message_query_page_options,
    )

    result.set_response_headers(response, request)

    return result.data


@router.get(
    "/{chat_id}/messages/{message_id}",
    status_code=status.HTTP_200_OK,
)
def get_client_chat_message_by_id(
    client_id: client_id_annotation,
    chat_id: chat_id_annotation,
    message_id: message_id_annotation,
    db: Annotated[Session, Depends(get_db_session)],
) -> ChatMessageRead:
    """Get client's chat message by id."""

    # check that client is member of the chat
    chat = services.chat.get_chat(
        db=db,
        chat_id=chat_id,
        query_filter=ChatQueryFilter(
            member_id=client_id,
        ),
    )

    return services.chat.get_message(
        db=db,
        message_id=message_id,
        query_filter=ChatMessageQueryFilter(
            chat_id=chat.id,
        ),
    )
