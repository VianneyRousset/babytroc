"""add region tables

Revision ID: 4e448b380021
Revises: 2308ae67cf21
Create Date: 2025-04-21 14:59:18.444329
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4e448b380021"
down_revision: str | None = "2308ae67cf21"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    create_region_table()


def downgrade() -> None:
    drop_region_table()


def create_region_table():
    op.create_table(
        "region",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(),
            autoincrement=True,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_region_id"), "region", ["id"], unique=False)


def drop_region_table():
    op.drop_index(op.f("ix_region_id"), table_name="region")
    op.drop_table("region")
