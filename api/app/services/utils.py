from app import config
from app.clients import dicebear


async def generate_avatar(
    size: int,
    seed: str,
) -> str:
    """Create an avatar of given `size` from `seed`."""

    return dicebear.generate_avatar(
        size=size,
        seed=seed,
        scale=config.avatar.scale,
        radius=config.avatar.radius,
        bg=config.avatar.bg,
        fg=config.avatar.fg,
    )
