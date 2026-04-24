"""Add database triggers

Moves trigger definitions from app startup into migrations so they are
version-tracked and applied exactly once via ``alembic upgrade``.

Revision ID: a1b2c3d4e5f6
Revises: 16e479c62349
Create Date: 2026-04-24 00:00:00.000000
"""

from collections.abc import Sequence

from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "16e479c62349"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- notify chat members on new message ---
    op.execute(
        text(
            "CREATE OR REPLACE FUNCTION notify_chat_members_new_message() "
            "RETURNS TRIGGER AS $$ "
            "DECLARE "
            "    borrower_id INTEGER; "
            "    owner_id INTEGER; "
            "    payload TEXT; "
            "BEGIN "
            "    borrower_id := new.borrower_id; "
            "    SELECT item.owner_id INTO owner_id FROM item "
            "        WHERE item.id = new.item_id; "
            "    payload := json_build_object("
            "        'type', 'new_chat_message', "
            "        'chat_message_id', new.id"
            "    )::text; "
            "    PERFORM pg_notify(format('user%s', borrower_id), payload); "
            "    PERFORM pg_notify(format('user%s', owner_id), payload); "
            "    RETURN NEW; "
            "END; "
            "$$ LANGUAGE plpgsql;"
        )
    )

    op.execute(
        text(
            "CREATE OR REPLACE TRIGGER new_chat_message "
            "AFTER INSERT ON chat_message "
            "FOR EACH ROW "
            "EXECUTE FUNCTION notify_chat_members_new_message();"
        )
    )

    # --- set update_date on item update ---
    op.execute(
        text(
            "CREATE OR REPLACE FUNCTION set_update_date() "
            "RETURNS TRIGGER AS $$ "
            "BEGIN "
            "    NEW.update_date := now(); "
            "    RETURN NEW; "
            "END; "
            "$$ LANGUAGE plpgsql;"
        )
    )

    op.execute(
        text(
            "CREATE OR REPLACE TRIGGER set_update_date "
            "BEFORE UPDATE ON item "
            "FOR EACH ROW "
            "EXECUTE FUNCTION set_update_date();"
        )
    )


def downgrade() -> None:
    op.execute(text("DROP TRIGGER IF EXISTS set_update_date ON item"))
    op.execute(text("DROP FUNCTION IF EXISTS set_update_date"))
    op.execute(text("DROP TRIGGER IF EXISTS new_chat_message ON chat_message"))
    op.execute(text("DROP FUNCTION IF EXISTS notify_chat_members_new_message"))
