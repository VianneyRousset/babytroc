from typing import Annotated

from pydantic import BaseModel, StringConstraints

from babytroc.infrastructure.cap import verify_cap_token
from babytroc.infrastructure.config import CapConfig
from babytroc.shared.errors import BadRequestError


class AntiBotMixin(BaseModel):
    """Mixin contributing transport-only anti-bot fields.

    Compose into router-layer request schemas; never inherit into domain
    schemas — services must not require cap_token/website.
    """

    cap_token: Annotated[str, StringConstraints(min_length=1, max_length=4096)]
    website: str = ""  # honeypot — bots fill, humans don't see


async def verify_antibot(payload: AntiBotMixin, cap_config: CapConfig) -> None:
    """Run honeypot then cap PoW check. Raise BadRequestError on either failure.

    Both rejections surface as the same shared 400 INVALID_SUBMISSION error
    so the response cannot be used as a probe oracle for which layer fired.
    """
    if payload.website:
        msg = "INVALID_SUBMISSION"
        raise BadRequestError(msg)
    if not await verify_cap_token(cap_config, payload.cap_token):
        msg = "INVALID_SUBMISSION"
        raise BadRequestError(msg)
