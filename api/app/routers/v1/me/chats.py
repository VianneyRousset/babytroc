from typing import Annotated, Optional

from fastapi import APIRouter, Body, Path, Query, Request, WebSocket, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import database as db
from app import services
from app.report import ReportCreate
from app.schemas.chat import ChatMessageRead, ChatRead, ChatsListRead

router = APIRouter()

chat_id_annotation = Annotated[
    int,
    Path(
        title="The ID of the chat.",
        ge=0,
    ),
]

chat_message_id_annotation = Annotated[
    int,
    Path(
        title="The ID of the chat message.",
        ge=0,
    ),
]


@router.get("/chats", status_code=status.HTTP_200_OK)
def list_client_chats(
    request: Request,
    db: Session = Depends(db.get_session),
) -> ChatsListRead:
    """List all chats and all messages that have not been seen."""

    client_user_id = services.auth.check_auth(request)

    return services.chats.get_user_chats_list(
        db=db,
        user_id=client_user_id,
    )


@router.websocket("/chats/ws")
def get_client_chats_websocket(
    request: Request,
    websocket: WebSocket,
):
    """Get client's chats websocket with new messages."""
    # TODO subscribe and read redis new messages from clients


@router.get("/chats/{chat_id}", status_code=status.HTTP_200_OK)
def get_client_chat_by_id(
    request: Request,
    chat_id: chat_id_annotation,
    db: Session = Depends(db.get_session),
) -> ChatRead:
    """Read client chat info by chat id."""

    client_user_id = services.auth.check_auth(request)

    return services.chats.get_user_chat_by_id(
        db=db,
        user_id=client_user_id,
        chat_id=chat_id,
    )


@router.get("/chats/{chat_id}/messages", status_code=status.HTTP_200_OK)
def list_client_chat_messages(
    request: Request,
    chat_id: chat_id_annotation,
    before: Annotated[
        Optional[int],
        Query(
            title="Select item with id strictly before this one",
        ),
    ] = None,
    count: Annotated[
        Optional[int],
        Query(
            title="Maximum number of messages to return",
            ge=0,
        ),
    ] = None,
    db: Session = Depends(db.get_session),
) -> ChatMessageRead:
    """List messages in the chat ordered by inversed id (newer first)."""

    client_user_id = services.auth.check_auth(request)

    return services.chats.list_user_chat_messages(
        db=db,
        user_id=client_user_id,
        chat_id=chat_id,
        before_message_id=before,
        count=count,
    )


@router.get(
    "/chats/{chat_id}/messages/{message_id}",
    status_code=status.HTTP_200_OK,
)
def get_client_chat_message_by_id(
    request: Request,
    chat_id: chat_id_annotation,
    chat_message_id: chat_message_id_annotation,
    db: Session = Depends(db.get_session),
) -> ChatMessageRead:
    """Get client's chat message by id."""

    client_user_id = services.auth.check_auth(request)

    return services.chats.get_user_chat_message_by_id(
        db=db,
        user_id=client_user_id,
        chat_id=chat_id,
        chat_message_id=chat_message_id,
    )


@router.post(
    "/chats/{chat_id}/messages/{message_id}/see",
    status_code=status.HTTP_200_OK,
)
def mark_client_chat_message_as_seen(
    request: Request,
    chat_id: chat_id_annotation,
    chat_message_id: chat_message_id_annotation,
    db: Session = Depends(db.get_session),
) -> ChatMessageRead:
    """Mark client's chat message as seen."""

    client_user_id = services.auth.check_auth(request)

    return services.chats.mark_user_chat_message_as_seen(
        db=db,
        user_id=client_user_id,
        chat_id=chat_id,
        chat_message_id=chat_message_id,
    )


@router.post(
    "/chats/{chat_id}/report",
    status_code=status.HTTP_201_CREATED,
)
def report_client_chat(
    request: Request,
    chat_id: chat_id_annotation,
    report_create: Annotated[
        ReportCreate,
        Body(title="Report fields."),
    ],
    db: Session = Depends(db.get_session),
) -> ChatRead:
    """Report client's chat by id."""

    client_user_id = services.auth.check_auth(request)

    return services.chats.report_user_chat(
        db=db,
        user_id=client_user_id,
        chat_id=chat_id,
        reported_by_user_id=client_user_id,
        report_create=report_create,
    )
