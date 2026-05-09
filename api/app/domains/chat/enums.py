from app.shared.enums import EnumWithMetadata


class ChatMessageType(int, EnumWithMetadata):
    text = 1
    loan_request_created = 2
    loan_request_cancelled = 3
    loan_request_accepted = 4
    loan_request_rejected = 5
    loan_started = 6
    loan_ended = 7
    item_not_available = 8
    item_available = 9
