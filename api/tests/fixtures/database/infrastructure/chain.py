"""Template chain build engine.

A `TemplateSpec` declares one named template: its parent (or None for the
root), the alembic-applied flag, and a list of seed callables. `build_chain`
walks the registry in topological order, creating each template via
`CREATE DATABASE … TEMPLATE`, optionally running alembic, and running the
seed callables inside a single transaction. Each step disposes its engine
so the next `CREATE DATABASE TEMPLATE` of this DB has no active connections.

Seed signature: `async def seed(db: AsyncSession, ctx: SeedContext) -> None`.
Every seed receives the same `SeedContext` object — fields it doesn't need
are simply ignored. This avoids per-template kwargs plumbing.
"""

from __future__ import annotations

import asyncio
import contextlib
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

from alembic.config import Config as AlembicConfig

from alembic import command
from tests.fixtures.database.infrastructure.admin import (
    create_database,
    drop_database,
    run_against,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from sqlalchemy import URL
    from sqlalchemy.ext.asyncio import AsyncSession

    from babytroc.infrastructure.config import Config


@dataclass(frozen=True)
class SeedContext:
    """Cross-cutting context every seed receives.

    `db_url` is the URL of the template under construction. Seeds that need
    multiple transactions (e.g. to advance postgres `now()` between
    `execute_many_loan_requests` and `end_many_loans`) can open extra
    sessions against this URL via `session_against`.
    """

    config: Config
    db_url: URL


type SeedFn = Callable[[AsyncSession, SeedContext], Awaitable[None]]


@dataclass(frozen=True)
class TemplateSpec:
    """One template node in the chain."""

    name: str
    parent: str | None
    seeds: tuple[SeedFn, ...] = ()
    apply_alembic: bool = False


def _topo_sort(specs: dict[str, TemplateSpec]) -> list[str]:
    visited: set[str] = set()
    order: list[str] = []

    def visit(name: str, stack: tuple[str, ...]) -> None:
        if name in visited:
            return
        if name in stack:
            cycle = " → ".join((*stack, name))
            msg = f"Template chain cycle: {cycle}"
            raise ValueError(msg)
        spec = specs[name]
        if spec.parent is not None:
            visit(spec.parent, (*stack, name))
        visited.add(name)
        order.append(name)

    for n in specs:
        visit(n, ())
    return order


def _alembic_upgrade_head(url: URL) -> None:
    project_root = Path(__file__).resolve().parents[4]
    cfg = AlembicConfig(project_root / "alembic.ini")
    cfg.set_main_option("script_location", str(project_root / "alembic"))
    cfg.set_main_option("sqlalchemy.url", url.render_as_string(hide_password=False))
    command.upgrade(cfg, "head")


def _make_url(base: URL, *, name: str, worker_id: str) -> URL:
    return base._replace(database=f"tpl-{name}-{worker_id}-{uuid4().hex[:8]}")


def _run_seeds(
    seeds: tuple[SeedFn, ...],
    ctx: SeedContext,
) -> Callable[[AsyncSession], Awaitable[None]]:
    async def _run(session: AsyncSession) -> None:
        for seed in seeds:
            await seed(session, ctx)

    return _run


async def build_chain(
    *,
    base_url: URL,
    worker_id: str,
    specs: dict[str, TemplateSpec],
    ctx: SeedContext,
) -> dict[str, URL]:
    """Build every template in `specs` in topological order. Returns name → URL."""
    order = _topo_sort(specs)
    urls: dict[str, URL] = {}

    for name in order:
        spec = specs[name]
        url = _make_url(base_url, name=name, worker_id=worker_id)
        parent_db = urls[spec.parent].database if spec.parent else None
        await create_database(url, template=parent_db)

        if spec.apply_alembic:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, partial(_alembic_upgrade_head, url))

        if spec.seeds:
            node_ctx = SeedContext(config=ctx.config, db_url=url)
            await run_against(url, _run_seeds(spec.seeds, node_ctx))

        urls[name] = url

    return urls


async def teardown_chain(urls: dict[str, URL]) -> None:
    """Drop all chain DBs in reverse order. Errors on individual drops are swallowed."""
    for url in reversed(list(urls.values())):
        with contextlib.suppress(Exception):
            await drop_database(url)
