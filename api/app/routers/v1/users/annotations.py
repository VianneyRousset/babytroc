from typing import Annotated

from fastapi import Path

user_id_annotation = Annotated[
    int,
    Path(
        title="The ID of the user.",
        ge=0,
    ),
]


item_id_annotation = Annotated[
    int,
    Path(
        title="The ID of the item",
        ge=0,
    ),
]
