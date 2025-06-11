from typing import Annotated

from fastapi import Depends

from .verification import verify_request_credentials

client_id_annotation = Annotated[int, Depends(verify_request_credentials)]
