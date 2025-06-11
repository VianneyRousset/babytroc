"""add user table

Revision ID: 1e7d0576a6ff
Revises: 46e4ae20e795
Create Date: 2025-04-21 14:59:06.664486
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1e7d0576a6ff"
down_revision: str | None = "46e4ae20e795"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    create_user_table()


def downgrade() -> None:
    drop_user_table()


def create_user_table():
    op.create_table(
        "user",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=True),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("validated", sa.Boolean(), nullable=False),
        sa.Column("validation_code", sa.UUID(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column(
            "avatar_seed",
            sa.String(),
            server_default=sa.text("md5(random()::text)"),
            nullable=False,
        ),
        sa.Column("stars_count", sa.Integer(), nullable=False),
        sa.Column(
            "creation_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("stars_count >= 0", name="positive_stars_count"),
        sa.PrimaryKeyConstraint("id"),
    )

    # index of the email
    op.create_index(
        op.f("ix_user_email"),
        "user",
        ["email"],
        unique=True,
    )

    # index of the name
    op.create_index(
        op.f("ix_user_name"),
        "user",
        ["name"],
        unique=True,
    )

    # index of the id
    op.create_index(
        op.f("ix_user_id"),
        "user",
        ["id"],
        unique=False,
    )

    # index of the validation_code
    op.create_index(
        op.f("ix_user_validation_code"),
        "user",
        ["validation_code"],
        unique=True,
    )


def drop_user_table():
    op.drop_index(op.f("ix_user_validation_code"), table_name="user")
    op.drop_index(op.f("ix_user_id"), table_name="user")
    op.drop_index(op.f("ix_user_name"), table_name="user")
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_table("user")
