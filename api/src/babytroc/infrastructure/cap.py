import httpx

from babytroc.infrastructure.config import CapConfig


async def verify_cap_token(config: CapConfig, token: str) -> bool:
    """Verify a cap PoW token by calling the cap server's /siteverify endpoint.

    Returns False on any failure (HTTP non-200, network error, success=False,
    invalid JSON). Failure is fail-closed by design — see spec.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                f"{config.api_url}/{config.site_key}/siteverify",
                json={"secret": config.secret_key, "response": token},
            )
            if resp.status_code != 200:
                return False
            try:
                payload = resp.json()
            except ValueError:
                return False
            return payload.get("success") is True
    except httpx.HTTPError:
        return False
