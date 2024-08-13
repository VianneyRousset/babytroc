from sqlalchemy.orm import Session

from app.models.loan import LoanRequest as LoanRequestDB
from app.schemas.loan import LoanRequest, LoanRequestCreation


def request_item(
    session: Session,
    loan_request: LoanRequestCreation,
) -> LoanRequest:
    loan_request = LoanRequestDB(**loan_request.model_dump(exclude_node=True))
    session.add(loan_request)
    session.commit()
    session.refresh()
    return LoanRequest(**loan_request.__dict__)
