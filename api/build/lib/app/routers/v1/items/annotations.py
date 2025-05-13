from typing import Annotated

from fastapi import Path

item_id_annotation = Annotated[
    int,
    Path(
        title="The ID of the item",
        ge=0,
    ),
]
