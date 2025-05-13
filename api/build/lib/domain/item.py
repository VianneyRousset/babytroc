def compute_item_available(
    is_blocked: bool,
    active_loans_count: int,
) -> bool:
    if is_blocked or active_loans_count > 0:
        return False

    return True
