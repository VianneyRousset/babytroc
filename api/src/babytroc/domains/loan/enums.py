from babytroc.shared.enums import EnumWithMetadata


class LoanRequestState(int, EnumWithMetadata):
    pending = 1
    cancelled = 2
    accepted = 3
    rejected = 4
    executed = 5

    @classmethod
    def get_active_states(cls) -> set["LoanRequestState"]:
        return {cls.pending, cls.accepted}

    @classmethod
    def get_inactive_states(cls) -> set["LoanRequestState"]:
        return set(LoanRequestState) - cls.get_active_states()
