from dataclasses import dataclass


@dataclass(frozen=True)
class LoanRequestCreated:
    loan_request_id: int
    item_id: int
    borrower_id: int
    owner_id: int


@dataclass(frozen=True)
class LoanRequestAccepted:
    loan_request_id: int
    item_id: int
    borrower_id: int
    owner_id: int


@dataclass(frozen=True)
class LoanRequestRejected:
    loan_request_id: int
    item_id: int
    borrower_id: int
    owner_id: int


@dataclass(frozen=True)
class LoanRequestCancelled:
    loan_request_id: int
    item_id: int
    borrower_id: int
    owner_id: int


@dataclass(frozen=True)
class LoanStarted:
    loan_id: int
    loan_request_id: int
    item_id: int
    borrower_id: int
    owner_id: int


@dataclass(frozen=True)
class LoanEnded:
    loan_id: int
    item_id: int
    borrower_id: int
    owner_id: int
