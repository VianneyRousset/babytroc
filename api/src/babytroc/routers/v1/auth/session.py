from fastapi import status

from babytroc.domains.auth.schemas.session import AuthSession

from .annotations import maybe_client_id_annotation
from .router import router


@router.get("/session", status_code=status.HTTP_200_OK)
async def get_auth_session(
    client_id: maybe_client_id_annotation,
) -> AuthSession:
    """Return whether the client is currently logged in."""

    return AuthSession(logged_in=client_id is not None)
