# Design: `GET /v1/auth/session`

**Date:** 2026-06-20

## Purpose

Let a client check whether its current credentials are valid without
triggering a 401. The endpoint always returns `200` with a boolean body, so
the frontend can branch on login state without treating an error as the
expected "not logged in" case.

## Endpoint

- `GET /v1/auth/session`
- Auth: **optional**. Uses the existing `maybe_client_id_annotation`
  (`Depends(maybe_verify_request_credentials)`), which reads the access token
  from the `Authorization` header or cookie and returns the user id or `None`.
- No DB query. The dependency already resolves identity from the token; the
  handler only maps `id -> bool`.

## Response schema

New schema in `src/babytroc/domains/auth/schemas/`, extending `AuthBase`:

```python
class AuthSession(AuthBase):
    logged_in: bool
```

Response body: `{"logged_in": true}` or `{"logged_in": false}`, status `200`.

## Handler

New file `src/babytroc/routers/v1/auth/session.py`, registered in
`src/babytroc/routers/v1/auth/__init__.py` alongside the other endpoints:

```python
@router.get("/session", status_code=status.HTTP_200_OK)
async def get_auth_session(
    client_id: maybe_client_id_annotation,
) -> AuthSession:
    """Return whether the client is currently logged in."""
    return AuthSession(logged_in=client_id is not None)
```

## Semantics

`logged_in` reflects a **validated** session. The optional dependency wraps
`verify_request_credentials`, which treats an unvalidated account as invalid.
A logged-in-but-unvalidated user therefore gets `logged_in: false`. This
matches what every other protected endpoint enforces. No separate flag for the
unvalidated case (YAGNI).

## Testing (`tests/auth/`)

- `alice_client` (logged in) -> `200 {"logged_in": true}`
- unauthenticated client -> `200 {"logged_in": false}`
- garbage / expired token -> `200 {"logged_in": false}`

## Out of scope

- Returning user data (use `GET /me/`).
- Refresh-token state or token-expiry info.
