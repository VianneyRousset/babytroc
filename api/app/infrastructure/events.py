import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)

type EventHandler = Callable[[Any, Any], Awaitable[None]]


@dataclass
class _Registration:
    handler: EventHandler
    critical: bool


_handlers: dict[type, list[_Registration]] = defaultdict(list)


def on(event_type: type, *, critical: bool = True):
    """Register a handler for an event type."""

    def decorator(fn: EventHandler):
        _handlers[event_type].append(_Registration(handler=fn, critical=critical))
        return fn

    return decorator


async def emit(db: Any, event: object) -> None:
    """Dispatch event to all registered handlers.

    Critical handlers propagate exceptions (rolling back the transaction).
    Non-critical handlers log and swallow exceptions.
    """
    for reg in _handlers[type(event)]:
        if reg.critical:
            await reg.handler(db, event)
        else:
            try:
                await reg.handler(db, event)
            except Exception:
                logger.exception(
                    "Non-critical handler %s failed for %s",
                    reg.handler.__name__,
                    type(event).__name__,
                )
