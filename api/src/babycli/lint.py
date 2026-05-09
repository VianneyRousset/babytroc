# src/babycli/lint.py
import sys
from typing import Annotated

from cyclopts import App, Parameter

from ._utils import console_err, console_ok, run_subprocess

lint_app = App(
    name="lint",
    help="Run code quality checks.",
)


@lint_app.command(name="ruff")
def lint_ruff():
    """Run ruff linter."""
    code = run_subprocess(["ruff", "check", "."])
    if code == 0:
        console_ok("ruff — no issues")
    else:
        console_err("ruff — issues found")
    sys.exit(code)


@lint_app.command(name="mypy")
def lint_mypy():
    """Run mypy type checker."""
    code = run_subprocess(["mypy", "stubs", "src", "tests"])
    if code == 0:
        console_ok("mypy — no issues")
    else:
        console_err("mypy — issues found")
    sys.exit(code)


@lint_app.command(name="boundaries")
def lint_boundaries(
    strict: Annotated[
        bool,
        Parameter(
            name="--strict",
            help="Also flag ambiguous cross-domain imports.",
        ),
    ] = False,
):
    """Run domain boundary violation check."""
    from .boundaries import check_boundaries

    violations = check_boundaries(strict=strict)
    if violations:
        console_err(
            f"Found {len(violations)} boundary violation(s):"
        )
        for v in violations:
            print(f"  {v}")
        console_err(
            "Fix: move cross-domain writes to event handlers"
        )
        sys.exit(1)
    else:
        console_ok("boundaries — no violations")


@lint_app.default
def lint_all():
    """Run all linters (ruff + mypy + boundaries)."""
    failed = False

    code = run_subprocess(["ruff", "check", "."])
    if code == 0:
        console_ok("ruff — no issues")
    else:
        console_err("ruff — issues found")
        failed = True

    code = run_subprocess(["mypy", "stubs", "src", "tests"])
    if code == 0:
        console_ok("mypy — no issues")
    else:
        console_err("mypy — issues found")
        failed = True

    from .boundaries import check_boundaries

    violations = check_boundaries()
    if not violations:
        console_ok("boundaries — no violations")
    else:
        console_err(
            f"boundaries — {len(violations)} violation(s) found"
        )
        for v in violations:
            print(f"  {v}")
        failed = True

    if failed:
        sys.exit(1)
