from sqlalchemy.ext.asyncio import AsyncSession

from app import models


async def apply_seed(db: AsyncSession):
    # create users
    alice = models.user.User(
        email="alice@test.org",
        name="Alice",
        password="xxx",
    )
    bob = models.user.User(
        email="bob@test.org",
        name="Bob",
        password="xxx",
    )
    db.add(alice)
    db.add(bob)

    # create items
    db.add(
        models.item.Item(
            name="Mystic Glow Candle",
            description="A handcrafted candle with a unique blend of lavender and"
            " vanilla, perfect for relaxation. The soft, flickering light adds a"
            "soothing ambiance to any space.",
            owner=alice,
        )
    )
    db.add(
        models.item.Item(
            name="Bamboo Zen Mug",
            description="An eco-friendly mug made from sustainable bamboo fibers."
            " Lightweight yet durable, it's ideal for your morning coffee or tea"
            " ritual.",
            owner=bob,
        )
    )
    db.add(
        models.item.Item(
            name="Pocket Herb Garden",
            description="A compact kit containing seeds for growing basil, mint, and"
            " thyme. Perfect for kitchen counters or small spaces, bringing fresh"
            " herbs to your meals.",
            owner=alice,
        )
    )
    db.add(
        models.item.Item(
            name="Aurora Night Light",
            description="A mesmerizing night light that projects colorful auroras on"
            " your walls and ceiling. Perfect for calming nighttime routines or"
            " creating a magical atmosphere.",
            owner=bob,
        )
    )
    db.add(
        models.item.Item(
            name="Gourmet Snack Box",
            description="A curated selection of artisanal treats, from chocolate"
            " truffles to spicy nuts. Perfect for sharing or indulging in a solo"
            " snacking adventure.",
            owner=alice,
        )
    )
    db.add(
        models.item.Item(
            name="Celestial Journal",
            description="A beautifully designed notebook with starry constellations on"
            " the cover. Filled with high-quality, thick paper for writing, sketching,"
            " or planning your dreams.",
            owner=bob,
        )
    )
    db.add(
        models.item.Item(
            name="Traveler's Mini Blanket",
            description="A soft, lightweight blanket that folds into a portable pouch."
            " Ideal for picnics, camping, or keeping cozy during travel.",
            owner=alice,
        )
    )
    db.add(
        models.item.Item(
            name="Artisan Soap Trio",
            description="A set of three handmade soaps, each with a distinct scent:"
            " citrus burst, calming lavender, and invigorating peppermint."
            " Made with natural ingredients for a gentle cleanse.",
            owner=bob,
        )
    )
    db.add(
        models.item.Item(
            name="Pocket Puzzle Cube",
            description="A compact, tactile puzzle game that challenges your problem-"
            "solving skills. Small enough to carry everywhere, it's great for quick"
            " mental breaks.",
            owner=alice,
        )
    )
    db.add(
        models.item.Item(
            name="Ocean Mist Spray",
            description="A refreshing facial mist infused with minerals and sea"
            " botanicals. Perfect for revitalizing your skin and spirit throughout the"
            " day.",
            owner=bob,
        )
    )

    await db.commit()
