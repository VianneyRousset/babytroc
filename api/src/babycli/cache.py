# src/babycli/cache.py
import sys
from typing import Annotated

from cyclopts import App, Parameter

from ._utils import confirm_prompt, console_err, console_ok
from .danger import require_danger

cache_app = App(
    name="cache",
    help="Cache management.",
)


@cache_app.command(name="reset")
async def reset(
    danger: Annotated[
        bool,
        Parameter(name="--danger", help="Confirm destructive operation."),
    ] = False,
    yes: Annotated[
        bool,
        Parameter(name=["--yes", "-y"], help="Skip confirmation prompt."),
    ] = False,
):
    """Flush all keys from the configured Redis cache DB. DESTRUCTIVE."""
    from babytroc.infrastructure.config import RedisConfig
    from babytroc.infrastructure.redis import create_redis_client

    require_danger(danger_flag=danger)

    config = RedisConfig.from_env()
    target = f"{config.host}:{config.port}/{config.db}"
    prompt = f"This will FLUSH all keys on {target}. Continue?"
    if not yes and not confirm_prompt(prompt):
        print("Aborted.")
        return

    client = create_redis_client(config)
    try:
        await client.flushdb()
    except Exception as e:
        console_err(f"Cache reset failed — {e}")
        sys.exit(1)
    finally:
        await client.aclose()

    console_ok(f"Cache flushed on {target}")
