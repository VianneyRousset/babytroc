def stars_gain_when_adding_item(added_items_count: int) -> int:
    """Compute the number of stars won when adding `added_items_count` items."""

    if not isinstance(added_items_count, int):
        msg = f"added_items_count must be an integer, got {type(added_items_count)}."
        raise ValueError(msg)

    return 20 * added_items_count
