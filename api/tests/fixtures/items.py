import random
from io import BytesIO
from string import ascii_letters
from typing import TypedDict, TypeVar

import pytest
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import services
from app.config import Config
from app.schemas.image.read import ItemImageRead
from app.schemas.item.base import MonthRange
from app.schemas.item.create import ItemCreate
from app.schemas.item.read import ItemRead
from app.schemas.region.read import RegionRead
from app.schemas.user.private import UserPrivateRead


class UserData(TypedDict):
    name: str
    email: str
    password: str


class ItemData(TypedDict):
    name: str
    description: str
    targeted_age_months: str
    regions: list[int]
    images: list[str]


@pytest.fixture(scope="class")
def alice_items_data(
    alice_items_image: ItemImageRead,
    regions: list[RegionRead],
) -> list[ItemData]:
    """Alice items data."""

    return [
        {
            "name": "candle",
            "description": "dwell into a flowerbed",
            "targeted_age_months": "4-10",
            "regions": [regions[0].id],
            "images": [alice_items_image.name],
        },
    ]


@pytest.fixture(scope="class")
def alice_new_item_data(
    alice_new_item_images: list[ItemImageRead],
    regions: list[RegionRead],
) -> ItemData:
    """Alice new item data."""

    return {
        "name": "new-item",
        "description": "This is the latest new item created by alice.",
        "targeted_age_months": "7-",
        "regions": [regions[1].id],
        "images": [image.name for image in alice_new_item_images],
    }


@pytest.fixture(scope="class")
def alice_special_item_data(
    alice_special_item_images: list[ItemImageRead],
    regions: list[RegionRead],
) -> ItemData:
    """Alice special item data."""

    return {
        "name": "Special item",
        "description": "This is the special item created by alice.",
        "targeted_age_months": "2-5",
        "regions": [regions[0].id],
        "images": [image.name for image in alice_special_item_images],
    }


@pytest.fixture(scope="class")
def bob_items_data(
    bob_items_image: ItemImageRead,
    regions: list[RegionRead],
) -> list[ItemData]:
    """Bob items data."""

    return [
        {
            "name": "Dark side",
            "description": "Breathe, breathe in the air. Don't be afraid to care",
            "targeted_age_months": "16-",
            "regions": [regions[0].id, regions[1].id],
            "images": [bob_items_image.name],
        },
    ]


@pytest.fixture(scope="class")
def alice_items_image_data() -> bytes:
    """Basic PBM image."""

    return "\n".join(
        [
            "P1",
            "3 3",
            "101",
            "101",
            "010",
        ]
    ).encode()


@pytest.fixture(scope="class")
def alice_new_item_image_data() -> bytes:
    """Basic PBM image."""

    return "\n".join(
        [
            "P1",
            "3 3",
            "000",
            "111",
            "000",
        ]
    ).encode()


@pytest.fixture(scope="class")
def alice_special_item_image_data() -> bytes:
    """Basic PBM image."""

    return "\n".join(
        [
            "P1",
            "3 3",
            "101",
            "111",
            "010",
        ]
    ).encode()


@pytest.fixture(scope="class")
def bob_items_image_data() -> bytes:
    """Basic PBM image."""

    return "\n".join(
        [
            "P1",
            "3 3",
            "101",
            "101",
            "010",
        ]
    ).encode()


@pytest.fixture(scope="class")
def alice_items_image(
    app_config: Config,
    database: sqlalchemy.URL,
    alice: UserPrivateRead,
    alice_items_image_data: bytes,
) -> ItemImageRead:
    """Ensure Alice's item image exists."""

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return services.image.upload_image(
            db=session,
            config=app_config,
            owner_id=alice.id,
            fp=BytesIO(alice_items_image_data),
        )


@pytest.fixture(scope="class")
def alice_new_item_images(
    app_config: Config,
    database: sqlalchemy.URL,
    alice: UserPrivateRead,
    alice_new_item_image_data: bytes,
) -> list[ItemImageRead]:
    """Ensure Alice's item image exists."""

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return [
            services.image.upload_image(
                db=session,
                config=app_config,
                owner_id=alice.id,
                fp=BytesIO(image_data),
            )
            for image_data in [alice_new_item_image_data] * 3
        ]


@pytest.fixture(scope="class")
def alice_special_item_images(
    app_config: Config,
    database: sqlalchemy.URL,
    alice: UserPrivateRead,
    alice_new_item_image_data: bytes,
) -> list[ItemImageRead]:
    """Ensure Alice's item image exists."""

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return [
            services.image.upload_image(
                db=session,
                config=app_config,
                owner_id=alice.id,
                fp=BytesIO(image_data),
            )
            for image_data in [alice_new_item_image_data] * 2
        ]


@pytest.fixture(scope="class")
def bob_items_image(
    app_config: Config,
    database: sqlalchemy.URL,
    bob: UserPrivateRead,
    bob_items_image_data: bytes,
) -> ItemImageRead:
    """Ensure Bob's item image exists."""

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return services.image.upload_image(
            db=session,
            config=app_config,
            owner_id=bob.id,
            fp=BytesIO(bob_items_image_data),
        )


@pytest.fixture(scope="class")
def alice_items(
    database: sqlalchemy.URL,
    alice: UserPrivateRead,
    alice_items_data: list[ItemData],
) -> list[ItemRead]:
    """Ensures Alice's items exist."""

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return [
            services.item.create_item(
                db=session,
                owner_id=alice.id,
                item_create=ItemCreate(
                    name=item["name"],
                    description=item["description"],
                    images=item["images"],
                    targeted_age_months=MonthRange(item["targeted_age_months"]),
                    regions=item["regions"],
                ),
            )
            for item in alice_items_data
        ]


# scope function
@pytest.fixture
def alice_new_item(
    database: sqlalchemy.URL,
    alice: UserPrivateRead,
    alice_new_item_data: ItemData,
) -> ItemRead:
    """Alice's new item."""

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return services.item.create_item(
            db=session,
            owner_id=alice.id,
            item_create=ItemCreate(
                name=alice_new_item_data["name"],
                description=alice_new_item_data["description"],
                images=alice_new_item_data["images"],
                targeted_age_months=MonthRange(
                    alice_new_item_data["targeted_age_months"]
                ),
                regions=alice_new_item_data["regions"],
            ),
        )


# scope function
@pytest.fixture(scope="class")
def alice_special_item(
    database: sqlalchemy.URL,
    alice: UserPrivateRead,
    alice_special_item_data: ItemData,
) -> ItemRead:
    """Alice's special item."""

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return services.item.create_item(
            db=session,
            owner_id=alice.id,
            item_create=ItemCreate(
                name=alice_special_item_data["name"],
                description=alice_special_item_data["description"],
                images=alice_special_item_data["images"],
                targeted_age_months=MonthRange(
                    alice_special_item_data["targeted_age_months"]
                ),
                regions=alice_special_item_data["regions"],
            ),
        )


@pytest.fixture(scope="class")
def bob_items(
    database: sqlalchemy.URL,
    bob: UserPrivateRead,
    bob_items_data: list[ItemData],
) -> list[ItemRead]:
    """Ensures bob's items exist."""

    engine = create_engine(database)
    with Session(engine) as session, session.begin():
        return [
            services.item.create_item(
                db=session,
                owner_id=bob.id,
                item_create=ItemCreate(
                    name=item["name"],
                    description=item["description"],
                    images=item["images"],
                    targeted_age_months=MonthRange(item["targeted_age_months"]),
                    regions=item["regions"],
                ),
            )
            for item in bob_items_data
        ]


@pytest.fixture(scope="class")
def items(
    alice_items: list[ItemRead],
    bob_items: list[ItemRead],
) -> list[ItemRead]:
    """All items."""

    return [
        *alice_items,
        *bob_items,
    ]


def random_str(length: int) -> str:
    return "".join(random.choices(ascii_letters, k=length))


def random_targeted_age_months() -> MonthRange:
    lower = random.randint(0, 32)
    upper = random.randint(lower, 33)
    return MonthRange.from_values(
        lower=None if lower == 0 else lower,
        upper=None if upper > 32 else upper,
    )


T = TypeVar("T")


def random_sample(population: list[T]) -> list[T]:
    return random.sample(population, k=random.randint(1, len(population)))


@pytest.fixture(scope="class")
def many_items(
    database: sqlalchemy.URL,
    alice: UserPrivateRead,
    bob: UserPrivateRead,
    alice_items_image: ItemImageRead,
    bob_items_image: ItemImageRead,
    regions: list[RegionRead],
) -> list[ItemRead]:
    """Many items."""

    n = 256
    random.seed(0xBDF81829)

    engine = create_engine(database)

    owner_ids, images = [
        list(column)
        for column in zip(
            *random.choices(
                [
                    (alice.id, alice_items_image),
                    (bob.id, bob_items_image),
                ],
                k=n,
            ),
            strict=True,
        )
    ]

    with Session(engine) as session, session.begin():
        items = services.item.create_many_items(
            db=session,
            owner_ids=owner_ids,
            item_creates=[
                ItemCreate(
                    name=random_str(8),
                    description=random_str(50),
                    targeted_age_months=random_targeted_age_months(),
                    regions=random_sample([reg.id for reg in regions]),
                    images=[image.name],
                    blocked=random.choice([False] * 3 + [True]),
                )
                for image in images
            ],
        )

        return items


@pytest.fixture(scope="class")
def some_item_french_names() -> list[str]:
    """Some item French names."""

    random.seed(0xA19F)

    return [
        "Le sénat du bien-être",
        "Le senat bleus",
        "Les sénats bleus",
        "L'importance du Bien être",
        "La Lettre bleu",
        "Les lettres bleus",
        "Les mots bleus",
        "Le sénat bleu",
        "Les leçons données",
        "La lecon de mon ami",
        "La caravane bleue",
        "L'écriture bleue",
        "La cerise bleue",
        *(f"{random_str(5)} bleu {random_str(5)}" for _ in range(40)),
    ]


@pytest.fixture(scope="class")
def some_items_with_french_names(
    database: sqlalchemy.URL,
    alice: UserPrivateRead,
    bob: UserPrivateRead,
    alice_items_image: ItemImageRead,
    bob_items_image: ItemImageRead,
    regions: list[RegionRead],
    some_item_french_names: list[str],
) -> list[ItemRead]:
    """Many items."""

    random.seed(0x15976)

    engine = create_engine(database)

    owner_ids, images = [
        list(column)
        for column in zip(
            *random.choices(
                [
                    (alice.id, alice_items_image),
                    (bob.id, bob_items_image),
                ],
                k=len(some_item_french_names),
            ),
            strict=True,
        )
    ]

    with Session(engine) as session, session.begin():
        items = services.item.create_many_items(
            db=session,
            owner_ids=owner_ids,
            item_creates=[
                ItemCreate(
                    name=name,
                    description=random_str(50),
                    targeted_age_months=random_targeted_age_months(),
                    regions=random_sample([reg.id for reg in regions]),
                    images=[image.name],
                    blocked=random.choice([False] * 3 + [True]),
                )
                for name, image in zip(some_item_french_names, images, strict=True)
            ],
        )

        return items
