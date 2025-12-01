from datetime import UTC, datetime, timedelta

from httpx import AsyncClient

from app.schemas.item.read import ItemRead
from app.schemas.loan.read import LoanRead, LoanRequestRead
from app.schemas.user.private import UserPrivateRead


class TestLoanUpdate:
    """Tests loans update."""

    async def test_end_loan(
        self,
        bob_new_loan_for_alice_special_item: LoanRequestRead,
        alice: UserPrivateRead,
        bob: UserPrivateRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
        carol_client: AsyncClient,
        alice_special_item: ItemRead,
    ):
        """Check an active loan can be ended.
        - Check only Alice can end the loan.
        - Check an inactive loan cannot be ended.
        """

        loan_id = bob_new_loan_for_alice_special_item.id

        # check only alice can end the loan
        assert (
            await bob_client.post(f"https://babytroc.ch/api/v1/me/loans/{loan_id}/end")
        ).is_error
        assert (
            await bob_client.post(
                f"https://babytroc.ch/api/v1/me/borrowing/{loan_id}/end"
            )
        ).is_error
        assert (
            await carol_client.post(
                f"https://babytroc.ch/api/v1/me/loans/{loan_id}/end"
            )
        ).is_error
        assert (
            await carol_client.post(
                f"https://babytroc.ch/api/v1/me/borrowing/{loan_id}/end"
            )
        ).is_error

        #  loan request
        resp = await alice_client.post(
            f"https://babytroc.ch/api/v1/me/loans/{loan_id}/end"
        )
        print(resp.text)
        resp.raise_for_status()
        loan = LoanRead.model_validate(resp.json())

        # check item
        assert loan.item.id == alice_special_item.id

        # check owner and borrower
        assert loan.owner.id == alice.id
        assert loan.borrower.id == bob.id

        # check chat
        assert loan.chat_id == bob_new_loan_for_alice_special_item.chat_id

        # check during and active
        start, stop = loan.during
        assert start is not None
        assert abs(start - datetime.now(UTC)) < timedelta(minutes=5)
        assert stop is not None
        assert abs(stop - datetime.now(UTC)) < timedelta(minutes=5)
        assert not loan.active
