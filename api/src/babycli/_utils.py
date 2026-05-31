import subprocess
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from urllib.parse import urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession

# ANSI color codes
_GREEN = "\x1b[32m"
_RED = "\x1b[31m"
_YELLOW = "\x1b[33m"
_RESET = "\x1b[0m"

_SECRET_PATTERNS = ("PASSWORD", "SECRET", "KEY", "TOKEN")


def console_ok(msg: str) -> None:
    print(f"{_GREEN}[OK]{_RESET} {msg}")


def console_err(msg: str) -> None:
    print(f"{_RED}[FAIL]{_RESET} {msg}")


def console_warn(msg: str) -> None:
    print(f"{_YELLOW}[WARN]{_RESET} {msg}")


def redact_secrets(key: str, value: str) -> str:
    upper = key.upper()
    if any(p in upper for p in _SECRET_PATTERNS):
        return "***"
    return _mask_url_userinfo(value)


def _mask_url_userinfo(value: str) -> str:
    if "://" not in value:
        return value
    try:
        parsed = urlparse(value)
    except ValueError:
        return value
    if not (parsed.username or parsed.password):
        return value
    host = parsed.hostname or ""
    if host and ":" in host:
        host = f"[{host}]"
    netloc = f"***@{host}:{parsed.port}" if parsed.port else f"***@{host}"
    return urlunparse(parsed._replace(netloc=netloc))


def confirm_prompt(msg: str) -> bool:
    answer = input(f"{_RED}{msg} [y/N]{_RESET} ").strip().lower()
    return answer == "y"


@asynccontextmanager
async def async_db_session(test: bool | None = None) -> AsyncGenerator[AsyncSession]:
    from babytroc.infrastructure.config import DatabaseConfig
    from babytroc.infrastructure.database import create_session_maker

    config = DatabaseConfig.from_env(test=test)
    session_maker = create_session_maker(config.url)
    async with session_maker.begin() as session:
        yield session


def run_subprocess(cmd: list[str]) -> int:
    result = subprocess.run(cmd, check=False)  # noqa: S603
    return result.returncode
