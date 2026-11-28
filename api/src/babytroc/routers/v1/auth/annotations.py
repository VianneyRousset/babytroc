from typing import Annotated

from fastapi import Depends

from .verification import (
    maybe_verify_request_credentials,
    verify_request_credentials,
    verify_request_credentials_admin,
    verify_request_credentials_moderator,
)

client_id_annotation = Annotated[
    int,
    Depends(verify_request_credentials),
]
client_id_annotation_admin = Annotated[
    int,
    Depends(verify_request_credentials_admin),
]
client_id_annotation_moderator = Annotated[
    int, Depends(verify_request_credentials_moderator)
]
maybe_client_id_annotation = Annotated[
    int | None, Depends(maybe_verify_request_credentials)
]
