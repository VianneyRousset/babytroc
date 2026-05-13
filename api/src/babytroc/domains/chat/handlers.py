from babytroc.domains.auth.events import AccountValidated
from babytroc.domains.loan.events import (
    LoanEnded,
    LoanRequestAccepted,
    LoanRequestCancelled,
    LoanRequestCreated,
    LoanRequestRejected,
    LoanStarted,
)
from babytroc.infrastructure.events import on


@on(LoanRequestCreated)
async def send_loan_request_created_message(db, event: LoanRequestCreated):
    from babytroc.domains.chat.schemas.base import ChatId
    from babytroc.domains.chat.schemas.send import SendChatMessageLoanRequestCreated
    from babytroc.domains.chat.services.message.create import send_many_chat_messages

    await send_many_chat_messages(
        db=db,
        messages=[
            SendChatMessageLoanRequestCreated(
                chat_id=ChatId.from_values(
                    item_id=event.item_id,
                    borrower_id=event.borrower_id,
                ),
                loan_request_id=event.loan_request_id,
            )
        ],
        ensure_chats=True,
    )


@on(LoanRequestAccepted)
async def send_loan_request_accepted_message(db, event: LoanRequestAccepted):
    from babytroc.domains.chat.schemas.base import ChatId
    from babytroc.domains.chat.schemas.send import SendChatMessageLoanRequestAccepted
    from babytroc.domains.chat.services.message.create import send_many_chat_messages

    await send_many_chat_messages(
        db=db,
        messages=[
            SendChatMessageLoanRequestAccepted(
                chat_id=ChatId.from_values(
                    item_id=event.item_id,
                    borrower_id=event.borrower_id,
                ),
                loan_request_id=event.loan_request_id,
            )
        ],
    )


@on(LoanRequestRejected)
async def send_loan_request_rejected_message(db, event: LoanRequestRejected):
    from babytroc.domains.chat.schemas.base import ChatId
    from babytroc.domains.chat.schemas.send import SendChatMessageLoanRequestRejected
    from babytroc.domains.chat.services.message.create import send_many_chat_messages

    await send_many_chat_messages(
        db=db,
        messages=[
            SendChatMessageLoanRequestRejected(
                chat_id=ChatId.from_values(
                    item_id=event.item_id,
                    borrower_id=event.borrower_id,
                ),
                loan_request_id=event.loan_request_id,
            )
        ],
    )


@on(LoanRequestCancelled)
async def send_loan_request_cancelled_message(db, event: LoanRequestCancelled):
    from babytroc.domains.chat.schemas.base import ChatId
    from babytroc.domains.chat.schemas.send import SendChatMessageLoanRequestCancelled
    from babytroc.domains.chat.services.message.create import send_many_chat_messages

    await send_many_chat_messages(
        db=db,
        messages=[
            SendChatMessageLoanRequestCancelled(
                chat_id=ChatId.from_values(
                    item_id=event.item_id,
                    borrower_id=event.borrower_id,
                ),
                loan_request_id=event.loan_request_id,
            )
        ],
    )


@on(LoanStarted)
async def send_loan_started_message(db, event: LoanStarted):
    from babytroc.domains.chat.schemas.base import ChatId
    from babytroc.domains.chat.schemas.send import SendChatMessageLoanStarted
    from babytroc.domains.chat.services.message.create import send_many_chat_messages

    await send_many_chat_messages(
        db=db,
        messages=[
            SendChatMessageLoanStarted(
                chat_id=ChatId.from_values(
                    item_id=event.item_id,
                    borrower_id=event.borrower_id,
                ),
                loan_id=event.loan_id,
            )
        ],
    )


@on(LoanEnded)
async def send_loan_ended_message(db, event: LoanEnded):
    from babytroc.domains.chat.schemas.base import ChatId
    from babytroc.domains.chat.schemas.send import SendChatMessageLoanEnded
    from babytroc.domains.chat.services.message.create import send_many_chat_messages

    await send_many_chat_messages(
        db=db,
        messages=[
            SendChatMessageLoanEnded(
                chat_id=ChatId.from_values(
                    item_id=event.item_id,
                    borrower_id=event.borrower_id,
                ),
                loan_id=event.loan_id,
            )
        ],
    )


@on(AccountValidated)
async def send_account_validated_notification(db, event: AccountValidated):
    from babytroc.domains.chat.schemas.pubsub import (
        PubsubMessageUpdatedAccountValidation,
    )
    from babytroc.infrastructure.pubsub import get_broadcast, notify_user_after_commit

    notify_user_after_commit(
        db=db,
        broadcast=get_broadcast(),
        user_id=event.user_id,
        message=PubsubMessageUpdatedAccountValidation(validated=True),
    )
