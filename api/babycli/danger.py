import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

from cyclopts import App, Parameter

from ._utils import console_err, console_ok, console_warn, confirm_prompt

DANGER_DIR = Path.home() / ".babytroc"
DANGER_FILE_NAME = ".danger-mode"

danger_mode_app = App(
    name="danger-mode",
    help="Enable/disable danger mode for destructive operations.",
)


def _get_danger_file() -> Path:
    return DANGER_DIR / DANGER_FILE_NAME


def _write_danger_file(ttl_minutes: int) -> None:
    DANGER_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "enabled_at": datetime.now(tz=timezone.utc).isoformat(),
        "ttl_minutes": ttl_minutes,
    }
    _get_danger_file().write_text(json.dumps(data))


def _read_danger_file() -> dict | None:
    fp = _get_danger_file()
    if not fp.exists():
        return None
    try:
        return json.loads(fp.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _clear_danger_file() -> None:
    fp = _get_danger_file()
    if fp.exists():
        fp.unlink()


def is_danger_mode() -> bool:
    data = _read_danger_file()
    if data is None:
        return False
    enabled_at = datetime.fromisoformat(data["enabled_at"])
    ttl_minutes = data["ttl_minutes"]
    now = datetime.now(tz=timezone.utc)
    if enabled_at.tzinfo is None:
        enabled_at = enabled_at.replace(tzinfo=timezone.utc)
    elapsed = (now - enabled_at).total_seconds() / 60
    if elapsed > ttl_minutes:
        _clear_danger_file()
        return False
    return True


def remaining_minutes() -> float:
    data = _read_danger_file()
    if data is None:
        return 0.0
    enabled_at = datetime.fromisoformat(data["enabled_at"])
    if enabled_at.tzinfo is None:
        enabled_at = enabled_at.replace(tzinfo=timezone.utc)
    ttl_minutes = data["ttl_minutes"]
    now = datetime.now(tz=timezone.utc)
    elapsed = (now - enabled_at).total_seconds() / 60
    return max(0.0, ttl_minutes - elapsed)


def require_danger(*, danger_flag: bool) -> None:
    if danger_flag or is_danger_mode():
        return
    console_err(
        "This command requires danger mode. "
        "Use --danger flag or run: babycli danger-mode enable"
    )
    sys.exit(1)


@danger_mode_app.command(name="enable")
def enable(
    ttl: Annotated[
        int,
        Parameter(
            name="--ttl",
            help="Time-to-live in minutes.",
        ),
    ] = 5,
):
    """Enable danger mode for destructive operations."""
    _write_danger_file(ttl_minutes=ttl)
    console_warn(f"Danger mode ON (expires in {ttl} minutes)")


@danger_mode_app.command(name="disable")
def disable():
    """Disable danger mode."""
    _clear_danger_file()
    console_ok("Danger mode OFF")


@danger_mode_app.command(name="status")
def status():
    """Show danger mode status."""
    if is_danger_mode():
        mins = remaining_minutes()
        console_warn(f"Danger mode ACTIVE — {mins:.1f} minutes remaining")
    else:
        console_ok("Danger mode is OFF")
