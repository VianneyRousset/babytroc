from httpx import AsyncClient

from app.enums import LoanRequestState
from app.schemas.item.read import ItemRead

"""Test loan request state diagram.

         1   ┌───────┐   2
      ┌──────┤pending├────────┐
      │      └───┬───┘        │
      │          │ 3,4,5      │
      ▼          ▼            ▼
┌────────┐ 3 ┌────────┐ 4 ┌─────────┐
│rejected│◄──┤accepted├──►│cancelled│
└────────┘   └───┬────┘   └─────────┘
                 │ 5
                 ▼
             ┌────────┐
             │executed│
             └────────┘
"""


class TestLoanRequestUpdatePath1:
    """Test path 1, pending -> rejected."""

    async def test_path1_pending_rejected(
        self,
        alice_new_item: ItemRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
    ):
        """Test path 1, pending -> rejected."""

        # request item
        resp = await bob_client.post(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}/request"
        )
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # reject loan request
        resp = await alice_client.post(
            f"https://babytroc.ch/api/v1/me/items/{alice_new_item.id}/requests/{request['id']}/reject"
        )
        print(resp.text)
        resp.raise_for_status()

        # check loan request state is "rejected"
        resp = await bob_client.get(
            f"https://babytroc.ch/api/v1/me/borrowings/requests/{request['id']}"
        )
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.rejected


class TestLoanRequestUpdatePath2:
    """Test path 2, pending -> cancelled."""

    async def test_path2_pending_cancelled(
        self,
        alice_new_item: ItemRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
    ):
        """Test path 2, pending -> cancelled."""

        # request item
        resp = await bob_client.post(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}/request"
        )
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # cancel loan request
        resp = await bob_client.delete(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}/request"
        )
        print(resp.text)
        resp.raise_for_status()

        # check loan request state is "cancelled"
        resp = await bob_client.get(
            f"https://babytroc.ch/api/v1/me/borrowings/requests/{request['id']}"
        )
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.cancelled


class TestLoanRequestUpdatePath3:
    """Test path 3, pending -> accepted -> rejected."""

    async def test_path3_pending_accepted_rejected(
        self,
        alice_new_item: ItemRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
    ):
        """Test path 3, pending -> accepted -> rejected."""

        # request item
        resp = await bob_client.post(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}/request"
        )
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # accept loan request
        resp = await alice_client.post(
            f"https://babytroc.ch/api/v1/me/items/{alice_new_item.id}/requests/{request['id']}/accept"
        )
        print(resp.text)
        resp.raise_for_status()

        # check loan request state is "accepted"
        resp = await bob_client.get(
            f"https://babytroc.ch/api/v1/me/borrowings/requests/{request['id']}"
        )
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.accepted

        # reject loan request
        resp = await alice_client.post(
            f"https://babytroc.ch/api/v1/me/items/{alice_new_item.id}/requests/{request['id']}/reject"
        )
        print(resp.text)
        resp.raise_for_status()

        # check loan request state is "reject"
        resp = await bob_client.get(
            f"https://babytroc.ch/api/v1/me/borrowings/requests/{request['id']}"
        )
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.rejected


class TestLoanRequestUpdatePath4:
    """Test path 4, pending -> accepted -> cancelled."""

    async def test_path4_pending_accepted_cancelled(
        self,
        alice_new_item: ItemRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
    ):
        """Test path 4, pending -> accepted -> cancelled."""

        # request item
        resp = await bob_client.post(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}/request"
        )
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # accept loan request
        resp = await alice_client.post(
            f"https://babytroc.ch/api/v1/me/items/{alice_new_item.id}/requests/{request['id']}/accept"
        )
        print(resp.text)
        resp.raise_for_status()

        # check loan request state is "accepted"
        resp = await bob_client.get(
            f"https://babytroc.ch/api/v1/me/borrowings/requests/{request['id']}"
        )
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.accepted

        # cancel loan request
        resp = await bob_client.delete(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}/request"
        )
        print(resp.text)
        resp.raise_for_status()

        # check loan request state is "cancelled"
        resp = await bob_client.get(
            f"https://babytroc.ch/api/v1/me/borrowings/requests/{request['id']}"
        )
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.cancelled


class TestLoanRequestUpdatePath5:
    """Test path 5, pending -> accepted -> executed."""

    async def test_path5_pending_accepted_executed(
        self,
        alice_new_item: ItemRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
        carol_client: AsyncClient,
    ):
        """Test path 5, pending -> accepted -> executed."""

        # request item
        resp = await bob_client.post(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}/request"
        )
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # accept loan request
        resp = await alice_client.post(
            f"https://babytroc.ch/api/v1/me/items/{alice_new_item.id}/requests/{request['id']}/accept"
        )
        print(resp.text)
        resp.raise_for_status()

        # check loan request state is "accepted"
        resp = await bob_client.get(
            f"https://babytroc.ch/api/v1/me/borrowings/requests/{request['id']}"
        )
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.accepted

        # execute loan request
        resp = await bob_client.post(
            f"https://babytroc.ch/api/v1/me/borrowings/requests/{request['id']}/execute"
        )
        print(resp.text)
        resp.raise_for_status()
        loan = resp.json()

        # check loan request state is "executed"
        resp = await bob_client.get(
            f"https://babytroc.ch/api/v1/me/borrowings/requests/{request['id']}"
        )
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.executed

        # check active loan is set in item read for alice
        resp = await alice_client.get(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}"
        )
        resp.raise_for_status()
        item = resp.json()
        assert item["active_loan"]["id"] == loan["id"]

        # check active loan is set in item read for bob
        resp = await bob_client.get(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}"
        )
        resp.raise_for_status()
        item = resp.json()
        assert item["active_loan"]["id"] == loan["id"]

        # check carol does not have access to the active loan
        resp = await carol_client.get(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}"
        )
        resp.raise_for_status()
        item = resp.json()
        assert item["active_loan"] is None, (
            "Carol shouldn't have access to the active loan"
        )


class TestLoanRequestUpdatePendingInvalidTransitions:
    """Test path invalid transitions from pending state."""

    async def test_state_pending_invalid_transitions(
        self,
        alice_new_item: ItemRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
    ):
        """Check invalid transitions from state 'pending' cannot be performed."""

        # request item
        resp = await bob_client.post(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}/request"
        )
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # check loan request state is "pending"
        resp = await bob_client.get(
            f"https://babytroc.ch/api/v1/me/borrowings/requests/{request['id']}"
        )
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.pending

        # check pending loan request cannot be executed
        resp = await bob_client.post(
            f"https://babytroc.ch/api/v1/me/borrowings/requests/{request['id']}/execute"
        )
        assert not resp.is_success


class TestLoanRequestUpdateCancelledInvalidTransitions:
    """Test path invalid transitions from cancelled state."""

    async def test_state_cancelled_invalid_transitions(
        self,
        alice_new_item: ItemRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
    ):
        """Check invalid transitions from state 'cancelled' cannot be performed."""

        # request item
        resp = await bob_client.post(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}/request"
        )
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # cancel loan request
        resp = await bob_client.delete(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}/request"
        )
        resp.raise_for_status()

        # check loan request state is "cancelled"
        resp = await bob_client.get(
            f"https://babytroc.ch/api/v1/me/borrowings/requests/{request['id']}"
        )
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.cancelled

        # check cancelled loan request cannot be accepted
        resp = await alice_client.post(
            f"https://babytroc.ch/api/v1/me/items/{alice_new_item.id}/requests/{request['id']}/accept"
        )
        assert not resp.is_success

        # check cancelled loan request cannot be rejected
        resp = await alice_client.post(
            f"https://babytroc.ch/api/v1/me/items/{alice_new_item.id}/requests/{request['id']}/reject"
        )
        assert not resp.is_success

        # check cancelled loan request cannot be executed
        resp = await bob_client.post(
            f"https://babytroc.ch/api/v1/me/borrowings/requests/{request['id']}/execute"
        )
        assert not resp.is_success


class TestLoanRequestUpdateRejectedInvalidTransitions:
    """Test path invalid transitions from rejected state."""

    async def test_state_rejected_invalid_transitions(
        self,
        alice_new_item: ItemRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
    ):
        """Check invalid transitions from state 'rejected' cannot be performed."""

        # request item
        resp = await bob_client.post(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}/request"
        )
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # reject loan request
        resp = await alice_client.post(
            f"https://babytroc.ch/api/v1/me/items/{alice_new_item.id}/requests/{request['id']}/reject"
        )
        print(resp.text)
        resp.raise_for_status()

        # check loan request state is "rejected"
        resp = await bob_client.get(
            f"https://babytroc.ch/api/v1/me/borrowings/requests/{request['id']}"
        )
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.rejected

        # check rejected loan request cannot be cancelled
        resp = await bob_client.delete(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}/request"
        )
        assert not resp.is_success

        # check rejected loan request cannot be accepted
        resp = await alice_client.post(
            f"https://babytroc.ch/api/v1/me/items/{alice_new_item.id}/requests/{request['id']}/accept"
        )
        assert not resp.is_success

        # check cancelled loan request cannot be executed
        resp = await bob_client.post(
            f"https://babytroc.ch/api/v1/me/borrowings/requests/{request['id']}/execute"
        )
        assert not resp.is_success


class TestLoanRequestUpdateExecutedInvalidTransitions:
    """Test path invalid transitions from executed state."""

    async def test_state_executed_invalid_transitions(
        self,
        alice_new_item: ItemRead,
        alice_client: AsyncClient,
        bob_client: AsyncClient,
    ):
        """Check invalid transitions from state 'executed' cannot be performed."""

        # request item
        resp = await bob_client.post(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}/request"
        )
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # accept loan request
        resp = await alice_client.post(
            f"https://babytroc.ch/api/v1/me/items/{alice_new_item.id}/requests/{request['id']}/accept"
        )
        print(resp.text)
        resp.raise_for_status()

        # execute loan request
        resp = await bob_client.post(
            f"https://babytroc.ch/api/v1/me/borrowings/requests/{request['id']}/execute"
        )
        print(resp.text)
        resp.raise_for_status()

        # check loan request state is "executed"
        resp = await bob_client.get(
            f"https://babytroc.ch/api/v1/me/borrowings/requests/{request['id']}"
        )
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.executed

        # check rejected loan request cannot be cancelled
        resp = await bob_client.delete(
            f"https://babytroc.ch/api/v1/items/{alice_new_item.id}/request"
        )
        assert not resp.is_success

        # check rejected loan request cannot be accepted
        resp = await alice_client.post(
            f"https://babytroc.ch/api/v1/me/items/{alice_new_item.id}/requests/{request['id']}/accept"
        )
        assert not resp.is_success

        # check rejected loan request cannot be rejected
        resp = await alice_client.post(
            f"https://babytroc.ch/api/v1/me/items/{alice_new_item.id}/requests/{request['id']}/reject"
        )
        assert not resp.is_success
