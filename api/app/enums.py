import enum


class ChatMessageType(enum.Enum):
    text = 1
    loan_request_created = 2
    loan_request_canceled = 3
    loan_request_accepted = 4
    loan_request_rejected = 5
    loan_started = 6
    loan_ended = 7
    item_not_available = 9
    item_available = 9


class ReportType(enum.Enum):
    user = 1
    item = 2
    chat = 3


class LoanRequestState(enum.Enum):
    pending = 1
    canceled = 2
    accepted = 3
    rejected = 4
    executed = 5


class ItemQueryAvailability(enum.Enum):
    yes = "y"
    no = "n"
    all = "a"
