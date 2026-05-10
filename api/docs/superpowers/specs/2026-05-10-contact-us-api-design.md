# Contact Us API

**Date:** 2026-05-10
**Status:** Draft
**Branch:** refactor/ddd-lite-restructure (or feature branch off it)

## Problem Statement

The frontend page `gui/app/pages/me/contact.vue` collects a name, email, subject, and message but currently has no backend to send it anywhere. We need a `POST /api/v1/utils/contact` endpoint that forwards submissions by email to a configurable address (default recipient: `contact@babytroc.ch`, sourced from `CONTACT_EMAIL` env var, never hardcoded).

The endpoint must be safe to expose without authentication (the GUI page lives under `/me/` but the form must work for both anonymous visitors and logged-in users), which means defense against spam, abuse, and email injection is part of the contract — not a follow-up.

## Goals

- `POST /api/v1/utils/contact` accepts both anonymous and authenticated submissions.
- Email is delivered to the address in `CONTACT_EMAIL`; no hardcoded recipient anywhere in the codebase.
- Three independent abuse-prevention layers: honeypot field, per-IP/per-user rate limiting, and `cap` PoW captcha verification.
- Rate limiter is implemented as a reusable component (other endpoints can adopt it later without refactoring).
- `cap` server reachability is verifiable via `babycli check cap` and is part of `babycli check` aggregate.
- All user-supplied content is HTML-escaped before being placed in the outgoing email body; `Reply-To` is the submitter's email so support staff can reply directly.
- Tests cover happy path (anon + auth), each rejection layer, and HTML-injection safety.

## Non-Goals

- Persisting submissions in the database (email is the record of truth).
- Building or operating the cap server itself — it runs as an external Docker service operated separately. We only consume its `/siteverify` endpoint.
- Replacing existing email infrastructure (`fastapi_mail` + `FastMail` client). We add a new sender module alongside `email_auth.py` and `email_report.py`.
- Internationalisation of the email body (English/French copy) — fixed English in v1, can be revisited.
- A general-purpose middleware-level rate limiter. The reusable component is a `Depends`-friendly class, scoped per endpoint by instantiation.
- Replacing `BackgroundTasks` with a job queue. Failed SMTP sends are lost; that matches existing `email_auth.py` behavior and is acceptable for a contact form.

## Architecture

### File layout

```
src/babytroc/
├── infrastructure/
│   ├── config.py                 # +ContactConfig, +CapConfig in Config
│   ├── email_contact.py          # NEW: send_contact_email()
│   └── cap.py                    # NEW: verify_cap_token()
├── routers/v1/
│   └── utils/                    # PROMOTE utils.py → utils/ package
│       ├── __init__.py           # router aggregator
│       ├── regions.py            # extracted from utils.py
│       ├── categories.py         # extracted from utils.py
│       └── contact.py            # NEW: POST /utils/contact
├── shared/
│   └── rate_limit.py             # NEW: reusable RateLimiter dep class
└── (other modules unchanged)

src/babycli/
└── check.py                      # +check_cap() + 'cap' subcommand

tests/
├── fixtures/
│   └── contact.py                # NEW: cap stub, rate-limit override
└── utils/
    └── test_contact.py           # NEW
```

`routers/v1/utils.py` becomes a package because it now hosts three sibling endpoint groups (regions, categories, contact). The aggregating router in `routers/v1/utils/__init__.py` keeps the existing `/utils` prefix from `routers/v1/__init__.py` — no caller changes.

### Endpoint contract

```
POST /api/v1/utils/contact
Content-Type: application/json
Authorization: Bearer <token>     (optional)

{
  "name":      string,  1..100 chars, trimmed
  "email":     EmailStr,
  "subject":   string,  1..200 chars, trimmed
  "message":   string,  1..5000 chars, trimmed
  "cap_token": string,                 # cap PoW solution token
  "website":   string,  optional       # honeypot — must be empty/missing
}

→ 204 No Content                      success
→ 400 INVALID_SUBMISSION              honeypot filled OR cap rejected OR cap unreachable
→ 422 Unprocessable Entity            pydantic validation failure (length, email format)
→ 429 RATE_LIMITED                    over the per-IP or per-user window
```

A single shared error code (`INVALID_SUBMISSION`) is returned for honeypot, captcha, and cap-server failures so the response cannot be used as an oracle to identify which layer fired.

### Submission flow

```
client → POST /api/v1/utils/contact
  ↓
1. pydantic validation                        → 422 on failure
2. honeypot check (website == "")             → 400 INVALID_SUBMISSION
3. RateLimiter dep (Redis INCR + EXPIRE)      → 429 RATE_LIMITED
4. cap.verify_cap_token (httpx → cap server)  → 400 INVALID_SUBMISSION (fail-closed)
5. resolve optional current user
6. background_tasks.add_task(send_contact_email, …)
7. return 204
```

Order is intentional. Pydantic comes first because it is the cheapest gate and FastAPI runs it before handler code anyway. Honeypot is a constant-time string check. Rate limiting comes before cap so an attacker cannot exhaust the cap server with garbage tokens. Cap verification (an outbound HTTP call) is last among the gates.

### Reusable rate limiter

`shared/rate_limit.py`:

```python
class RateLimiter:
    def __init__(
        self,
        *,
        key_prefix: str,
        anon_limit: int,
        auth_limit: int,
        window: timedelta,
    ) -> None: ...

    async def __call__(
        self,
        request: Request,
        cache: Annotated[Cache, Depends(get_cache)],
        client_id: Annotated[int | None, Depends(maybe_verify_request_credentials)],
    ) -> None:
        # key = f"ratelimit:{key_prefix}:user:{client_id}"  if authenticated
        #       f"ratelimit:{key_prefix}:ip:{request.client.host}"  if anonymous
        # limit = auth_limit if authenticated else anon_limit
        # INCR key → if value == 1: EXPIRE key window
        # if value > limit: raise HTTPException(429, code=RATE_LIMITED)
```

The contact endpoint instantiates one configured from `ContactConfig`:

```python
rate_limit_contact = RateLimiter(
    key_prefix="contact",
    anon_limit=config.contact.rate_limit_anon,
    auth_limit=config.contact.rate_limit_auth,
    window=config.contact.rate_limit_window,
)
```

Future endpoints (`auth/login`, `auth/reset`, etc.) can adopt the limiter by instantiating their own. Key prefix isolates counters per endpoint; one user spamming `contact` does not affect their `login` quota.

### Cap integration

`cap` runs as an external Docker container outside this codebase. The API only calls its `siteverify` endpoint:

```python
# infrastructure/cap.py
async def verify_cap_token(config: CapConfig, token: str) -> bool:
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.post(
            f"{config.api_url}/{config.site_key}/siteverify",
            json={"secret": config.secret_key, "response": token},
        )
        if resp.status_code != 200:
            return False
        return resp.json().get("success") is True
```

If the cap server is unreachable or returns a non-success body, the verifier returns `False` and the endpoint returns `400 INVALID_SUBMISSION` — fail-closed. This is the conservative choice: when the captcha layer breaks, we reject submissions rather than allow attackers to bypass it. Operators are expected to monitor cap availability via `babycli check cap` and the `/utils/contact` 400 rate.

In tests, `verify_cap_token` is replaced via FastAPI dependency override (see Testing section). Production code does not branch on `Config.test` for the captcha layer — the test/production split is purely at the DI boundary.

### Email sender

`infrastructure/email_contact.py`:

```python
async def send_contact_email(
    email_client: FastMail,
    *,
    app_name: str,
    contact_email: str,
    submitter_name: str,
    submitter_email: EmailStr,
    subject: str,
    message: str,
    authenticated_user_id: int | None,
) -> None:
    msg = MessageSchema(
        subject=f"[{app_name}] Contact: {subject}",
        recipients=[NameEmail("Contact", contact_email)],
        reply_to=[NameEmail(submitter_name, submitter_email)],
        body=(
            f"<h2>New contact form submission</h2>"
            f"<p><b>From:</b> {escape(submitter_name)} "
            f"&lt;{escape(submitter_email)}&gt;</p>"
            f"<p><b>Authenticated user ID:</b> "
            f"{authenticated_user_id if authenticated_user_id is not None else '—'}</p>"
            f"<p><b>Subject:</b> {escape(subject)}</p>"
            f"<hr>"
            f"<pre>{escape(message)}</pre>"
        ),
        subtype=MessageType.html,
    )
    await email_client.send_message(msg)
```

The endpoint enqueues this via `BackgroundTasks.add_task(...)` (matching `email_auth.py`) so the HTTP response returns immediately at 204 regardless of SMTP latency.

### Configuration

Two new `NamedTuple`s in `infrastructure/config.py`, attached to `Config`:

```python
class ContactConfig(NamedTuple):
    email: str
    rate_limit_anon: int
    rate_limit_auth: int
    rate_limit_window: timedelta

    @classmethod
    def from_env(cls, ...) -> Self:
        # CONTACT_EMAIL                     (required)
        # CONTACT_RATE_LIMIT_ANON           (default "5")
        # CONTACT_RATE_LIMIT_AUTH           (default "10")
        # CONTACT_RATE_LIMIT_WINDOW_SECONDS (default "3600")
        ...

class CapConfig(NamedTuple):
    api_url: str
    site_key: str
    secret_key: str

    @classmethod
    def from_env(cls, ...) -> Self:
        # CAP_API_URL, CAP_SITE_KEY, CAP_SECRET_KEY  (all required)
        ...
```

`Config` gains `contact: ContactConfig` and `cap: CapConfig` fields. Both follow the existing `from_env` pattern with optional override args for tests.

### babycli check

`babycli/check.py` adds:

```python
async def check_cap() -> bool:
    try:
        config = CapConfig.from_env()
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Any HTTP response (200, 404, etc.) proves the server is up.
            # Only network errors / timeouts indicate unreachability.
            await client.get(f"{config.api_url}/", timeout=5.0)
        console_ok(f"Cap — reachable ({config.api_url})")
        return True
    except Exception as e:
        console_err(f"Cap — {e}")
        return False
```

Wired into `check_all()` and exposed as `babycli check cap`. Contact email config is covered by the existing `check email` (we extend `check_email_config` to also require `CONTACT_EMAIL`).

## Security considerations

1. **Header injection.** `Reply-To` and `recipients` come from a pydantic-validated `EmailStr`; CR/LF cannot enter. The recipient is from env (operator-controlled). `subject` is a plain string interpolated into `MessageSchema.subject`; `fastapi_mail` builds the MIME headers safely.
2. **HTML injection in support inbox.** Every user-supplied field rendered into the HTML body goes through `html.escape`. The body is `subtype=MessageType.html`; raw `<script>` payloads are escaped to entities.
3. **Spam / abuse.** Three layers — honeypot, rate limit, cap PoW — applied independently. Each layer alone is bypassable by a determined attacker; defense-in-depth makes the combined cost-to-attack much higher than a low-volume contact form is worth.
4. **Information disclosure on rejection.** Honeypot, cap rejection, and cap-unreachable all surface as the same `400 INVALID_SUBMISSION`, so the endpoint is not a probe oracle.
5. **Timing oracle on auth state.** The optional auth dep runs *after* honeypot and rate-limit gates; auth failure does not change response. Anonymous and authenticated paths converge on the same 204 response shape.
6. **Rate limit key choice.** Anonymous keying is by `request.client.host`. Behind a reverse proxy this must be the real client IP; the deployment must therefore set `forwarded_allow_ips` (uvicorn / `--proxy-headers`) so `request.client.host` reflects the original IP, not the proxy. Documented in the operator setup, not enforced in code.
7. **Cap fail-closed.** If the cap server is down, submissions are rejected. This trades availability for safety; the alternative (fail-open) would allow a trivial bypass by killing the cap server (DoS for spam-through). Operators rely on `babycli check cap` and 400-rate alerting.
8. **No persistence.** Contact submissions are not written to the database. PII (name + email + free-text message) only transits through the SMTP outbound queue and the support mailbox, reducing GDPR surface.
9. **Background SMTP send.** The 204 response returns before SMTP completes. Failed SMTP sends are logged by `fastapi_mail` but not retried. Acceptable for a contact form; not acceptable for transactional auth flows (those already use the same pattern, so this is consistent).

## Testing

New file `tests/utils/test_contact.py`. New fixtures in `tests/fixtures/contact.py`:

- `mock_cap_verify` (autouse, function scope): patches `verify_cap_token` to return `True`. Tests opt out via parametrize/override to test rejection.
- `tight_rate_limit` (function scope): overrides the endpoint's `RateLimiter` dep with one configured for a 60-second window and small limits, to make rate-limit tests fast and deterministic.

Test cases:

1. Anonymous valid submission → 204; assert email sent with `Reply-To` set to submitter and `authenticated_user_id` is `None` in body.
2. Authenticated valid submission (alice_client) → 204; assert email body contains `alice.id`.
3. Honeypot filled (`website="x"`) → 400 `INVALID_SUBMISSION`; no email sent.
4. Cap token rejected (override `verify_cap_token` → False) → 400 `INVALID_SUBMISSION`; no email sent.
5. Cap server unreachable (override `verify_cap_token` to raise httpx.RequestError) → 400 `INVALID_SUBMISSION`; no email sent.
6. Rate limit anon: under tight limit, sixth POST from same client → 429 `RATE_LIMITED`.
7. Rate limit auth: alice posts past auth limit → 429.
8. Rate limit isolation: alice (auth) + same-IP anon both submit at their respective limits — neither exhausts the other.
9. Pydantic validation: missing field, malformed email, message > 5000, name == "" all → 422.
10. HTML injection: message containing `<script>alert(1)</script>` → 204; assert email body contains `&lt;script&gt;` not raw `<script>`.
11. `CONTACT_EMAIL` env: assert outgoing message recipient matches `config.contact.email`.

Test infra notes:
- Email client is already mocked by the existing global SMTP fixture; assertions read from the captured outbox.
- Redis is real and flushed per test by existing infra; rate-limit tests rely on this.
- `tests/fixtures/contact.py` is registered via `tests/conftest.py::pytest_plugins`.

## Migration / operator setup

No database migration. Deployment requires:

- Setting `CONTACT_EMAIL` in the environment (production: `contact@babytroc.ch`).
- Running a `cap` server (external Docker container; not in this repo's compose file unless we add it).
- Setting `CAP_API_URL`, `CAP_SITE_KEY`, `CAP_SECRET_KEY`.
- Optionally overriding `CONTACT_RATE_LIMIT_ANON`, `CONTACT_RATE_LIMIT_AUTH`, `CONTACT_RATE_LIMIT_WINDOW_SECONDS`.
- Ensuring uvicorn is started with `--proxy-headers` (or equivalent) when behind a reverse proxy, so `request.client.host` is the real client IP for rate limiting.

Verification: `babycli check` should pass all subchecks, including the new `cap` check.

## GUI integration (informational, not in scope)

The frontend page `gui/app/pages/me/contact.vue` will:

- Render the cap widget (configured with `CAP_SITE_KEY` and `CAP_API_URL`).
- POST to `/api/v1/utils/contact` with `nom→name`, `sujet→subject`, `email`, `message`, `cap_token` from the widget, omitting `website`.
- Show the existing success state on `204`, surface a generic error on `400`/`429`, and field-level errors on `422`.

GUI changes are out of scope for this spec but listed so the contract is unambiguous.
