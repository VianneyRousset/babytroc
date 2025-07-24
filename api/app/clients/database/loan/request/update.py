from collections.abc import Mapping
from typing import Any

from sqlalchemy.orm import Session

from app.models.loan import LoanRequest


def update_loan_request(
    db: Session,
    loan_request: LoanRequest,
    attributes: Mapping[str, Any],
) -> LoanRequest:
    """Update given `attributes` of the loan request `loan_request`."""

    for key, value in attributes.items():
        setattr(loan_request, key, value)

    db.flush()
    db.refresh(loan_request)

    return loan_request
