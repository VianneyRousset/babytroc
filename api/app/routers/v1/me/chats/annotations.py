from typing import Annotated

from fastapi import APIRouter, Path

router = APIRouter()


chat_id_annotation = Annotated[
    str,
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
