"""add loan tables

Revision ID: 5fd696534ab9
Revises: 9984a44906d2
Create Date: 2025-04-21 14:59:37.270555
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5fd696534ab9"
down_revision: str | None = "9984a44906d2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    create_loan_table()
    create_loan_request_table()


def downgrade() -> None:
    drop_loan_request_table()
    drop_loan_table()


def create_loan_table():
    op.create_table(
        "loan",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("borrower_id", sa.Integer(), nullable=True),
        sa.Column(
            "during",
            postgresql.TSTZRANGE(),
            server_default=sa.text("tstzrange(now(), NULL, '()')"),
            nullable=False,
        ),
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=True),
            autoincrement=True,
            nullable=False,
        ),
        postgresql.ExcludeConstraint(
            (sa.column("item_id"), "="),
            (sa.column("during"), "&&"),
            using="gist",
            name="loan_no_overlapping_date_ranges",
        ),
        sa.ForeignKeyConstraint(
            ["borrower_id"],
            ["user.id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["item.id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_loan_during"), "loan", ["during"], unique=False)
    op.create_index(op.f("ix_loan_id"), "loan", ["id"], unique=False)
    op.create_index(op.f("ix_loan_item_id"), "loan", ["item_id"], unique=False)


def drop_loan_table():
    op.drop_index(op.f("ix_loan_item_id"), table_name="loan")
    op.drop_index(op.f("ix_loan_id"), table_name="loan")
    op.drop_index(op.f("ix_loan_during"), table_name="loan")
    op.drop_table("loan")
    op.execute(text("DROP TYPE loanrequeststate"))


def create_loan_request_table():
    op.create_table(
        "loan_request",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("borrower_id", sa.Integer(), nullable=False),
        sa.Column(
            "state",
            sa.Enum(
                "pending",
                "cancelled",
                "accepted",
                "rejected",
                "executed",
                name="loanrequeststate",
            ),
            nullable=False,
        ),
        sa.Column(
            "loan_id",
            sa.Integer(),
            nullable=True,
            comment="The created loan originating from this loan request.",
        ),
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=True),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "creation_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        postgresql.ExcludeConstraint(
            (sa.column("item_id"), "="),
            (sa.column("borrower_id"), "="),
            where=sa.text("state = 'pending'"),
            using="gist",
            name="loan_request_unique_pending_request",
        ),
        sa.CheckConstraint(
            "state = 'executed' AND loan_id IS NOT NULL "
            "OR state != 'executed' AND loan_id IS NULL",
            name="loan_request_executed_or_not",
        ),
        sa.ForeignKeyConstraint(
            ["borrower_id"],
            ["user.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["item.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["loan_id"],
            ["loan.id"],
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_loan_request_id"), "loan_request", ["id"], unique=False)


def drop_loan_request_table():
    op.drop_index(op.f("ix_loan_request_id"), table_name="loan_request")
    op.drop_table("loan_request")
