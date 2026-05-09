from typing import Annotated

from fastapi import Path

loan_id_annotation = Annotated[
    int,
    Path(
        title="The ID of the loan.",
        ge=0,
    ),
]
