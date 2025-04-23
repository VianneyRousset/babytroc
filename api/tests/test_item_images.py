from fastapi.testclient import TestClient


def test_created_image_can_be_read(
    client0: TestClient,
    users: list[int],
    image_data: str,
):
    """Upload image from client 0 and retrieve it from public client."""

    # upload image
    resp = client0.post("/v1/images", files={"file": image_data})
    resp.raise_for_status()
    name = resp.json()["name"]

    # request item
    resp = client0.get(f"/v1/images/{name}")
    resp.raise_for_status()
