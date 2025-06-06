from collections.abc import Mapping
from typing import Any

from psycopg2.extensions import AsIs
from sqlalchemy.dialects.postgresql import Range
from sqlalchemy.orm import Session

from app.models.loan import Loan, LoanRequest


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


def update_loan(
    db: Session,
    loan: Loan,
    attributes: Mapping[str, Any],
) -> Loan:
    """Update given `attributes` of the loan `loan`."""

    for key, value in attributes.items():
        setattr(loan, key, value)

    db.flush()
    db.refresh(loan)

    return loan


def end_loan(
    db: Session,
    loan: Loan,
) -> Loan:
    """Update upper bound of `loan.during` to `now()`."""

    loan.during = Range(loan.during.lower, AsIs("now()"), bounds="()")

    db.flush()
    db.refresh(loan)

    return loan
