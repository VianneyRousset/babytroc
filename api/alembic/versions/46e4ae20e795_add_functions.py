"""Add functions

Revision ID: 46e4ae20e795
Revises: 22a533ebcf12
Create Date: 2025-01-03 14:08:55.701246
"""

from collections.abc import Sequence

from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "46e4ae20e795"
down_revision: str | None = "22a533ebcf12"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        text(
            "CREATE OR REPLACE FUNCTION normalize_text(text) RETURNS text AS $$ "
            "SELECT lower(unaccent($1)); "
            "$$ "
            "LANGUAGE SQL IMMUTABLE;"
        )
    )


def downgrade() -> None:
    op.execute(text("DROP FUNCTION normalize_text"))
