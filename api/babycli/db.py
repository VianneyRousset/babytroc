# babycli/db.py
import sys
from pathlib import Path
from typing import Annotated

from cyclopts import App, Parameter

from ._utils import confirm_prompt, console_err, console_ok, run_subprocess
from .danger import require_danger

db_app = App(
    name="db",
    help="Database management (migrations, seed, reset).",
)

seed_app = App(
    name="seed",
    help="Seed database with dev data.",
)

db_app.command(seed_app)


@db_app.command(name="migrate")
def migrate():
    """Run alembic upgrade head."""
    code = run_subprocess(["alembic", "upgrade", "head"])
    if code != 0:
        console_err("Migration failed")
        sys.exit(code)
    console_ok("Migrations applied")


@db_app.command(name="downgrade")
def downgrade(
    revision: Annotated[
        str,
        Parameter(
            help="Target revision (default: -1 for one step back).",
        ),
    ] = "-1",
):
    """Run alembic downgrade."""
    code = run_subprocess(["alembic", "downgrade", revision])
    if code != 0:
        console_err("Downgrade failed")
        sys.exit(code)
    console_ok(f"Downgraded to {revision}")


@db_app.command(name="status")
def status():
    """Show current migration status."""
    run_subprocess(["alembic", "current"])


@db_app.command(name="reset")
def reset(
    danger: Annotated[
        bool,
        Parameter(name="--danger", help="Confirm destructive operation."),
    ] = False,
    with_seed: Annotated[
        bool,
        Parameter(name="--seed", help="Re-seed after reset."),
    ] = False,
):
    """Drop all tables and re-migrate. DESTRUCTIVE."""
    require_danger(danger_flag=danger)
    if not confirm_prompt("This will DROP ALL TABLES. Continue?"):
        print("Aborted.")
        return

    code = run_subprocess(["alembic", "downgrade", "base"])
    if code != 0:
        console_err("Downgrade to base failed")
        sys.exit(code)

    code = run_subprocess(["alembic", "upgrade", "head"])
    if code != 0:
        console_err("Re-migration failed")
        sys.exit(code)

    console_ok("Database reset complete")

    if with_seed:
        import asyncio
        from seed.__main__ import populate_all
        asyncio.run(populate_all())
        console_ok("Seed data populated")


@seed_app.command(name="all")
async def seed_all(
    data_file: Annotated[
        Path,
        Parameter(
            name="--data-file",
            help="File containing regions and users data.",
        ),
    ] = Path("seed/data/data.json"),
    items_count: Annotated[
        int,
        Parameter(
            name=["--items-count", "-n"],
            help="Total number of generated items.",
        ),
    ] = 50,
    force: Annotated[
        bool,
        Parameter(
            name=["--force", "-f"],
            help="Force populate even if already populated.",
        ),
    ] = False,
    danger: Annotated[
        bool,
        Parameter(name="--danger", help="Confirm destructive operation (required with --force)."),
    ] = False,
):
    """Populate all dev data (regions, categories, users, items)."""
    if force:
        require_danger(danger_flag=danger)

    from seed.__main__ import populate_all as _populate_all
    await _populate_all(fp=data_file, items_count=items_count, force=force)
    console_ok("Seed complete")


@seed_app.command(name="regions")
async def seed_regions(
    data_file: Annotated[
        Path,
        Parameter(name="--data-file", help="Data file."),
    ] = Path("seed/data/data.json"),
    force: Annotated[
        bool,
        Parameter(name=["--force", "-f"], help="Force re-populate."),
    ] = False,
):
    """Seed regions."""
    from seed.__main__ import populate_regions
    await populate_regions(fp=data_file, force=force)
    console_ok("Regions seeded")


@seed_app.command(name="categories")
async def seed_categories(
    data_file: Annotated[
        Path,
        Parameter(name="--data-file", help="Data file."),
    ] = Path("seed/data/data.json"),
    force: Annotated[
        bool,
        Parameter(name=["--force", "-f"], help="Force re-populate."),
    ] = False,
):
    """Seed categories."""
    from seed.__main__ import populate_categories
    await populate_categories(fp=data_file, force=force)
    console_ok("Categories seeded")


@seed_app.command(name="users")
async def seed_users(
    data_file: Annotated[
        Path,
        Parameter(name="--data-file", help="Data file."),
    ] = Path("seed/data/data.json"),
    force: Annotated[
        bool,
        Parameter(name=["--force", "-f"], help="Force re-populate."),
    ] = False,
):
    """Seed users."""
    from seed.__main__ import populate_users
    await populate_users(fp=data_file, force=force)
    console_ok("Users seeded")


@seed_app.command(name="items")
async def seed_items(
    items_count: Annotated[
        int,
        Parameter(name=["--items-count", "-n"], help="Number of items."),
    ] = 20,
    force: Annotated[
        bool,
        Parameter(name=["--force", "-f"], help="Force re-populate."),
    ] = False,
):
    """Seed items."""
    from seed.__main__ import populate_items
    await populate_items(items_count=items_count, force=force)
    console_ok("Items seeded")
