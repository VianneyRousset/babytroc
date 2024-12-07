import enum


class ChatMessageType(enum.Enum):
    text = 1
    request_accept = 2
    request_reject = 3
    loan_start = 4
    loan_stop = 5
    not_available = 6
    available = 7


class ReportType(enum.Enum):
    user = 1
    item = 2
    chat = 3


class LoanRequestState(enum.Enum):
    pending = 1
    accepted = 2
    rejected = 3
    executed = 4
