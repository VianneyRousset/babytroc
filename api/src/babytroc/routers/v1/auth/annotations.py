from typing import Annotated

from fastapi import Depends

from .verification import maybe_verify_request_credentials, verify_request_credentials

client_id_annotation = Annotated[int, Depends(verify_request_credentials)]
maybe_client_id_annotation = Annotated[
    int | None, Depends(maybe_verify_request_credentials)
]
