from app.clients.networking import dicebear

from .constants import BG, FG, RADIUS, SCALE


def get_avatar(
    seed: str,
    *,
    size: int,
) -> bytes:
    """Create an avatar of given `size` from `seed`."""

    return dicebear.generate_avatar(
        seed=seed,
        size=size,
        scale=SCALE,
        radius=RADIUS,
        bg=BG,
        fg=FG,
    )
