from fastapi.testclient import TestClient


def test_created_image_can_be_read(
    client: TestClient,
    users: list[int],
    image_data: str,
):
    # upload image
    resp = client.post("/v1/images", files={"file": image_data})
    resp.raise_for_status()
    name = resp.json()["name"]

    # request item
    resp = client.get(f"/v1/images/{name}")
    resp.raise_for_status()
