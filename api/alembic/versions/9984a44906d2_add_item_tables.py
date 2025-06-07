"""add item tables

Revision ID: 9984a44906d2
Revises: 4e448b380021
Create Date: 2025-04-21 14:59:29.499998
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9984a44906d2"
down_revision: str | None = "4e448b380021"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    create_item_table()
    create_item_image_table()
    create_item_image_association_table()
    create_item_like_table()
    create_item_save_table()
    create_item_region_table()


def downgrade() -> None:
    drop_item_region_table()
    drop_item_save_table()
    drop_item_like_table()
    drop_item_image_association_table()
    drop_item_image_table()
    drop_item_table()


def create_item_table():
    op.create_table(
        "item",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=True),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column(
            "targeted_age_months",
            postgresql.INT4RANGE(),
            server_default=sa.text("'[0,]'::int4range"),
            nullable=False,
        ),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("blocked", sa.Boolean(), nullable=False),
        sa.Column(
            "searchable_text",
            sa.String(),
            sa.Computed(
                "normalize_text(name || ' ' || description)",
            ),
            nullable=False,
        ),
        sa.Column(
            "creation_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "update_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_item_searchable_text",
        "item",
        ["searchable_text"],
        unique=False,
        postgresql_using="gist",
        postgresql_ops={"searchable_text": "gist_trgm_ops"},
    )
    op.create_index(op.f("ix_item_id"), "item", ["id"], unique=False)


def drop_item_table():
    op.drop_index(op.f("ix_item_id"), table_name="item")
    op.drop_index(
        "idx_item_searchable_text",
        table_name="item",
        postgresql_using="gist",
        postgresql_ops={"searchable_text": "gist_trgm_ops"},
    )
    op.drop_table("item")


def create_item_image_table():
    op.create_table(
        "item_image",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column(
            "creation_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("name"),
    )
    op.create_index(op.f("ix_item_image_name"), "item_image", ["name"], unique=True)


def drop_item_image_table():
    op.drop_index(op.f("ix_item_image_name"), table_name="item_image")
    op.drop_table("item_image")


def create_item_image_association_table():
    op.create_table(
        "item_image_association",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("image_name", sa.String(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["image_name"], ["item_image.name"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["item_id"], ["item.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("item_id", "image_name"),
    )


def drop_item_image_association_table():
    op.drop_table("item_image_association")


def create_item_like_table():
    op.create_table(
        "item_like",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=True),
            autoincrement=True,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["item.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("item_id", "user_id", "id"),
        sa.UniqueConstraint("item_id", "user_id"),
    )
    op.create_index(op.f("ix_item_like_id"), "item_like", ["id"], unique=False)


def drop_item_like_table():
    op.drop_index(op.f("ix_item_like_id"), table_name="item_like")
    op.drop_table("item_like")


def create_item_save_table():
    op.create_table(
        "item_save",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=True),
            autoincrement=True,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["item.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("item_id", "user_id", "id"),
        sa.UniqueConstraint("item_id", "user_id"),
    )
    op.create_index(op.f("ix_item_save_id"), "item_save", ["id"], unique=False)


def drop_item_save_table():
    op.drop_index(op.f("ix_item_save_id"), table_name="item_save")
    op.drop_table("item_save")


def create_item_region_table():
    op.create_table(
        "item_region",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("region_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["item.id"],
        ),
        sa.ForeignKeyConstraint(
            ["region_id"],
            ["region.id"],
        ),
        sa.PrimaryKeyConstraint("item_id", "region_id"),
    )


def drop_item_region_table():
    op.drop_table("item_region")
