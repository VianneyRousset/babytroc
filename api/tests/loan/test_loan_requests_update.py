from fastapi.testclient import TestClient

from app.enums import LoanRequestState
from app.schemas.item.read import ItemRead


class TestLoanRequestUpdate:
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

    def test_path1_pending_rejected(
        self,
        alice_new_item: ItemRead,
        alice_client: TestClient,
        bob_client: TestClient,
    ):
        """Test path 1, reject a loan request."""

        # request item
        resp = bob_client.post(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # reject loan request
        resp = alice_client.post(
            f"/v1/me/items/{alice_new_item.id}/requests/{request['id']}/reject"
        )
        print(resp.text)
        resp.raise_for_status()

        # check loan request state is "rejected"
        resp = bob_client.get(f"/v1/me/borrowings/requests/{request['id']}")
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.rejected

    def test_path2_pending_cancelled(
        self,
        alice_new_item: ItemRead,
        alice_client: TestClient,
        bob_client: TestClient,
    ):
        """Test path 2, cancel a loan request."""

        # request item
        resp = bob_client.post(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # cancel loan request
        resp = bob_client.delete(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        resp.raise_for_status()

        # check loan request state is "cancelled"
        resp = bob_client.get(f"/v1/me/borrowings/requests/{request['id']}")
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.cancelled

    def test_path3_pending_accepted_rejected(
        self,
        alice_new_item: ItemRead,
        alice_client: TestClient,
        bob_client: TestClient,
    ):
        """Test path 3, accept then reject a loan request."""

        # request item
        resp = bob_client.post(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # accept loan request
        resp = alice_client.post(
            f"/v1/me/items/{alice_new_item.id}/requests/{request['id']}/accept"
        )
        print(resp.text)
        resp.raise_for_status()

        # check loan request state is "accepted"
        resp = bob_client.get(f"/v1/me/borrowings/requests/{request['id']}")
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.accepted

        # reject loan request
        resp = alice_client.post(
            f"/v1/me/items/{alice_new_item.id}/requests/{request['id']}/reject"
        )
        print(resp.text)
        resp.raise_for_status()

        # check loan request state is "reject"
        resp = bob_client.get(f"/v1/me/borrowings/requests/{request['id']}")
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.rejected

    def test_path4_pending_accepted_cancelled(
        self,
        alice_new_item: ItemRead,
        alice_client: TestClient,
        bob_client: TestClient,
    ):
        """Test path 4, accept then cancel a loan request."""

        # request item
        resp = bob_client.post(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # accept loan request
        resp = alice_client.post(
            f"/v1/me/items/{alice_new_item.id}/requests/{request['id']}/accept"
        )
        print(resp.text)
        resp.raise_for_status()

        # check loan request state is "accepted"
        resp = bob_client.get(f"/v1/me/borrowings/requests/{request['id']}")
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.accepted

        # cancel loan request
        resp = bob_client.delete(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        resp.raise_for_status()

        # check loan request state is "cancelled"
        resp = bob_client.get(f"/v1/me/borrowings/requests/{request['id']}")
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.cancelled

    def test_path5_pending_accepted_executed(
        self,
        alice_new_item: ItemRead,
        alice_client: TestClient,
        bob_client: TestClient,
    ):
        """Test path 5, accept then execute a loan request."""

        # request item
        resp = bob_client.post(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # accept loan request
        resp = alice_client.post(
            f"/v1/me/items/{alice_new_item.id}/requests/{request['id']}/accept"
        )
        print(resp.text)
        resp.raise_for_status()

        # check loan request state is "accepted"
        resp = bob_client.get(f"/v1/me/borrowings/requests/{request['id']}")
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.accepted

        # execute loan request
        resp = bob_client.post(f"/v1/me/borrowings/requests/{request['id']}/execute")
        print(resp.text)
        resp.raise_for_status()

        # check loan request state is "executed"
        resp = bob_client.get(f"/v1/me/borrowings/requests/{request['id']}")
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.executed

    def test_state_pending_invalid_transitions(
        self,
        alice_new_item: ItemRead,
        alice_client: TestClient,
        bob_client: TestClient,
    ):
        """Check invalid transitions from state 'pending' cannot be performed."""

        # request item
        resp = bob_client.post(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # check loan request state is "pending"
        resp = bob_client.get(f"/v1/me/borrowings/requests/{request['id']}")
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.pending

        # check pending loan request cannot be executed
        resp = bob_client.post(f"/v1/me/borrowings/requests/{request['id']}/execute")
        assert not resp.is_success

    def test_state_cancelled_invalid_transitions(
        self,
        alice_new_item: ItemRead,
        alice_client: TestClient,
        bob_client: TestClient,
    ):
        """Check invalid transitions from state 'cancelled' cannot be performed."""

        # request item
        resp = bob_client.post(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # cancel loan request
        bob_client.delete(f"/v1/items/{alice_new_item.id}/request").raise_for_status()

        # check loan request state is "cancelled"
        resp = bob_client.get(f"/v1/me/borrowings/requests/{request['id']}")
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.cancelled

        # check cancelled loan request cannot be accepted
        resp = alice_client.post(
            f"/v1/me/items/{alice_new_item.id}/requests/{request['id']}/accept"
        )
        assert not resp.is_success

        # check cancelled loan request cannot be rejected
        resp = alice_client.post(
            f"/v1/me/items/{alice_new_item.id}/requests/{request['id']}/reject"
        )
        assert not resp.is_success

        # check cancelled loan request cannot be executed
        resp = bob_client.post(f"/v1/me/borrowings/requests/{request['id']}/execute")
        assert not resp.is_success

    def test_state_rejected_invalid_transitions(
        self,
        alice_new_item: ItemRead,
        alice_client: TestClient,
        bob_client: TestClient,
    ):
        """Check invalid transitions from state 'rejected' cannot be performed."""

        # request item
        resp = bob_client.post(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # reject loan request
        resp = alice_client.post(
            f"/v1/me/items/{alice_new_item.id}/requests/{request['id']}/reject"
        )
        print(resp.text)
        resp.raise_for_status()

        # check loan request state is "rejected"
        resp = bob_client.get(f"/v1/me/borrowings/requests/{request['id']}")
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.rejected

        # check rejected loan request cannot be cancelled
        resp = bob_client.delete(f"/v1/items/{alice_new_item.id}/request")
        assert not resp.is_success

        # check rejected loan request cannot be accepted
        resp = alice_client.post(
            f"/v1/me/items/{alice_new_item.id}/requests/{request['id']}/accept"
        )
        assert not resp.is_success

        # check cancelled loan request cannot be executed
        resp = bob_client.post(f"/v1/me/borrowings/requests/{request['id']}/execute")
        assert not resp.is_success

    def test_state_executed_invalid_transitions(
        self,
        alice_new_item: ItemRead,
        alice_client: TestClient,
        bob_client: TestClient,
    ):
        """Check invalid transitions from state 'executed' cannot be performed."""

        # request item
        resp = bob_client.post(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # accept loan request
        resp = alice_client.post(
            f"/v1/me/items/{alice_new_item.id}/requests/{request['id']}/accept"
        )
        print(resp.text)
        resp.raise_for_status()

        # execute loan request
        resp = bob_client.post(f"/v1/me/borrowings/requests/{request['id']}/execute")
        print(resp.text)
        resp.raise_for_status()

        # check loan request state is "executed"
        resp = bob_client.get(f"/v1/me/borrowings/requests/{request['id']}")
        resp.raise_for_status()
        request = resp.json()
        assert request["state"] == LoanRequestState.executed

        # check rejected loan request cannot be cancelled
        resp = bob_client.delete(f"/v1/items/{alice_new_item.id}/request")
        assert not resp.is_success

        # check rejected loan request cannot be accepted
        resp = alice_client.post(
            f"/v1/me/items/{alice_new_item.id}/requests/{request['id']}/accept"
        )
        assert not resp.is_success

        # check rejected loan request cannot be rejected
        resp = alice_client.post(
            f"/v1/me/items/{alice_new_item.id}/requests/{request['id']}/reject"
        )
        assert not resp.is_success
