from fastapi.testclient import TestClient


def test_can_read_regions_list(
    client: TestClient,
    regions: list[int],
    regions_data: list[dict],
):
    """Check that regions list can be retrieved."""

    # list regions
    resp = client.get("/v1/utils/regions")
    print(resp.text)
    resp.raise_for_status()
    regions_list = resp.json()

    # check data
    for i, region_data in enumerate(regions_data):
        assert regions_list[i]["id"] == region_data["id"]
        assert regions_list[i]["name"] == region_data["name"]
