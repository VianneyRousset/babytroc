# Contact page ↔ API + cap widget integration

**Date:** 2026-05-12
**Status:** Approved (pending implementation)
**Scope:** GUI only — no API changes

## Goal

Wire `gui/app/pages/me/contact.vue` to the existing `POST /v1/utils/contact` API endpoint, and add the cap (PoW captcha) widget so submissions satisfy the server-side `cap_token` requirement. Build the captcha as a reusable component so later retrofits onto account-create and password-reset forms are cheap.

## Non-goals

- API changes (the `/v1/utils/contact` endpoint already exists and the cap server is already wired in the API config).
- Retrofitting `<CapWidget>` onto `/me/account/new` or `/me/account/forgotten-password` (deferred — those API endpoints don't currently accept `cap_token` and need their own spec).
- i18n abstraction. Strings stay inline French.
- Cap widget custom theming.
- Admin/inbox UI for received contact submissions (backend forwards to email).
- New automated GUI test framework (none currently exists in the repo). Verification is manual + `nuxi typecheck`.

## API contract (existing)

```
POST /api/v1/utils/contact
Content-Type: application/json

{
  "name":     "string (1..100)",
  "email":    "EmailStr",
  "subject":  "string (1..200)",
  "message":  "string (1..5000)",
  "cap_token":"string (1..4096)",
  "website":  "string (honeypot — always empty from real users)"
}
```

Responses:
- `204 No Content` — accepted, email enqueued in background task
- `400 INVALID_SUBMISSION` — honeypot tripped OR cap token invalid
- `429` — rate limited (anon: IP-based; auth: user-based)
- `422` — Pydantic validation (length/email format)

Server enriches with `authenticated_user_id` when the session is logged-in (cookie-based, automatic via `$api`).

## Architecture

### New files

| Path | Purpose |
| --- | --- |
| `gui/app/components/ui/CapWidget.vue` | Reusable wrapper over the `cap-widget` custom element. Owns CDN script injection, event extraction, reset() control. |
| `gui/app/composables/contact.ts` | `useSendContactMessage()` — `useMutation`-backed POST to `/v1/utils/contact`. |
| `gui/types/cap-widget.d.ts` | Minimal ambient typing for the `cap-widget` custom element and its `solve` / `expire` `CustomEvent` payloads. |

### Modified files

| Path | Change |
| --- | --- |
| `gui/app/pages/me/contact.vue` | Replace local fake-success flow with real submit, pre-fill, cap widget, toast mapping. |
| `gui/nuxt.config.ts` | Extend `runtimeConfig.public` with `cap: { apiUrl, siteKey }`. |

### Environment variables (deploy-time)

| Variable | Maps to | Required |
| --- | --- | --- |
| `NUXT_PUBLIC_CAP_API_URL` | `runtimeConfig.public.cap.apiUrl` | Yes (in prod) |
| `NUXT_PUBLIC_CAP_SITE_KEY` | `runtimeConfig.public.cap.siteKey` | Yes (in prod) |

In dev/preview these may be blank; the page renders a red `PanelBanner` ("Captcha unavailable") and disables submit. This avoids a silent broken state.

## Components

### `<CapWidget>`

**Props**

| Name | Type | Notes |
| --- | --- | --- |
| `apiUrl` | `string` | Cap server base, e.g. `https://cap.example.com` (no trailing slash) |
| `siteKey` | `string` | Public site key |
| `disabled` | `boolean` (default `false`) | Visually inert; ignore `solve` events while true |
| `resetSignal` | `number \| string` (default `0`) | Watched — any change triggers `widget.reset()` to force re-solve |

**Emits**

| Event | Payload | When |
| --- | --- | --- |
| `solve` | `string` (token) | Cap fires `solve`, payload is `e.detail.token` |
| `expire` | `void` | Cap fires `expire`; parent should clear its stored token |

**Behavior**

- On setup: `useHead({ script: [{ src: "https://cdn.jsdelivr.net/npm/cap-widget", tagPosition: "bodyClose" }] })`. Nuxt deduplicates by `src` across page navigations.
- Template: `<cap-widget :data-cap-api-endpoint="\`${apiUrl}/${siteKey}/\`" ref="el" />`.
- `onMounted`: attach `solve` and `expire` `addEventListener` on the ref. Emit corresponding Vue events.
- `onBeforeUnmount`: detach listeners.
- `watch(resetSignal, () => el.value?.reset?.())` — defensive optional chain in case widget isn't ready.

**Why a wrapper** — keeps script lifecycle, event-detail extraction, and reset mechanics in one place; consumers see standard Vue props/emits.

### `useSendContactMessage()`

```ts
export function useSendContactMessage(): {
  sendContactMessage: (ctx: ContactSubmit) => Promise<void>;
  isLoading: Ref<boolean>;
  status: Ref<"idle" | "pending" | "success" | "error">;
  error: Ref<FetchError | null>;
};

export type ContactSubmit = {
  name: string;
  email: string;
  subject: string;
  message: string;
  capToken: string;
};
```

Internals:
- Wraps `useMutation` (matches `useLogin`, `useCreateAccount`).
- `$api("/v1/utils/contact", { method: "POST", body: { ...fields, cap_token: capToken, website: "" } })`.
- No retry (cap tokens are single-use; retry would always 400).
- No `onSuccess`/`onError` side effects in the composable — page handles UX.

### `me/contact.vue` rewrite

**Script setup**

- `const { loggedIn } = useAuth()` — `Ref<boolean | undefined>`; `undefined` means the auth query is still pending. Treat `undefined` as "not yet known" — render the form in its anonymous-editable state but don't pre-fill until `loggedIn === true`.
- `const { me } = useMe()` — `Ref<UserPrivate | undefined>` exposing `name` and `email` (both required strings on `UserPrivateRead`).
- Local refs (template-bound, kept in French to match existing page): `nom`, `email`, `sujet`, `message`, `capToken`, `website` (honeypot), `capResetSignal`, `dismissedSuccess`.
- `watch(me, …)` once `loggedIn === true`: if `nom`/`email` are still empty, seed them from `me.value.name` / `me.value.email`. Re-evaluating when `me` first resolves handles the case where the page mounts before the `me` query settles.
- When `loggedIn === true`, the name and email inputs render with `readonly` + an `is-locked` class. Internally the composable still POSTs whatever is in `nom`/`email` (the page values), so the backend receives the pre-filled values — `authenticated_user_id` is attached server-side from the cookie and is the trust anchor.
- `valid`:
  - all of `nom`, `email`, `sujet`, `message` non-empty after trim
  - `email` matches `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`
  - `message.length <= 5000`
  - `capToken !== ""`
- `submit()`:
  1. Bail if `!valid`.
  2. Call `sendContactMessage({ name: unref(nom), email: unref(email), subject: unref(sujet), message: unref(message), capToken: unref(capToken) })` — composable consumes English field names, page refs stay French to match the rest of the page's locale.
  3. On resolve: clear `sujet` and `message` (keep `nom`/`email` so a logged-in user doesn't see their pre-filled identity vanish), increment `capResetSignal`, leave `status === "success"` (drives inline block via `transition`). For anonymous users, clearing `nom`/`email` is also OK — pick "always clear sujet+message, never clear name+email" for both cases for consistency.
  4. On reject: map `error.value` to a toast (see Error Mapping); increment `capResetSignal` (token already consumed server-side).

**Template**

- Same outer `AppPage` + intro/divider structure.
- Inputs: when `loggedIn === true`, name & email have `readonly` + a `is-locked` class (subtle background tint). When `loggedIn === undefined` (pending) or `false`, both are normal editable inputs.
- Hidden honeypot:
  ```html
  <input
    v-model="website"
    name="website"
    type="text"
    tabindex="-1"
    autocomplete="off"
    aria-hidden="true"
    class="honeypot"
  />
  ```
  CSS: `position: absolute; left: -9999px; width: 1px; height: 1px; opacity: 0;`
- Message counter: `<small>{{ message.length }} / 5000</small>` under the textarea, red colour when `message.length > 5000`.
- Cap widget block (between message and submit):
  ```html
  <CapWidget
    v-if="capApiUrl && capSiteKey"
    :api-url="capApiUrl"
    :site-key="capSiteKey"
    :reset-signal="capResetSignal"
    :disabled="isLoading"
    @solve="capToken = $event"
    @expire="capToken = ''"
  />
  <PanelBanner v-else color="red" :icon="OctagonAlert">
    Captcha indisponible. Le formulaire est désactivé.
  </PanelBanner>
  ```
- Submit button: `:disabled="!valid || isLoading"`, `:loading="isLoading"`.
- Success block (existing animation): on `status === 'success' && !dismissedSuccess`. "Envoyer un autre message" sets `dismissedSuccess = true` so the form returns; submitting again resets `dismissedSuccess`.

**Removed** — the local `sent` ref and its fake-success branch.

### Runtime config (`nuxt.config.ts`)

```ts
runtimeConfig: {
  public: {
    openFetch: { api: { baseURL: "/api" } },
    cap: {
      apiUrl: "",
      siteKey: "",
    },
  },
},
```

Page reads via `useRuntimeConfig().public.cap`.

## Error mapping (page-level)

| Outcome | UX |
| --- | --- |
| `204` | Inline success block (existing transition + copy) |
| `400 INVALID_SUBMISSION` | `toast.error("Captcha invalide, veuillez réessayer.")` + reset widget |
| `429` | `toast.error("Trop d'envois. Réessayez dans quelques minutes.")` |
| `422` | `toast.error("Champs invalides.")` (shouldn't happen with client validation, but fail-safe) |
| `5xx` | `toast.error("Erreur serveur. Réessayez plus tard.")` |
| Network/abort | `toast.error("Problème de connexion. Vérifiez votre réseau.")` |
| Cap token missing at click | No request; button disabled — no toast |
| Cap `expire` event | Clear `capToken`; button auto-disables — no toast |

Mapping logic lives in the page (`switch` on `error.value?.status`), not in the composable — composable stays generic and reusable.

## Data flow

```
User fills form
  └── cap widget shown
        └── user solves PoW challenge
              └── widget emits `solve` → page stores capToken
                    └── submit button enabled
                          └── click submit
                                └── useSendContactMessage → POST /v1/utils/contact
                                      ├── 204 → inline success block + clear fields + reset cap
                                      └── error → toast + reset cap
```

## Validation rules (client)

| Field | Rule | Source |
| --- | --- | --- |
| `nom` | non-empty after trim | API: 1..100 |
| `email` | non-empty + `/^[^\s@]+@[^\s@]+\.[^\s@]+$/` | API: `EmailStr` |
| `sujet` | non-empty after trim | API: 1..200 |
| `message` | non-empty after trim, ≤ 5000 chars (counter visible) | API: 1..5000 |
| `cap_token` | non-empty (set by widget `solve` event) | API: 1..4096 |
| `website` | hidden, must remain `""` | API: honeypot |

The client deliberately doesn't enforce upper-bound lengths on `nom` / `sujet` — the counter is on `message` only (the field a user can realistically hit the cap on). Over-length submissions fall through to the 422 path.

## Testing & verification

No GUI test framework currently in the repo, so no automated tests are added in this scope.

- **Type-check:** `nuxi typecheck` (already enabled via `typescript.typeCheck: true` in `nuxt.config.ts`) must pass.
- **Manual happy path (anonymous):** dev server up, fill form, solve cap, submit → inline success block + email arrives at `CONTACT_EMAIL`.
- **Manual happy path (logged in):** same as above with a session; verify name/email render `readonly`, request body contains the logged-in user's name+email, server logs show `authenticated_user_id` set.
- **Manual honeypot:** in devtools, set `value` on the hidden `website` input, submit → 400 + captcha-invalid toast (server-side error message is shared between honeypot and cap failures).
- **Manual cap failure:** in devtools, set `capToken.value = ""` after solving → submit button disables; clear server's secret to force a 400 from a real submit → toast + widget reset.
- **Manual rate-limit:** burst submit until 429 → rate-limit toast.
- **Manual config gap:** unset `NUXT_PUBLIC_CAP_API_URL` → page shows red "Captcha indisponible" banner, submit disabled.

## Risks & open questions

- **CDN dependency:** the cap widget is loaded from `cdn.jsdelivr.net`. If the CDN is unavailable, the widget element never renders interactive UI. Acceptable for now (matches the upstream guide); if it becomes a problem, vendor `cap-widget` from npm and serve it from the Nuxt build.
- **CSP:** if/when a Content-Security-Policy header is added, `script-src` must allow `cdn.jsdelivr.net` and `frame-src`/`connect-src` must allow the cap server origin.
- **Custom element warning in Vue:** `<cap-widget>` needs to be marked as a custom element. Nuxt/Vite already passes unknown lowercase-hyphenated tags through, but if Vue logs a warning, add it to `vue.compilerOptions.isCustomElement` in `nuxt.config.ts`.

## Out of scope (follow-up specs)

1. Retrofit `<CapWidget>` onto account-creation and password-reset forms. Requires API changes (accept + verify `cap_token`, add rate limits) and tests.
2. i18n / locale infrastructure.
3. Self-hosted cap widget bundle (vendoring instead of CDN).
