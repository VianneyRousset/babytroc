from httpx import AsyncClient

from babytroc.domains.item.schemas.read import ItemRead
from babytroc.domains.loan.schemas.read import LoanRead


class TestItemAvailabilityWithLoans:
    """Test that Item.available reflects active loan state correctly.

    Regression: Item.has_active_loan column_property checked
    func.upper(Loan.during).is_not(None) — which matches *ended* loans
    (upper bound set), not active ones (upper bound NULL). This inverts
    both has_active_loan and available.
    """

    async def test_item_available_before_loan(
        self,
        alice_client: AsyncClient,
        alice_new_item: ItemRead,
    ):
        """An item with no loans should be available."""

        resp = await alice_client.get(f"/api/v1/me/items/{alice_new_item.id}")
        resp.raise_for_status()
        item = ItemRead.model_validate(resp.json())

        assert item.available is True

    async def test_item_unavailable_during_active_loan(
        self,
        alice_client: AsyncClient,
        alice_new_item: ItemRead,
        bob_new_loan_of_alice_new_item: LoanRead,
    ):
        """An item with an active loan should NOT be available."""

        assert bob_new_loan_of_alice_new_item.active

        resp = await alice_client.get(f"/api/v1/me/items/{alice_new_item.id}")
        resp.raise_for_status()
        item = ItemRead.model_validate(resp.json())

        assert item.available is False

    async def test_item_available_after_loan_ended(
        self,
        alice_client: AsyncClient,
        alice_new_item: ItemRead,
        bob_new_loan_of_alice_new_item: LoanRead,
    ):
        """An item should become available again after its loan ends."""

        loan_id = bob_new_loan_of_alice_new_item.id

        # end the loan
        resp = await alice_client.post(f"/api/v1/me/loans/{loan_id}/end")
        resp.raise_for_status()
        ended_loan = LoanRead.model_validate(resp.json())
        assert not ended_loan.active

        # check item is available again
        resp = await alice_client.get(f"/api/v1/me/items/{alice_new_item.id}")
        resp.raise_for_status()
        item = ItemRead.model_validate(resp.json())

        assert item.available is True
