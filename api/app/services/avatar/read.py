from app import config
from app.clients.networking import dicebear


def get_avatar(
    seed: str,
    *,
    size: int,
) -> bytes:
    """Create an avatar of given `size` from `seed`."""

    return dicebear.generate_avatar(
        seed=seed,
        size=size,
        scale=config.AVATAR_SCALE,
        radius=config.AVATAR_RADIUS,
        bg=config.AVATAR_BG,
        fg=config.AVATAR_FG,
    )
