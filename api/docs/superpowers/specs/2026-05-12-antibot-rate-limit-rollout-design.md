# Anti-Bot + Rate Limit Rollout

**Date:** 2026-05-12
**Status:** Draft
**Branch:** refactor/ddd-lite-restructure (or feature branch off it)

## Problem Statement

`POST /api/v1/utils/contact` already runs three defense layers — honeypot field, per-IP/per-user rate limiter, and `cap` PoW captcha — see `2026-05-10-contact-us-api-design.md`. Every other public mutation endpoint that creates server-side state currently runs none of them. Concretely:

- `POST /api/v1/auth/new` (user signup, anonymous) — uncapped account creation enables credential-stuffing prep, mailbox spam via the welcome email, and DB pollution.
- `POST /api/v1/auth/reset-password` (anonymous reset trigger) — uncapped means a single attacker can fan out reset emails to any harvested address.
- `POST /api/v1/me/items` (authenticated item creation) — once an account exists, an attacker can mass-create items consuming storage and search indices.
- `POST /api/v1/images` (authenticated image upload) — each call writes to S3 and the DB; uncapped uploads are an expensive abuse path even for legitimate accounts under takeover.

The contact endpoint reuses an existing `RateLimiter` class (`shared/rate_limit.py`) and `verify_cap_token` (`infrastructure/cap.py`), but the honeypot check, the per-endpoint rate-limit dependency wiring, and the `cap_token`/`website` schema fields are inlined in `routers/v1/utils/contact.py`. Rolling this out to four more endpoints without refactoring would copy three to five lines of identical glue per endpoint.

## Goals

- All five endpoints above run the same defense pipeline (where applicable per the matrix below).
- The honeypot + cap pair is a single reusable artifact (a pydantic mixin + an async helper) rather than copy-pasted code.
- The per-endpoint rate-limit dependency wiring (lazy-build, attach to `app.state`, call the limiter) is built from a single factory rather than copy-pasted per endpoint.
- Rate-limit configuration follows the contact endpoint's pattern: hardcoded sane defaults, env-overridable via a per-endpoint `*_RATE_LIMIT_{ANON,AUTH,WINDOW_SECONDS}` prefix.
- The existing `POST /utils/contact` endpoint is refactored to consume the new shared artifacts, with no behavior change visible to clients.
- Domain layer stays clean: services accept the same domain schemas they accept today (`UserCreate`, `ItemCreate`, `AuthAccountPasswordResetAuthorizationCreate`); the transport-only `cap_token` and `website` fields live only in router-layer request schemas.
- Existing tests for protected endpoints continue to pass with minimal changes (test fixtures stub the cap verifier and relax the rate limiter; see Testing).

## Non-Goals

- Adding honeypot/cap to `POST /api/v1/images`. The endpoint is `multipart/form-data` with a binary file body; adding a `cap_token` form field alongside the file is awkward, cap tokens can expire faster than realistic upload workflows, and the practical abuse vector requires both a valid account (gated by signup) and a later item creation (gated by item-create cap). Rate limit alone is sufficient there.
- Adding honeypot/cap/rate-limit to the reset-password *apply* step (`POST /api/v1/auth/reset-password/{authorization_code}`). It requires a valid UUID delivered by email, making bot abuse infeasible.
- Adding rate-limit to login. The login endpoint already exists and may need rate limiting for credential stuffing; that is a separate spec because login rate-limit semantics (per-account vs per-IP keying, lockout vs throttle) differ from these creation endpoints.
- Adding rate-limit to non-creation endpoints (reads, updates). Outside the scope of this design — would be its own spec.
- Building or operating the cap server. Same as the contact spec: we consume `/siteverify`.
- New env-var infrastructure beyond what the contact spec already established.
- GUI changes. The frontend will need to render the cap widget on signup, item creation, and password reset forms and include the `cap_token` in payloads, but that is tracked separately.

## Coverage Matrix

| Endpoint | Auth | Honeypot | Cap | Rate Limit | Default Limits |
| --- | --- | --- | --- | --- | --- |
| `POST /api/v1/auth/new` | anon | ✓ | ✓ | ✓ | 3/h anon |
| `POST /api/v1/auth/reset-password` | anon | ✓ | ✓ | ✓ | 3/h anon |
| `POST /api/v1/me/items` | auth | ✓ | ✓ | ✓ | 30/h auth |
| `POST /api/v1/images` | auth | — | — | ✓ | 60/h auth |
| `POST /api/v1/utils/contact` (refactor) | anon+auth | ✓ | ✓ | ✓ | existing: 5/h anon, 10/h auth |

All limits are env-overridable per the configuration section. The "auth" / "anon" qualifier in the limits column reflects which side of `RateLimiter` actually fires in practice — the inert side is set equal to the active side so the limiter is harmless in any unexpected auth state.

## Architecture

### File layout

```
src/babytroc/
├── infrastructure/
│   ├── config.py
│   │     - extract: RateLimitConfig (NamedTuple)
│   │     - ContactConfig: keeps `email`, switches to `rate_limit: RateLimitConfig`
│   │     - Config: adds `signup`, `password_reset`, `item_create`,
│   │                    `image_upload` of type RateLimitConfig
│   └── cap.py                            # unchanged
├── shared/
│   ├── antibot.py                        # NEW
│   └── rate_limit.py                     # +make_rate_limit_dep factory
├── routers/v1/
│   ├── auth/
│   │   ├── new.py                        # uses UserCreateRequest + deps
│   │   └── reset.py                      # uses PasswordResetRequest + deps
│   │                                       (only on the trigger endpoint)
│   ├── me/items/
│   │   └── create.py                     # uses ItemCreateRequest + deps
│   ├── images/
│   │   └── create.py                     # adds rate_limit dep only
│   └── utils/
│       └── contact.py                    # refactor to consume new shared bits

tests/
├── fixtures/
│   └── antibot.py                        # NEW: shared cap stub + limiter override helpers
├── auth/
│   ├── test_new.py                       # extend existing tests
│   └── test_reset.py                     # extend existing tests
├── item/
│   └── test_create.py                    # extend existing tests
├── image/
│   └── test_upload.py                    # extend existing tests
└── utils/
    └── test_contact.py                   # update to new shape (no behavior change)
```

### Shared: `shared/antibot.py`

```python
from typing import Annotated
from pydantic import BaseModel, StringConstraints

from babytroc.infrastructure.cap import verify_cap_token
from babytroc.infrastructure.config import CapConfig
from babytroc.shared.errors import BadRequestError


class AntiBotMixin(BaseModel):
    """Mixin contributing the transport-only anti-bot fields.

    Compose into router-layer request schemas. Domain schemas must NOT
    inherit this — services must not require cap_token/website.
    """
    cap_token: Annotated[str, StringConstraints(min_length=1, max_length=4096)]
    website: str = ""  # honeypot — bots fill, humans don't see


async def verify_antibot(payload: AntiBotMixin, cap_config: CapConfig) -> None:
    """Run honeypot + cap PoW check. Raise BadRequestError on either failure.

    Both rejections surface as the same shared 400 INVALID_SUBMISSION error
    so the response is not a probe oracle for which layer fired.
    """
    if payload.website:
        msg = "INVALID_SUBMISSION"
        raise BadRequestError(msg)
    if not await verify_cap_token(cap_config, payload.cap_token):
        msg = "INVALID_SUBMISSION"
        raise BadRequestError(msg)
```

`verify_antibot` is an ordinary async helper, not a FastAPI dependency. FastAPI dependencies cannot easily share the parsed request body with the handler without double-parsing; calling the helper from the endpoint handler is simpler and matches what the contact endpoint already does inline.

### Shared: `shared/rate_limit.py` factory

Today, the contact endpoint defines a `rate_limit_contact` dependency that:

1. Reads a cached `RateLimiter` from `request.app.state._contact_limiter`.
2. Builds one from `request.app.state.config.contact` on first call.
3. Caches it on `app.state` and invokes it.

This pattern is identical for every endpoint we add. Extract it:

```python
from collections.abc import Callable, Awaitable
from typing import Annotated

from fastapi import Depends, Request
from redis.asyncio import Redis

from babytroc.infrastructure.redis_dep import get_redis
from babytroc.routers.v1.auth.verification import maybe_verify_request_credentials
from babytroc.infrastructure.config import Config, RateLimitConfig


def make_rate_limit_dep(
    *,
    key_prefix: str,
    extract_config: Callable[[Config], RateLimitConfig],
) -> Callable[..., Awaitable[None]]:
    """Build a FastAPI dependency that applies the per-endpoint rate limiter.

    `extract_config` is a callable that pulls the relevant `RateLimitConfig`
    out of the global `Config` (e.g. `lambda c: c.signup` or
    `lambda c: c.contact.rate_limit`). This keeps the factory agnostic to
    whether the rate-limit config is a top-level field or nested.

    `key_prefix` is the Redis key namespace for the limiter
    (e.g. "signup", "item_create", "contact") and doubles as the cache key
    on `app.state` so each endpoint reuses its own lazily-built limiter.
    """
    cache_attr = f"_rate_limiter_{key_prefix}"

    async def dep(
        request: Request,
        redis: Annotated[Redis, Depends(get_redis)],
        client_id: Annotated[int | None, Depends(maybe_verify_request_credentials)],
    ) -> None:
        limiter = getattr(request.app.state, cache_attr, None)
        if limiter is None:
            config: Config = request.app.state.config
            rl_config = extract_config(config)
            limiter = RateLimiter(
                key_prefix=key_prefix,
                anon_limit=rl_config.anon,
                auth_limit=rl_config.auth,
                window=rl_config.window,
            )
            setattr(request.app.state, cache_attr, limiter)
        await limiter(request=request, redis=redis, client_id=client_id)

    return dep
```

Each endpoint declares its dependency in one line:

```python
# routers/v1/auth/new.py
rate_limit_signup = make_rate_limit_dep(
    key_prefix="signup",
    extract_config=lambda c: c.signup,
)
```

The factory references `RateLimitConfig` from `infrastructure/config.py` (see Configuration). The contact endpoint's bespoke `rate_limit_contact` function is replaced by:

```python
# routers/v1/utils/contact.py
rate_limit_contact = make_rate_limit_dep(
    key_prefix="contact",
    extract_config=lambda c: c.contact.rate_limit,
)
```

The callable form lets `ContactConfig` keep `rate_limit` as a nested `RateLimitConfig` field, avoiding a flat `Config.contact_rate_limit` next to `Config.contact`.

### Router-layer request schemas

Each protected endpoint gets a router-local request schema that composes the domain create schema with `AntiBotMixin`. The handler strips the antibot fields and passes the domain schema to the service unchanged.

```python
# routers/v1/auth/new.py
from babytroc.shared.antibot import AntiBotMixin, verify_antibot

class UserCreateRequest(AntiBotMixin, UserCreate):
    pass

rate_limit_signup = make_rate_limit_dep(key_prefix="signup", config_attr="signup")

@router.post("/new")
async def create_user(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    email_client: Annotated[FastMail, Depends(get_email_client)],
    background_tasks: BackgroundTasks,
    request: Request,
    response: Response,
    user_create_request: UserCreateRequest,
    _rate_limited: Annotated[None, Depends(rate_limit_signup)],
) -> UserCredentialsInfo:
    await verify_antibot(user_create_request, request.app.state.config.cap)

    user_create = UserCreate.model_validate(
        user_create_request.model_dump(exclude={"cap_token", "website"})
    )
    await user_services.create_user(
        db=db,
        email_client=email_client,
        host_name=request.app.state.config.host_name,
        app_name=request.app.state.config.app_name,
        background_tasks=background_tasks,
        user_create=user_create,
    )
    ...
```

The same pattern applies to:

- `ItemCreateRequest(AntiBotMixin, ItemCreate)` in `routers/v1/me/items/create.py`. The service signature for `create_item` is unchanged; the handler passes the stripped `ItemCreate`.
- `PasswordResetRequest(AntiBotMixin, AuthAccountPasswordResetAuthorizationCreate)` in `routers/v1/auth/reset.py`, applied only to `POST /reset-password`. The `apply_account_password_reset` endpoint at `POST /reset-password/{authorization_code}` is untouched.
- `ContactSubmit` (already router-local) is rebased onto `AntiBotMixin` instead of declaring `cap_token`/`website` inline.

For `POST /api/v1/images`: no schema change (the endpoint takes an `UploadFile`, not a JSON body). Only the rate-limit dependency is added:

```python
# routers/v1/images/create.py
rate_limit_image_upload = make_rate_limit_dep(
    key_prefix="image_upload", config_attr="image_upload",
)

@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_image(
    client_id: client_id_annotation,
    request: Request,
    response: Response,
    file: UploadFile,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    _rate_limited: Annotated[None, Depends(rate_limit_image_upload)],
) -> ItemImageRead:
    ...
```

### Endpoint flow (creation endpoints with antibot)

```
client → POST <endpoint>
  ↓
1. pydantic validation                        → 422 on failure
2. rate-limit dep (Redis INCR + EXPIRE)       → 429 RATE_LIMITED
3. honeypot check (website == "")             → 400 INVALID_SUBMISSION
4. cap.verify_cap_token (httpx → cap server)  → 400 INVALID_SUBMISSION (fail-closed)
5. domain service call (existing logic)       → 201 / 200 / 204
```

This matches the contact endpoint order with one deliberate change: rate-limit moves from step 3 to step 2 (before honeypot). Rationale: in the contact spec, honeypot is before rate-limit because honeypot is a constant-time string check and rate-limit involves a Redis round-trip. That ordering is correct when the bot population is naive (most won't fill the honeypot and would burn ratelimit slots on legitimate-looking but failing-cap submissions). However, putting rate-limit first means a misbehaving caller cannot use the honeypot path as a free probe channel against the API. The Redis call is well under 1 ms in our infra and the trade-off favours putting the cheapest bot-distinguishing check (rate-limit by identity) before the cheapest payload check.

Since the contact endpoint is being refactored, its order is updated to match — this is a deliberate minor behavior change for contact (no client-visible difference; the response is the same 400 either way unless the rate limit also trips).

Domain-level errors (e.g. "email already exists" in signup) remain inside service code and continue to surface as today's errors. They are only reachable after antibot + rate-limit pass.

### Configuration

Extract a generic `RateLimitConfig` and reshape `ContactConfig` to embed it:

```python
# infrastructure/config.py

class RateLimitConfig(NamedTuple):
    anon: int
    auth: int
    window: timedelta

    @classmethod
    def from_env(
        cls,
        *,
        env_prefix: str,
        default_anon: int,
        default_auth: int,
        default_window_seconds: int,
    ) -> Self:
        return cls(
            anon=int(_env(f"{env_prefix}_RATE_LIMIT_ANON", default=str(default_anon))),
            auth=int(_env(f"{env_prefix}_RATE_LIMIT_AUTH", default=str(default_auth))),
            window=timedelta(seconds=int(
                _env(f"{env_prefix}_RATE_LIMIT_WINDOW_SECONDS",
                     default=str(default_window_seconds)),
            )),
        )


class ContactConfig(NamedTuple):
    email: str
    rate_limit: RateLimitConfig

    @classmethod
    def from_env(
        cls,
        email: str | None = None,
        rate_limit: RateLimitConfig | None = None,
    ) -> Self:
        if email is None:
            email = _env("CONTACT_EMAIL")
        if rate_limit is None:
            rate_limit = RateLimitConfig.from_env(
                env_prefix="CONTACT",
                default_anon=5, default_auth=10, default_window_seconds=3600,
            )
        return cls(email=email, rate_limit=rate_limit)
```

`Config` gains four new top-level fields (signup, password_reset, item_create, image_upload), each a `RateLimitConfig`. `Config.contact` keeps its current shape but with `rate_limit` nested inside it (extracted via `lambda c: c.contact.rate_limit`).

| Config field | Extractor used in dep | Default anon | Default auth | Default window | Env prefix |
| --- | --- | --- | --- | --- | --- |
| `contact.rate_limit` | `lambda c: c.contact.rate_limit` | 5 | 10 | 3600 | `CONTACT` |
| `signup` | `lambda c: c.signup` | 3 | 3 | 3600 | `SIGNUP` |
| `password_reset` | `lambda c: c.password_reset` | 3 | 3 | 3600 | `PASSWORD_RESET` |
| `item_create` | `lambda c: c.item_create` | 30 | 30 | 3600 | `ITEM_CREATE` |
| `image_upload` | `lambda c: c.image_upload` | 60 | 60 | 3600 | `IMAGE_UPLOAD` |

For anon-only endpoints (signup, password_reset) we still set `auth == anon` so an authenticated client who somehow hits the endpoint is subject to the same limit. For auth-only endpoints (item_create, image_upload) we set `anon == auth` for symmetry; the rate limiter still keys by IP for anonymous callers, but those callers will be rejected with 401 by the auth dependency anyway.

Backwards compatibility: the existing `CONTACT_RATE_LIMIT_ANON`, `CONTACT_RATE_LIMIT_AUTH`, `CONTACT_RATE_LIMIT_WINDOW_SECONDS` env vars continue to work — they now feed `Config.contact.rate_limit` instead of the previous flat `ContactConfig.rate_limit_*` fields. The `CONTACT_EMAIL` env var continues to feed `Config.contact.email`. No env var renames.

### Order of dependencies in FastAPI

FastAPI runs `Depends(...)` declarations in declaration order before the handler body. The rate-limit dependency is declared first in the parameter list, then the handler body runs `await verify_antibot(...)`. This produces the documented step ordering.

For consistency, every protected endpoint follows the convention:

```python
async def handler(
    # 1. domain-required deps (db, email_client, auth, etc.)
    ...,
    # 2. request schema (the request body — also runs pydantic)
    request_schema: <RequestSchema>,
    # 3. rate-limit dep
    _rate_limited: Annotated[None, Depends(rate_limit_X)],
) -> ...:
    # 4. antibot (honeypot + cap)
    await verify_antibot(request_schema, request.app.state.config.cap)
    # 5. service call
    ...
```

## Security considerations

1. **Same INVALID_SUBMISSION code** for honeypot + cap-failure + cap-unreachable on each protected endpoint. Identical to contact; no per-endpoint oracle.
2. **Reset-password trigger** historically returns a generic success regardless of whether the email exists, to avoid an email-existence oracle. Adding antibot does not regress this — the antibot rejection happens before the email lookup, and the existing flow's "always-success" semantics on the trigger remain.
3. **Signup oracle.** Before this change, `POST /auth/new` could be used to enumerate registered emails (existing email → 4xx, new email → 200). With antibot gating, an attacker needs a valid `cap_token` per probe, raising the cost to roughly one PoW solution per email tested. The oracle is not eliminated, only made expensive; closing it fully would require returning a uniform response for both cases, which is a separate behavior change and out of scope here.
4. **Authenticated endpoints (item_create, image_upload).** Cap on item_create still adds value because a takeover-driven mass-create attack from a single account can be slowed without locking the account out. The auth limiter caps `auth_limit` requests per window per user_id; once tripped, the user gets 429 until the window expires. No account lockout — degraded rather than denied.
5. **Image upload — no cap.** Justified in Non-Goals. Rate limit by user_id caps per-account abuse; the upstream signup + item-create caps gate the practical multi-account abuse path.
6. **Fail-closed cap.** Same posture as contact: if cap server is unreachable, antibot rejects. Operators monitor cap health via `babycli check cap` (already exists per contact spec).
7. **Rate-limit window keys.** Each endpoint uses a distinct `key_prefix`, so e.g. exhausting your `signup` window doesn't lock you out of `password_reset`. Counters are isolated per endpoint.
8. **Reverse-proxy correctness.** As contact spec already states: uvicorn must be configured with `--proxy-headers` so `request.client.host` is the real client IP. This applies identically to all rate-limited endpoints.
9. **No persistence of rejected attempts.** As today — rate-limit counters are in Redis with TTL; rejected submissions don't write to PostgreSQL.

## Testing

New file `tests/fixtures/antibot.py` (registered via `tests/conftest.py::pytest_plugins`):

- `mock_cap_verify` (autouse, function scope): replaces `verify_cap_token` to return `True`. Tests opt out via `monkeypatch` or per-test override to exercise rejection paths. Shared between all five endpoint test modules.
- `loose_rate_limits` (autouse, function scope): override `app.state._rate_limiter_*` attributes (or override the `make_rate_limit_dep`-built deps) with limiters configured to 1000/60s, so default tests aren't dependent on production limits. Tight-limit tests opt in via a parametrized fixture.
- `tight_rate_limit_factory`: helper returning a fixture that swaps in a small-limit limiter for one specific endpoint, used by the rate-limit-specific test cases.

The existing contact fixtures in `tests/fixtures/contact.py` are absorbed into `tests/fixtures/antibot.py` (or contact.py imports from antibot.py) to avoid duplicate cap-stubbing.

Per-endpoint test additions (beyond what already exists):

**`tests/auth/test_new.py`** (signup):
- Happy path with valid `cap_token` and empty `website` → 201.
- Honeypot filled → 400 INVALID_SUBMISSION; no user created.
- Cap rejected → 400 INVALID_SUBMISSION; no user created.
- Rate-limit anon: N+1 signups from same IP → 429.

**`tests/auth/test_reset.py`** (reset trigger):
- Happy path → 200 with usual generic success.
- Honeypot filled → 400; no email enqueued.
- Cap rejected → 400; no email enqueued.
- Rate-limit anon: N+1 triggers from same IP → 429.
- Apply endpoint (`POST /reset-password/{code}`) unchanged tests still pass — no new layers added.

**`tests/item/test_create.py`** (item create):
- Happy path with valid antibot → 201.
- Honeypot filled → 400.
- Cap rejected → 400.
- Rate-limit auth: alice past auth limit → 429.

**`tests/image/test_upload.py`** (image upload):
- Existing happy-path tests still pass with `loose_rate_limits`.
- Rate-limit auth: alice past auth limit → 429 (no antibot fields needed).

**`tests/utils/test_contact.py`** (refactor):
- All existing tests continue to pass after the contact endpoint switches to the shared mixin and factory.
- The test for rate-limit-before-honeypot order is added (or the existing honeypot-before-ratelimit test is updated; see the order-change note in Endpoint flow).

Heavy test directories (`tests/item/`, `tests/loan/`, `tests/chat/`) already use class-scoped `database` fixture overrides per CLAUDE.md — antibot fixtures must be function-scoped and autouse to avoid leaking limiter state across tests within a class.

## Migration / operator setup

No database migration. No new required env vars — every new env var defaults to a sane production value. Optional env vars for tuning:

```
SIGNUP_RATE_LIMIT_ANON               default 3
SIGNUP_RATE_LIMIT_AUTH               default 3
SIGNUP_RATE_LIMIT_WINDOW_SECONDS     default 3600

PASSWORD_RESET_RATE_LIMIT_ANON       default 3
PASSWORD_RESET_RATE_LIMIT_AUTH       default 3
PASSWORD_RESET_RATE_LIMIT_WINDOW_SECONDS  default 3600

ITEM_CREATE_RATE_LIMIT_ANON          default 30
ITEM_CREATE_RATE_LIMIT_AUTH          default 30
ITEM_CREATE_RATE_LIMIT_WINDOW_SECONDS default 3600

IMAGE_UPLOAD_RATE_LIMIT_ANON         default 60
IMAGE_UPLOAD_RATE_LIMIT_AUTH         default 60
IMAGE_UPLOAD_RATE_LIMIT_WINDOW_SECONDS default 3600
```

`CAP_API_URL`, `CAP_SITE_KEY`, `CAP_SECRET_KEY` are already required (set by the contact rollout). No new cap-server credentials.

Frontend / GUI work (out of scope here but required for the user-facing flow):

- Render the cap widget on signup, item creation, and password reset forms.
- Include `cap_token` (from the widget) in the JSON body; omit `website`.
- Handle 400 INVALID_SUBMISSION (generic error message, re-show cap widget) and 429 RATE_LIMITED (cooldown message).

## Open questions

None blocking. Tuning the default limits is an operational concern that can iterate post-launch via env vars.
