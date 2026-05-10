"""Template registry — single source of truth for the chain.

Append entries here as later phases add templates. The chain is built by
`build_chain(specs=TEMPLATES)`.
"""

from tests.fixtures.database.infrastructure.chain import TemplateSpec
from tests.fixtures.database.seeds.category import seed_reference_categories
from tests.fixtures.database.seeds.image import seed_baseline_images
from tests.fixtures.database.seeds.region import seed_reference_regions
from tests.fixtures.database.seeds.user import seed_baseline_users

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
}

DEFAULT_TEMPLATE = "baseline"
