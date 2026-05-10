"""Template registry — single source of truth for the chain.

Append entries here as later phases add templates. The chain is built by
`build_chain(specs=TEMPLATES)`.
"""

from tests.fixtures.database.infrastructure.chain import TemplateSpec
from tests.fixtures.database.seeds.category import (
    seed_alice_items_with_categories,
    seed_reference_categories,
)
from tests.fixtures.database.seeds.chat import seed_alice_many_chats
from tests.fixtures.database.seeds.image import seed_baseline_images
from tests.fixtures.database.seeds.item import (
    seed_alice_many_items,
    seed_baseline_items,
    seed_french_named_items,
    seed_many_items,
)
from tests.fixtures.database.seeds.loan import (
    seed_alice_many_loans,
    seed_alice_special_item_loan_requests,
    seed_many_loan_requests_for_alice_items,
)
from tests.fixtures.database.seeds.region import seed_reference_regions
from tests.fixtures.database.seeds.user import seed_baseline_users, seed_many_users

TEMPLATES: dict[str, TemplateSpec] = {
    "bare": TemplateSpec(
        name="bare",
        parent=None,
        apply_alembic=True,
    ),
    "reference": TemplateSpec(
        name="reference",
        parent="bare",
        seeds=(seed_reference_regions, seed_reference_categories),
    ),
    "baseline": TemplateSpec(
        name="baseline",
        parent="reference",
        seeds=(seed_baseline_users, seed_baseline_images),
    ),
    "baseline_items": TemplateSpec(
        name="baseline_items",
        parent="baseline",
        seeds=(seed_baseline_items,),
    ),
    "many_items": TemplateSpec(
        name="many_items",
        parent="baseline_items",
        seeds=(seed_many_items,),
    ),
    "alice_many_items": TemplateSpec(
        name="alice_many_items",
        parent="baseline_items",
        seeds=(seed_alice_many_items,),
    ),
    "alice_items_with_categories": TemplateSpec(
        name="alice_items_with_categories",
        parent="alice_many_items",
        seeds=(seed_alice_items_with_categories,),
    ),
    "french_named_items": TemplateSpec(
        name="french_named_items",
        parent="baseline_items",
        seeds=(seed_french_named_items,),
    ),
    "many_users": TemplateSpec(
        name="many_users",
        parent="baseline_items",
        seeds=(seed_many_users,),
    ),
    "alice_special_item_loan_requests": TemplateSpec(
        name="alice_special_item_loan_requests",
        parent="many_users",
        seeds=(seed_alice_special_item_loan_requests,),
    ),
    "many_loan_requests": TemplateSpec(
        name="many_loan_requests",
        parent="many_items",
        seeds=(seed_many_loan_requests_for_alice_items,),
    ),
    "alice_many_loans": TemplateSpec(
        name="alice_many_loans",
        parent="alice_many_items",
        seeds=(seed_alice_many_loans,),
    ),
    "alice_many_chats": TemplateSpec(
        name="alice_many_chats",
        parent="many_items",
        seeds=(seed_alice_many_chats,),
    ),
}

DEFAULT_TEMPLATE = "baseline_items"
