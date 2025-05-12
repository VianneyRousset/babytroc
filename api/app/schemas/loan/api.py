from pydantic import Field

from app.enums import LoanRequestState
from app.schemas.base import ApiQueryBase


class LoanRequestApiQuery(ApiQueryBase):
    # state
    active: bool | None = Field(
        title="Active loan requests",
        description="Only return pending and accepted loan requests.",
        default=None,
    )

    @property
    def states(self) -> None | set[LoanRequestState]:
        if self.active is None:
            return None

        active_states = {LoanRequestState.pending, LoanRequestState.accepted}

        if self.active:
            return active_states

        return set(LoanRequestState) - active_states


class LoanApiQuery(ApiQueryBase):
    # item_id
    item: int | None = Field(
        title="Loaned item",
        description="Only return loan with this item ID.",
        ge=0,
        default=None,
    )

    # active
    active: bool | None = Field(
        title="Active",
        description="Only return active loans.",
        default=None,
    )
