import subprocess
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

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
    return value


def confirm_prompt(msg: str) -> bool:
    answer = input(f"{_RED}{msg} [y/N]{_RESET} ").strip().lower()
    return answer == "y"


@asynccontextmanager
async def async_db_session() -> AsyncGenerator[AsyncSession]:
    from app.infrastructure.config import Config
    from app.infrastructure.database import create_session_maker

    config = Config.from_env()
    session_maker = create_session_maker(config.database.url)
    async with session_maker.begin() as session:
        yield session


def run_subprocess(cmd: list[str]) -> int:
    result = subprocess.run(cmd, check=False)
    return result.returncode
