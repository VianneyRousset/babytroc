from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Mapping

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item as ItemDB

from .utils import EndpointChangesRecorder

ITEM_NAME_MIN_LENGTH = 5
ITEM_NAME_MAX_LENGTH = 30
ITEM_DESCRIPTION_MIN_LENGTH = 50
ITEM_DESCRIPTION_MAX_LENGTH = 600

VALID_ITEM_NAME = "Voluptatem"
INVALID_ITEM_NAME_TOO_SHORT = "Sunt"
INVALID_ITEM_NAME_TOO_LONG = "Ut enim ad minima veniam enimas"
VALID_ITEM_DESCRIPTION = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse tristique "
    "urna sem, ut convallis dui lobortis eget. Suspendisse ac sem sed elit mattis "
    "ultrices eu id dui. Curabitur ante urna, tincidunt aliquet diam id, egestas "
    "laoreet est. Donec faucibus finibus bibendum."
)
INVALID_ITEM_DESCRIPTION_TOO_SHORT = "Lorem ipsum dolor sit amet, consectetur adipisci."
INVALID_ITEM_DESCRIPTION_TOO_LONG = (
    "Nullam nec mollis nisl. Vestibulum a libero dui. Cras malesuada massa sed libero "
    "venenatis fermentum. Curabitur in semper magna. Sed luctus ligula libero, vitae "
    "facilisis nulla accumsan a. Duis egestas, augue et porttitor maximus, metus leo "
    "tincidunt urna, euismod venenatis magna libero et odio. Aenean velit turpis, "
    "porta at eleifend id, posuere vitae velit. Vestibulum non risus luctus mi "
    "ultricies sagittis. Suspendisse potenti. Proin at urna nec velit pharetra luctus. "
    "Vestibulum sit amet maximus massa. Ut sit amet feugiat lorem. Pellentesque at dui "
    "sed ligula equ lobortis imperdiet ut ac urna."
)

# check constants
assert ITEM_NAME_MIN_LENGTH < len(VALID_ITEM_NAME) < ITEM_NAME_MAX_LENGTH
assert len(INVALID_ITEM_NAME_TOO_SHORT) < ITEM_NAME_MIN_LENGTH
assert len(INVALID_ITEM_NAME_TOO_LONG) > ITEM_NAME_MAX_LENGTH

assert (
    ITEM_DESCRIPTION_MIN_LENGTH
    < len(VALID_ITEM_DESCRIPTION)
    < ITEM_DESCRIPTION_MAX_LENGTH
)

assert len(INVALID_ITEM_DESCRIPTION_TOO_SHORT) < ITEM_DESCRIPTION_MIN_LENGTH
assert len(INVALID_ITEM_DESCRIPTION_TOO_LONG) > ITEM_DESCRIPTION_MAX_LENGTH


async def get_db_items(db: AsyncSession) -> list:
    return [
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "creation_date": item.creation_date.isoformat(),
        }
        for item in await db.scalars(select(ItemDB))
    ]


class TestCreateItem:
    """Test item creation using POST /items endpoint."""

    @pytest.mark.usefixtures("_seed_db")
    @pytest.mark.asyncio
    async def test_create_item(self, client: AsyncClient, db: AsyncSession):
        """
        Successfully create an item.
        - check POST response status code is HTTPStatus.CREATED.
        - check returned item creation datetime is close to now().
        - check returned item name and desciption match given info.
        - check the new items list only change is a new item which is the same as the
          returned item.
        """

        new_item = {
            "name": VALID_ITEM_NAME,
            "description": VALID_ITEM_DESCRIPTION,
        }

        recorder = EndpointChangesRecorder(
            client=client,
            endpoint="/v1/items",
            dict_key="id",
        )

        async with recorder:
            resp = await client.post(
                url="/v1/items",
                json=new_item,
            )

            assert (
                resp.status_code == HTTPStatus.CREATED
            ), "POST request did not succeed"

            api_new_item = resp.json()

        # check creation date is of the approximatively correct
        delta = abs(
            datetime.fromisoformat(api_new_item["creation_date"]) - datetime.now()
        )
        assert delta < timedelta(seconds=5)

        # check the new item is present in the items list
        assert recorder.diff() == {
            "dictionary_item_added": {f"root[{api_new_item['id']}]": api_new_item}
        }, "Wrong modification of the items list"

        # check given fields match
        del api_new_item["id"]
        del api_new_item["creation_date"]
        assert api_new_item == new_item

    @pytest.mark.usefixtures("_seed_db")
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "creation",
        [
            pytest.param(
                {
                    "description": VALID_ITEM_DESCRIPTION,
                },
                id="missing_name",
            ),
            pytest.param(
                {
                    "name": VALID_ITEM_NAME,
                },
                id="missing_description",
            ),
            pytest.param(
                {
                    "name": INVALID_ITEM_NAME_TOO_SHORT,
                    "description": VALID_ITEM_DESCRIPTION,
                },
                id="name_too_short",
            ),
            pytest.param(
                {
                    "name": INVALID_ITEM_NAME_TOO_LONG,
                    "description": VALID_ITEM_DESCRIPTION,
                },
                id="name_too_long",
            ),
            pytest.param(
                {
                    "name": VALID_ITEM_NAME,
                    "description": INVALID_ITEM_DESCRIPTION_TOO_SHORT,
                },
                id="description_too_short",
            ),
            pytest.param(
                {
                    "name": VALID_ITEM_NAME,
                    "description": INVALID_ITEM_DESCRIPTION_TOO_LONG,
                },
                id="description_too_long",
            ),
        ],
    )
    async def test_create_item_invalid_body(
        self,
        client: AsyncClient,
        db: AsyncSession,
        creation: Mapping[str, str],
    ):
        """
        Fail to create an item because of invalid body.
        - check POST response status code is HTTPStatus.BAD_REQUEST.
        - check that no modification has been done to the items list.
        """

        recorder = EndpointChangesRecorder(
            client=client,
            endpoint="/v1/items",
            dict_key="id",
        )

        async with recorder:
            # try to create item without name
            resp = await client.post(
                url="/v1/items",
                json={
                    "description": "x" * 100,
                },
            )

            assert (
                resp.status_code == HTTPStatus.BAD_REQUEST
            ), f"POST must fails with status code {HTTPStatus.BAD_REQUEST}"

        # verify nothing changed
        assert recorder.diff() == {}


class TestReadItems:
    """Test items reading using GET /items and /items/{item_id} endpoints."""

    @pytest.mark.usefixtures("_seed_db")
    @pytest.mark.asyncio
    async def test_list_items(self, client: AsyncClient, db: AsyncSession):
        resp = await client.get("/v1/items")

        assert resp.status_code == HTTPStatus.OK, "GET request did not succeed"

        api_items = resp.json()
        db_items = await get_db_items(db)

        assert len(api_items) == len(
            db_items
        ), "Number of items in API response doesn't match database"

        assert type(api_items) is list, "API response is not a list"

        db_items = {item["id"]: item for item in db_items}
        api_items = {item["id"]: item for item in api_items}

        # compare items
        assert (
            db_items == api_items
        ), "Mismatch in items between database and API response"

    @pytest.mark.usefixtures("_seed_db")
    @pytest.mark.asyncio
    async def test_read_single_item(self, client: AsyncClient, db: AsyncSession):
        db_items = {item["id"]: item for item in await get_db_items(db)}

        for item_id, db_item in db_items.items():
            # get first item
            resp = await client.get(f"/v1/items/{item_id}")

            print(resp.json())

            assert (
                resp.status_code == HTTPStatus.OK
            ), f"GET request did not succeed for item_id {item_id}"

            api_item = resp.json()

            assert api_item == db_item

    @pytest.mark.usefixtures("_seed_db")
    @pytest.mark.asyncio
    async def test_read_non_existing_item(self, client: AsyncClient, db: AsyncSession):
        max_item_id = max(item["id"] for item in await get_db_items(db))

        # non existing item id
        resp = await client.get(f"/v1/items/{max_item_id + 1}")

        print(resp.json())

        assert (
            resp.status_code == HTTPStatus.NOT_FOUND
        ), "Non existing item ID should return ..."

    @pytest.mark.usefixtures("_seed_db")
    @pytest.mark.asyncio
    async def test_read_invalid_item_id(self, client: AsyncClient, db: AsyncSession):
        # negative item id
        resp = await client.get("/v1/items/-1")
        assert (
            resp.status_code == HTTPStatus.BAD_REQUEST
        ), "Negative item ID should return Unprocessable Entity Error"

        # string item id
        resp = await client.get("/v1/items/abc")
        assert (
            resp.status_code == HTTPStatus.BAD_REQUEST
        ), "String item ID should return Unprocessable Entity Error"


class TestUpdateItem:
    @pytest.mark.usefixtures("_seed_db")
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "update",
        [
            pytest.param(
                {"name": "n" * 10},
                id="name_only",
            ),
            pytest.param(
                {"description": "d" * 100},
                id="description_only",
            ),
            pytest.param(
                {"name": "n" * 10, "description": "d" * 100},
                id="name_and_description",
            ),
        ],
    )
    async def test_update(
        self,
        update: Mapping[str, str],
        client: AsyncClient,
        db: AsyncSession,
    ):
        item_id = 4

        recorder = EndpointChangesRecorder(
            client=client,
            endpoint="/v1/items",
            dict_key="id",
        )

        async with recorder:
            resp = await client.patch(
                url=f"/v1/items/{item_id}",
                json=update,
            )

            assert resp.status_code == HTTPStatus.OK, "Patch request did not succeed"

            api_new_item = resp.json()

        # check the modifications has been done in GET /items list
        assert {
            report_type: {key: value["new_value"] for key, value in diff_levels.items()}
            for report_type, diff_levels in recorder.diff().items()
        } == {
            "values_changed": {
                f"root[{item_id}]['{key}']": value for key, value in update.items()
            },
        }

        # check returned item is matching
        assert api_new_item == recorder.stop_value[item_id]
