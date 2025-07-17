"""add chat tables

Revision ID: 49ba9ac4237e
Revises: 5fd696534ab9
Create Date: 2025-04-21 14:59:44.047290
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "49ba9ac4237e"
down_revision: str | None = "5fd696534ab9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    create_chat_table()
    create_chat_message_table()


def downgrade() -> None:
    drop_chat_message_table()
    drop_chat_table()


def create_chat_table():
    op.create_table(
        "chat",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("borrower_id", sa.Integer(), nullable=False),
        sa.Column("last_message_id", sa.Integer(), nullable=False),
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
        sa.PrimaryKeyConstraint("item_id", "borrower_id"),
    )


def drop_chat_table():
    op.drop_table("chat")


def create_chat_message_table():
    op.create_table(
        "chat_message",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("borrower_id", sa.Integer(), nullable=False),
        sa.Column(
            "message_type",
            sa.Enum(
                "text",
                "loan_request_created",
                "loan_request_cancelled",
                "loan_request_accepted",
                "loan_request_rejected",
                "loan_started",
                "loan_ended",
                "item_not_available",
                name="chatmessagetype",
            ),
            nullable=False,
        ),
        sa.Column("sender_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("loan_request_id", sa.Integer(), nullable=True),
        sa.Column("loan_id", sa.Integer(), nullable=True),
        sa.Column("seen", sa.Boolean(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["item_id", "borrower_id"],
            ["chat.item_id", "chat.borrower_id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["sender_id"],
            ["user.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["loan_request_id"],
            ["loan_request.id"],
            ondelete="SET NULL",
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
    op.create_index(op.f("ix_chat_message_id"), "chat_message", ["id"], unique=False)


def drop_chat_message_table():
    op.drop_index(op.f("ix_chat_message_id"), table_name="chat_message")
    op.drop_table("chat_message")
    op.execute(text("DROP TYPE chatmessagetype"))
