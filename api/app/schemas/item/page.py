from typing import Optional

from app.schemas.base import Base


class ItemPage(Base):
    """Data used for pagination of a list of items."""

    limit: Optional[int] = None
    max_words_match_distance: Optional[float] = None
    min_item_id: Optional[int] = None
