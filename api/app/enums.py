import enum


class ChatMessageType(enum.Enum):
    text = 1
    loan_request_created = 2
    loan_request_accept = 3
    loan_request_reject = 4
    loan_start = 5
    loan_stop = 6
    not_available = 7
    available = 8


class ReportType(enum.Enum):
    user = 1
    item = 2
    chat = 3


class LoanRequestState(enum.Enum):
    pending = 1
    accepted = 2
    rejected = 3
    executed = 4
