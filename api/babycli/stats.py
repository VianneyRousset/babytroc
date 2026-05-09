# babycli/stats.py
from cyclopts import App
from sqlalchemy import func, select

from ._utils import async_db_session, console_ok

stats_app = App(
    name="stats",
    help="Show database statistics.",
)


def _print_table(title: str, rows: list[tuple[str, int | str]]) -> None:
    print(f"\n  {title}")
    print(f"  {'─' * 35}")
    for label, value in rows:
        print(f"  {label:<25} {value:>8}")
    print()


@stats_app.command(name="users")
async def stats_users():
    """Show user statistics."""
    from app.domains.user.models import User

    async with async_db_session() as db:
        total = (await db.execute(select(func.count(User.id)))).scalar() or 0
        q = select(func.count(User.id)).where(User.validated.is_(True))
        validated = (await db.execute(q)).scalar() or 0
        unvalidated = total - validated

    _print_table("Users", [
        ("Total", total),
        ("Validated", validated),
        ("Unvalidated", unvalidated),
    ])


@stats_app.command(name="items")
async def stats_items():
    """Show item statistics."""
    from app.domains.item.models.item import Item

    async with async_db_session() as db:
        total = (await db.execute(select(func.count(Item.id)))).scalar() or 0
        blocked = (
            await db.execute(select(func.count(Item.id)).where(Item.blocked.is_(True)))
        ).scalar() or 0

    _print_table("Items", [
        ("Total", total),
        ("Blocked", blocked),
        ("Available", total - blocked),
    ])


@stats_app.command(name="loans")
async def stats_loans():
    """Show loan statistics."""
    from app.domains.loan.models import Loan, LoanRequest, LoanRequestState

    async with async_db_session() as db:
        q = select(func.count(LoanRequest.id))
        total_requests = (await db.execute(q)).scalar() or 0
        pending = (
            await db.execute(
                select(func.count(LoanRequest.id)).where(
                    LoanRequest.state == LoanRequestState.pending
                )
            )
        ).scalar() or 0
        accepted = (
            await db.execute(
                select(func.count(LoanRequest.id)).where(
                    LoanRequest.state == LoanRequestState.accepted
                )
            )
        ).scalar() or 0

        total_loans = (await db.execute(select(func.count(Loan.id)))).scalar() or 0
        # Loan.active is a hybrid property without SQL expression,
        # so filter on the underlying range column: upper bound is NULL = active
        active_loans = (
            await db.execute(
                select(func.count(Loan.id)).where(
                    func.upper(Loan.during).is_(None)
                )
            )
        ).scalar() or 0

    _print_table("Loan Requests", [
        ("Total", total_requests),
        ("Pending", pending),
        ("Accepted", accepted),
    ])
    _print_table("Loans", [
        ("Total", total_loans),
        ("Active", active_loans),
        ("Returned", total_loans - active_loans),
    ])


@stats_app.command(name="chats")
async def stats_chats():
    """Show chat statistics."""
    from app.domains.chat.models import Chat, ChatMessage

    async with async_db_session() as db:
        q = select(func.count()).select_from(Chat)
        total_chats = (await db.execute(q)).scalar() or 0
        q = select(func.count(ChatMessage.id))
        total_messages = (await db.execute(q)).scalar() or 0
        unread = (
            await db.execute(
                select(func.count(ChatMessage.id)).where(ChatMessage.seen.is_(False))
            )
        ).scalar() or 0

    _print_table("Chats", [
        ("Total chats", total_chats),
        ("Total messages", total_messages),
        ("Unread messages", unread),
    ])


@stats_app.default
async def stats_all():
    """Show all statistics."""
    await stats_users()
    await stats_items()
    await stats_loans()
    await stats_chats()
    console_ok("Stats complete")
