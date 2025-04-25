from fastapi.testclient import TestClient

from app.schemas.region.read import RegionRead
from tests.fixtures.regions import RegionData


def test_can_read_regions_list(
    client: TestClient,
    regions: list[RegionRead],
    regions_data: list[RegionData],
):
    """Check that regions list can be retrieved."""

    # list regions
    resp = client.get("/v1/utils/regions")
    print(resp.text)
    resp.raise_for_status()

    expected_regions = {reg["id"]: reg for reg in regions_data}
    received_regions = {reg["id"]: reg for reg in resp.json()}

    # check data
    assert set(expected_regions) == set(received_regions)
    for i in expected_regions:
        assert received_regions[i]["id"] == expected_regions[i]["id"]
        assert received_regions[i]["name"] == expected_regions[i]["name"]
