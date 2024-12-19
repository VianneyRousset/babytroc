def compute_item_available(
    is_blocked: bool,
    has_active_loan: bool,
) -> bool:
    if is_blocked or has_active_loan:
        return False

    return True
