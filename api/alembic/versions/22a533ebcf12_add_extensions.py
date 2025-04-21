"""Add extensions

Revision ID: 22a533ebcf12
Revises:
Create Date: 2025-01-03 13:43:15.133442
"""

from collections.abc import Sequence

from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "22a533ebcf12"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(text("CREATE EXTENSION btree_gist;"))
    op.execute(text("CREATE EXTENSION btree_gin;"))
    op.execute(text("CREATE EXTENSION unaccent;"))
    op.execute(text("CREATE EXTENSION pg_trgm;"))


def downgrade() -> None:
    op.execute(text("DROP EXTENSION btree_gist;"))
    op.execute(text("DROP EXTENSION btree_gin;"))
    op.execute(text("DROP EXTENSION unaccent;"))
    op.execute(text("DROP EXTENSION pg_trgm;"))
