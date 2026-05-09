# babycli/user.py
import sys
from typing import Annotated

from cyclopts import App, Parameter
from sqlalchemy import func, or_, select

from ._utils import async_db_session, confirm_prompt, console_err, console_ok
from .danger import require_danger

user_app = App(
    name="user",
    help="User administration.",
)


def _print_user(user) -> None:
    print(f"  ID:        {user.id}")
    print(f"  Name:      {user.name}")
    print(f"  Email:     {user.email}")
    print(f"  Validated: {user.validated}")
    print(f"  Disabled:  {user.disabled}")
    print(f"  Stars:     {user.stars_count}")
    print(f"  Created:   {user.creation_date}")
    print()


@user_app.command(name="list")
async def user_list(
    limit: Annotated[
        int,
        Parameter(name="--limit", help="Max results."),
    ] = 20,
    offset: Annotated[
        int,
        Parameter(name="--offset", help="Skip N results."),
    ] = 0,
):
    """List users."""
    from babytroc.domains.user.models import User

    async with async_db_session() as db:
        result = await db.execute(
            select(User).order_by(User.id).limit(limit).offset(offset)
        )
        users = result.scalars().all()
        total = (await db.execute(select(func.count(User.id)))).scalar() or 0

    print(f"\n  Users ({offset+1}-{offset+len(users)} of {total})")
    print(f"  {'ID':<6} {'Name':<20} {'Email':<30} {'Valid':>5} {'Dis':>4}")
    print(f"  {'─' * 67}")
    for u in users:
        dis = "Y" if u.disabled else ""
        val = "Y" if u.validated else ""
        print(f"  {u.id:<6} {u.name:<20} {u.email:<30} {val:>5} {dis:>4}")
    print()


@user_app.command(name="get")
async def user_get(
    user_id: Annotated[int, Parameter(help="User ID.")],
):
    """Show user details."""
    from babytroc.domains.user.models import User

    async with async_db_session() as db:
        user = await db.get(User, user_id)
    if user is None:
        console_err(f"User {user_id} not found")
        sys.exit(1)
    _print_user(user)


@user_app.command(name="search")
async def user_search(
    query: Annotated[str, Parameter(help="Search by name or email.")],
):
    """Search users by name or email."""
    from babytroc.domains.user.models import User

    pattern = f"%{query}%"
    async with async_db_session() as db:
        result = await db.execute(
            select(User).where(
                or_(User.name.ilike(pattern), User.email.ilike(pattern))
            ).limit(20)
        )
        users = result.scalars().all()

    if not users:
        print("  No users found.")
        return

    for u in users:
        _print_user(u)


@user_app.command(name="create")
async def user_create(
    email: Annotated[str, Parameter(name="--email", help="User email.")],
    name: Annotated[str, Parameter(name="--name", help="Username.")],
    password: Annotated[str, Parameter(name="--password", help="Password.")],
    danger: Annotated[
        bool,
        Parameter(name="--danger", help="Confirm destructive operation."),
    ] = False,
):
    """Create a user (bypasses auth flow). DANGER."""
    require_danger(danger_flag=danger)
    if not confirm_prompt(f"Create user '{name}' <{email}>?"):
        print("Aborted.")
        return

    from babytroc.domains.user.models import User
    from babytroc.shared.hash import HashedStr

    async with async_db_session() as db:
        user = User(
            email=email,
            name=name,
            password_hash=HashedStr(password),
            validated=True,
        )
        db.add(user)
        await db.flush()
        console_ok(f"User created — ID: {user.id}")


@user_app.command(name="disable")
async def user_disable(
    user_id: Annotated[int, Parameter(help="User ID.")],
    danger: Annotated[
        bool,
        Parameter(name="--danger", help="Confirm destructive operation."),
    ] = False,
):
    """Disable a user account. DANGER."""
    require_danger(danger_flag=danger)
    from babytroc.domains.user.models import User

    async with async_db_session() as db:
        user = await db.get(User, user_id)
        if user is None:
            console_err(f"User {user_id} not found")
            sys.exit(1)
        if not confirm_prompt(f"Disable user '{user.name}' (ID: {user_id})?"):
            print("Aborted.")
            return
        user.disabled = True
        console_ok(f"User {user_id} disabled")


@user_app.command(name="enable")
async def user_enable(
    user_id: Annotated[int, Parameter(help="User ID.")],
):
    """Re-enable a user account."""
    from babytroc.domains.user.models import User

    async with async_db_session() as db:
        user = await db.get(User, user_id)
        if user is None:
            console_err(f"User {user_id} not found")
            sys.exit(1)
        user.disabled = False
        console_ok(f"User {user_id} enabled")


@user_app.command(name="reset-password")
async def user_reset_password(
    user_id: Annotated[int, Parameter(help="User ID.")],
    new_password: Annotated[str, Parameter(name="--password", help="New password.")],
    danger: Annotated[
        bool,
        Parameter(name="--danger", help="Confirm destructive operation."),
    ] = False,
):
    """Force-reset a user's password. DANGER."""
    require_danger(danger_flag=danger)
    from babytroc.domains.user.models import User
    from babytroc.shared.hash import HashedStr

    async with async_db_session() as db:
        user = await db.get(User, user_id)
        if user is None:
            console_err(f"User {user_id} not found")
            sys.exit(1)
        msg = f"Reset password for '{user.name}' (ID: {user_id})?"
        if not confirm_prompt(msg):
            print("Aborted.")
            return
        user.password_hash = HashedStr(new_password)
        console_ok(f"Password reset for user {user_id}")


@user_app.command(name="delete")
async def user_delete(
    user_id: Annotated[int, Parameter(help="User ID.")],
    danger: Annotated[
        bool,
        Parameter(name="--danger", help="Confirm destructive operation."),
    ] = False,
):
    """Delete a user. DANGER."""
    require_danger(danger_flag=danger)
    from babytroc.domains.user.models import User

    async with async_db_session() as db:
        user = await db.get(User, user_id)
        if user is None:
            console_err(f"User {user_id} not found")
            sys.exit(1)
        msg = f"DELETE user '{user.name}' (ID: {user_id})? Cannot be undone."
        if not confirm_prompt(msg):
            print("Aborted.")
            return
        await db.delete(user)
        console_ok(f"User {user_id} deleted")
