import pytest
from fastapi.testclient import TestClient

from app.enums import LoanRequestState, ChatMessageType
from app.schemas.item.read import ItemRead


@pytest.mark.usefixtures("items")
class TestCreateLoanRequest:
    """Tests loan requests."""

    def test_can_request_item(
        self,
        alice_new_item: ItemRead,
        alice_client: TestClient,
        bob_client: TestClient,
    ):
        """Check that a loan request can be created and appears in various lists."""

        # request item
        resp = bob_client.post(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # check loan request appears in borrower's borrowings requests
        resp = bob_client.get("/v1/me/borrowings/requests")
        print(resp.text)
        resp.raise_for_status()
        assert request["id"] in {req["id"] for req in resp.json()}
        bob_client.get(f"/v1/me/borrowings/requests/{request['id']}").raise_for_status()

        # check loan request appears in item's borrowings requests
        resp = alice_client.get(f"/v1/me/items/{alice_new_item.id}/requests")
        print(resp.text)
        resp.raise_for_status()
        assert request["id"] in {item["id"] for item in resp.json()}
        alice_client.get(
            f"/v1/me/items/{alice_new_item.id}/requests/{request['id']}"
        ).raise_for_status()

        # check a chat message has been created for alice
        resp = alice_client.get(f"/v1/me/chats/{request['chat_id']}/messages")
        resp.raise_for_status()
        last_message = resp.json()[0]
        assert last_message["message_type"] == ChatMessageType.loan_request_created

        # check a chat message has been created for bob
        resp = alice_client.get(f"/v1/me/chats/{request['chat_id']}/messages")
        resp.raise_for_status()
        last_message = resp.json()[0]
        assert last_message["message_type"] == ChatMessageType.loan_request_created

    def test_cannot_request_item_twice(
        self,
        alice_new_item: ItemRead,
        alice_client: TestClient,
        bob_client: TestClient,
    ):
        """Check that a client cannot request the same item twice."""

        # request item
        resp = bob_client.post(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        resp.raise_for_status()
        request = resp.json()

        # check a chat message has been created for alice
        resp = alice_client.get(f"/v1/me/chats/{request['chat_id']}/messages")
        resp.raise_for_status()
        last_message = resp.json()[0]
        assert last_message["message_type"] == ChatMessageType.loan_request_created

        # request it again
        resp = bob_client.post(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        assert not resp.is_success

        # check not changes in the chat messages
        resp = alice_client.get(f"/v1/me/chats/{request['chat_id']}/messages")
        resp.raise_for_status()
        print(resp.text)
        assert resp.json()[0]["id"] == last_message["id"]

    def test_cannot_request_own_item(
        self,
        alice_new_item: ItemRead,
        alice_client: TestClient,
    ):
        """Check that a client cannot request an item owned by the latter."""

        resp = alice_client.post(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        assert not resp.is_success

    def test_can_request_after_cancelled(
        self,
        alice_new_item: ItemRead,
        bob_client: TestClient,
    ):
        """Check an item can be requested again after cancelled previous request."""

        # request item
        resp = bob_client.post(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        resp.raise_for_status()

        # cancel loan request
        bob_client.delete(f"/v1/items/{alice_new_item.id}/request").raise_for_status()

        # request item
        resp = bob_client.post(f"/v1/items/{alice_new_item.id}/request")
        print(resp.text)
        resp.raise_for_status()


class TestLoanRequestStateDiagram:
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

        # check a chat message has been created for alice
        resp = alice_client.get(f"/v1/me/chats/{request['chat_id']}/messages")
        resp.raise_for_status()
        last_message = resp.json()[0]
        assert last_message["message_type"] == ChatMessageType.loan_request_rejected

        # check a chat message has been created for bob
        resp = bob_client.get(f"/v1/me/chats/{request['chat_id']}/messages")
        resp.raise_for_status()
        last_message = resp.json()[0]
        assert last_message["message_type"] == ChatMessageType.loan_request_rejected

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

        # check a chat message has been created for alice
        resp = alice_client.get(f"/v1/me/chats/{request['chat_id']}/messages")
        resp.raise_for_status()
        last_message = resp.json()[0]
        assert last_message["message_type"] == ChatMessageType.loan_request_cancelled

        # check a chat message has been created for bob
        resp = bob_client.get(f"/v1/me/chats/{request['chat_id']}/messages")
        resp.raise_for_status()
        last_message = resp.json()[0]
        assert last_message["message_type"] == ChatMessageType.loan_request_cancelled

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

        # check a chat messages have been created for alice
        resp = alice_client.get(f"/v1/me/chats/{request['chat_id']}/messages")
        resp.raise_for_status()
        messages = resp.json()
        assert messages[2]["message_type"] == ChatMessageType.loan_request_created
        assert messages[1]["message_type"] == ChatMessageType.loan_request_accepted
        assert messages[0]["message_type"] == ChatMessageType.loan_request_rejected

        # check a chat message has been created for bob
        resp = bob_client.get(f"/v1/me/chats/{request['chat_id']}/messages")
        resp.raise_for_status()
        messages = resp.json()
        assert messages[2]["message_type"] == ChatMessageType.loan_request_created
        assert messages[1]["message_type"] == ChatMessageType.loan_request_accepted
        assert messages[0]["message_type"] == ChatMessageType.loan_request_rejected

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

        # check a chat messages have been created for alice
        resp = alice_client.get(f"/v1/me/chats/{request['chat_id']}/messages")
        resp.raise_for_status()
        messages = resp.json()
        assert messages[2]["message_type"] == ChatMessageType.loan_request_created
        assert messages[1]["message_type"] == ChatMessageType.loan_request_accepted
        assert messages[0]["message_type"] == ChatMessageType.loan_request_cancelled

        # check a chat message has been created for bob
        resp = bob_client.get(f"/v1/me/chats/{request['chat_id']}/messages")
        resp.raise_for_status()
        messages = resp.json()
        assert messages[2]["message_type"] == ChatMessageType.loan_request_created
        assert messages[1]["message_type"] == ChatMessageType.loan_request_accepted
        assert messages[0]["message_type"] == ChatMessageType.loan_request_cancelled

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

        # check a chat messages have been created for alice
        resp = alice_client.get(f"/v1/me/chats/{request['chat_id']}/messages")
        resp.raise_for_status()
        messages = resp.json()
        assert messages[2]["message_type"] == ChatMessageType.loan_request_created
        assert messages[1]["message_type"] == ChatMessageType.loan_request_accepted
        assert messages[0]["message_type"] == ChatMessageType.loan_started

        # check a chat message has been created for bob
        resp = bob_client.get(f"/v1/me/chats/{request['chat_id']}/messages")
        resp.raise_for_status()
        messages = resp.json()
        assert messages[2]["message_type"] == ChatMessageType.loan_request_created
        assert messages[1]["message_type"] == ChatMessageType.loan_request_accepted
        assert messages[0]["message_type"] == ChatMessageType.loan_started

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
