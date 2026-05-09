from babytroc.domains.loan.events import (
    LoanEnded,
    LoanRequestAccepted,
    LoanRequestCancelled,
    LoanRequestCreated,
    LoanRequestRejected,
    LoanStarted,
)
from babytroc.infrastructure.events import on


@on(LoanRequestCreated, critical=False)
async def invalidate_cache_on_request_created(db, event: LoanRequestCreated):
    from babytroc.infrastructure.cache import get_cache
    from babytroc.domains.loan.services.cache import invalidate_loan_request_created

    await invalidate_loan_request_created(
        get_cache(),
        item_id=event.item_id,
        borrower_id=event.borrower_id,
        owner_id=event.owner_id,
    )


@on(LoanRequestAccepted, critical=False)
async def invalidate_cache_on_request_accepted(db, event: LoanRequestAccepted):
    from babytroc.infrastructure.cache import get_cache
    from babytroc.domains.loan.services.cache import invalidate_loan_request_state_changed

    await invalidate_loan_request_state_changed(
        get_cache(),
        item_id=event.item_id,
        borrower_id=event.borrower_id,
        owner_id=event.owner_id,
    )


@on(LoanRequestRejected, critical=False)
async def invalidate_cache_on_request_rejected(db, event: LoanRequestRejected):
    from babytroc.infrastructure.cache import get_cache
    from babytroc.domains.loan.services.cache import invalidate_loan_request_state_changed

    await invalidate_loan_request_state_changed(
        get_cache(),
        item_id=event.item_id,
        borrower_id=event.borrower_id,
        owner_id=event.owner_id,
    )


@on(LoanRequestCancelled, critical=False)
async def invalidate_cache_on_request_cancelled(db, event: LoanRequestCancelled):
    from babytroc.infrastructure.cache import get_cache
    from babytroc.domains.loan.services.cache import invalidate_loan_request_state_changed

    await invalidate_loan_request_state_changed(
        get_cache(),
        item_id=event.item_id,
        borrower_id=event.borrower_id,
        owner_id=event.owner_id,
    )


@on(LoanStarted, critical=False)
async def invalidate_cache_on_loan_started(db, event: LoanStarted):
    from babytroc.infrastructure.cache import get_cache
    from babytroc.domains.loan.services.cache import invalidate_loan_started

    await invalidate_loan_started(
        get_cache(),
        item_id=event.item_id,
        borrower_id=event.borrower_id,
        owner_id=event.owner_id,
    )


@on(LoanEnded, critical=False)
async def invalidate_cache_on_loan_ended(db, event: LoanEnded):
    from babytroc.infrastructure.cache import get_cache
    from babytroc.domains.loan.services.cache import invalidate_loan_ended

    await invalidate_loan_ended(
        get_cache(),
        item_id=event.item_id,
        borrower_id=event.borrower_id,
        owner_id=event.owner_id,
    )
