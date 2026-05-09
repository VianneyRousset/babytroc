# babycli/server.py
import sys
from typing import Annotated

from cyclopts import App, Parameter

from ._utils import console_ok, run_subprocess

server_app = App(
    name="server",
    help="Start the API server.",
)


@server_app.command(name="start")
def start(
    host: Annotated[
        str,
        Parameter(name="--host", help="Bind host."),
    ] = "0.0.0.0",  # noqa: S104
    port: Annotated[
        int,
        Parameter(name="--port", help="Bind port."),
    ] = 8080,
    workers: Annotated[
        int | None,
        Parameter(name="--workers", help="Number of worker processes."),
    ] = None,
    reload: Annotated[
        bool,
        Parameter(name="--reload", help="Enable auto-reload (dev only)."),
    ] = False,
):
    """Start uvicorn server (runs migrations first)."""
    migrate_code = run_subprocess(["alembic", "upgrade", "head"])
    if migrate_code != 0:
        sys.exit(migrate_code)
    console_ok("Migrations applied")

    cmd = [
        "uvicorn",
        "app.main:application",
        f"--host={host}",
        f"--port={port}",
    ]
    if workers is not None:
        cmd.append(f"--workers={workers}")
    if reload:
        cmd.append("--reload")

    console_ok(f"Starting server on {host}:{port}")
    code = run_subprocess(cmd)
    sys.exit(code)
