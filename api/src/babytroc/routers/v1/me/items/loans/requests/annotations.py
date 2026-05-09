from typing import Annotated

from fastapi import Path

loan_request_id_annotation = Annotated[
    int,
    Path(
        title="The ID of the loan request.",
        ge=0,
    ),
]
