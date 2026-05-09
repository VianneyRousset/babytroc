from dataclasses import dataclass


@dataclass(frozen=True)
class AccountValidated:
    user_id: int
