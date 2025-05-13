"""add report tables

Revision ID: 16e479c62349
Revises: 49ba9ac4237e
Create Date: 2025-04-21 15:23:58.025539
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "16e479c62349"
down_revision: str | None = "49ba9ac4237e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    create_report_table()


def downgrade() -> None:
    drop_report_table()


def create_report_table():
    op.create_table(
        "report",
        sa.Column("description", sa.String(), nullable=False),
        sa.Column(
            "report_type",
            sa.Enum("user", "item", "chat", name="reporttype"),
            nullable=False,
        ),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column(
            "creation_date",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("saved_info", sa.String(), nullable=False),
        sa.Column("context", sa.String(), nullable=False),
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=True),
            autoincrement=True,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_report_id"), "report", ["id"], unique=False)


def drop_report_table():
    op.drop_index(op.f("ix_report_id"), table_name="report")
    op.drop_table("report")

    op.execute(text("DROP TYPE reporttype"))
