from fastapi.testclient import TestClient


def test_created_image_can_be_read(
    alice_client: TestClient,
    alice_items_image_data: str,
):
    """Upload image from client 0 and retrieve it from public client."""

    # upload image
    resp = alice_client.post(
        "/v1/images",
        files={"file": alice_items_image_data},
    )
    resp.raise_for_status()
    name = resp.json()["name"]

    # request item
    resp = alice_client.get(f"/v1/images/{name}")
    resp.raise_for_status()
