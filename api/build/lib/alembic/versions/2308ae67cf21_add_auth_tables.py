"""add auth tables

Revision ID: 2308ae67cf21
Revises: 1e7d0576a6ff
Create Date: 2025-04-21 14:59:13.591193
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2308ae67cf21"
down_revision: str | None = "1e7d0576a6ff"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    create_auth_table()


def downgrade() -> None:
    drop_auth_table()


def create_auth_table():
    op.create_table(
        "auth_refresh_token",
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("invalidated", sa.Boolean(), nullable=False),
        sa.Column(
            "creation_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("token"),
    )
    op.create_index(
        op.f("ix_auth_refresh_token_token"),
        "auth_refresh_token",
        ["token"],
        unique=True,
    )


def drop_auth_table():
    op.drop_index(op.f("ix_auth_refresh_token_token"), table_name="auth_refresh_token")
    op.drop_table("auth_refresh_token")
