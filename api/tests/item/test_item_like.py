import pytest
from fastapi.testclient import TestClient

from app.schemas.item.read import ItemRead


@pytest.mark.usefixtures("many_items")
class TestItemLike:
    """Test item likes."""

    def test_read_pages(
        self,
        bob_client: TestClient,
        alice_items: list[ItemRead],
    ):
        item = alice_items[-1]

        # like alice items
        bob_client.post(url=f"/v1/me/liked/{item.id}").raise_for_status()

        resp = bob_client.get("/v1/me/liked")
        resp.raise_for_status()

        assert [item["id"] for item in resp.json()] == [item.id]
