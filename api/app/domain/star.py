def get_stars_gain_when_adding_item(new_items_count: int) -> int:
    """Compute the number of stars won when adding `new_items_count` items."""

    if not isinstance(new_items_count, int):
        msg = f"new_items_count is to be an integer, got {type(new_items_count)}."
        raise ValueError(msg)

    return 20 * new_items_count
