"""drop notify_chat_members_new_message trigger

Revision ID: b657e37b3704
Revises: 5b5c5a10390e
Create Date: 2026-05-04 23:41:23.556895
"""

from collections.abc import Sequence

from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b657e37b3704"
down_revision: str | None = "5b5c5a10390e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(text("DROP TRIGGER IF EXISTS new_chat_message ON chat_message"))
    op.execute(text("DROP FUNCTION IF EXISTS notify_chat_members_new_message"))


def downgrade() -> None:
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
