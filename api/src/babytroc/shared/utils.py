from sqlalchemy.dialects.postgresql import Range


def integer_range_to_inclusive(ran: Range) -> Range:
    lower = ran.lower
    upper = ran.upper

    if lower is not None and not ran.lower_inc:
        lower = lower + 1

    if upper is not None and not ran.upper_inc:
        upper = upper - 1

    if lower is not None and upper is not None:
        if lower > upper:
            return Range(lower, upper, bounds="[]", empty=True)

    return Range(lower, upper, bounds="[]")
