# Cap widget + honeypot retrofit — signup, item-create, password-reset

**Date:** 2026-05-12
**Status:** Approved (pending implementation)
**Scope:** GUI only. API already accepts `cap_token` + `website` honeypot on all three endpoints (`/v1/auth/new`, `/v1/me/items`, `/v1/auth/reset-password`) via the shared `AntiBotMixin`.

## Goal

Wire the cap PoW widget and honeypot into three pages that were updated server-side by the antibot+rate-limit rollout but are still sending body shapes the API now rejects:

- `/me/account/new` (signup, multi-step)
- `/me/items/new` (item creation, single-page)
- `/me/account/forgotten-password` (password-reset trigger, single input)

Each will:
1. Send a `cap_token` solved by the existing `<CapWidget>` component.
2. Carry a hidden `website` honeypot field (always empty for real users, blocks submit if filled).
3. Map API errors (400/422/429/5xx/network) to `$toast.error` with localised copy.

Password-reset is included because regenerating `gui/openapi/api/openapi.json` makes `cap_token` a typed-required field on `/v1/auth/reset-password`, so the existing GUI no longer type-checks without wiring it.

## Non-goals

- API changes — the server is already ready for all three endpoints.
- Wiring cap onto other endpoints that don't request it (`/v1/auth/login`, `/v1/auth/validate/*`, `/v1/auth/reset-password/{code}` for the second-step reset, image uploads).
- Generalising `mapErrorToToast` into a shared util — three local copies until a fourth caller appears (then extract).
- Building automated tests — repo has no Vue/Nuxt test harness.
- Updating `auth-login.ts:15`'s `@ts-expect-error: cannot type FormData` — unrelated.

## Architecture

### New files

| Path | Purpose |
| --- | --- |
| `gui/app/components/ui/Honeypot.vue` | Reusable hidden `<input name="website">` with built-in offscreen CSS, `v-model` binding |

### Modified files

| Path | Change |
| --- | --- |
| `gui/openapi/api/openapi.json` | Regenerate from running API (`curl http://localhost/api/openapi.json`). Adds typed `cap_token` + `website` to the three request schemas |
| `gui/app/composables/contact.ts` | Remove the `@ts-expect-error` line (path now typed) |
| `gui/app/composables/auth-account-create.ts` | Accept body type from openapi (`ApiRequestBody<"create_user_v1_auth_new_post">`) — page passes the full body including `cap_token`/`website` |
| `gui/app/mutations/item.ts` | Same — accept `ApiRequestBody<"create_client_item_v1_me_items__post">`; delete the `as never` workaround if any |
| `gui/app/composables/auth-password-reset.ts` | Accept an additional `capToken: MaybeRefOrGetter<string>` argument; include `cap_token` + `website` in the POST body |
| `gui/app/mutations/auth.ts` | Delete `useAskPasswordResetMutation` (dead code — zero importers) |
| `gui/app/pages/me/items/new.vue` | Add `<Honeypot>`, `<CapWidget>`, capToken/website refs, error mapping; pass cap_token into the create call |
| `gui/app/components/account/AccountCreationPasswordForm.vue` | Add `<Honeypot>` + `<CapWidget>` inside the password step; expose `capToken` and `website` as `v-model`s; expose `bumpResetSignal()` via `defineExpose` |
| `gui/app/pages/me/account/new.vue` | Capture `capToken`/`website` refs, pass into `createAccount`, map errors to toasts, bump cap on error |
| `gui/app/components/account/AccountAskPasswordResetPanel.vue` | Add `<Honeypot>` + `<CapWidget>`, pass `capToken` to `useAskPasswordReset`, error toast mapping |
| `gui/app/components/item/ItemEditionForm.vue` | Add a `submitDisabled?: boolean` prop the page can drive (cap not yet solved) |
| `gui/app/pages/me/contact.vue` | Swap the inline honeypot for `<Honeypot v-model="website" />` (consistency, no behaviour change) |

## Components

### `<Honeypot>`

```vue
<script setup lang="ts">
const value = defineModel<string>({ default: "" });
</script>

<template>
  <input
    v-model="value"
    type="text"
    name="website"
    tabindex="-1"
    autocomplete="off"
    aria-hidden="true"
    class="Honeypot"
  >
</template>

<style scoped lang="scss">
.Honeypot {
  position: absolute;
  left: -9999px;
  width: 1px;
  height: 1px;
  opacity: 0;
}
</style>
```

- Caller owns the `website` ref via `v-model`.
- Caller still gates submission via its own `valid` computed (`unref(website) === ""`). `<Honeypot>` does not implement validation — single responsibility (render the trap).

### `<CapWidget>` — unchanged

Already shipped in `gui/app/components/ui/CapWidget.vue`. Re-used as-is on all three pages.

## Composables

### `useCreateAccount`

```ts
type CreateAccountBody = ApiRequestBody<"create_user_v1_auth_new_post">;

export function useCreateAccount(options?: { onSuccess?: () => void }) {
	const { $api } = useNuxtApp();
	const { mutateAsync: createAccount, ...mutation } = useMutation({
		mutation: (ctx: CreateAccountBody) =>
			$api("/v1/auth/new", { method: "POST", body: ctx }),
		onSuccess: () => options?.onSuccess?.(),
	});
	return { createAccount, ...mutation };
}
```

### `useCreateItemMutation`

```ts
type CreateItemBody = ApiRequestBody<"create_client_item_v1_me_items__post">;

export const useCreateItemMutation = defineMutation(() => {
	const { $api } = useNuxtApp();
	const queryCache = useQueryCache();
	return useMutation({
		mutation: async (ctx: CreateItemBody) =>
			await $api("/v1/me/items", { method: "POST", body: ctx }),
		onSettled: () => invalidateItemLists(queryCache),
	});
});
```

### `useAskPasswordReset`

```ts
export function useAskPasswordReset(
	email: MaybeRefOrGetter<string>,
	capToken: MaybeRefOrGetter<string>,
) {
	// ...existing validation logic unchanged...

	const { mutateAsync: askPasswordReset, ...mutation } = useMutation({
		mutation: () =>
			$api("/v1/auth/reset-password", {
				method: "POST",
				body: {
					email: unref(cleanedEmail),
					cap_token: toValue(capToken),
					website: "",
				},
			}),
	});
	// ...rest unchanged...
}
```

### `mutations/auth.ts` cleanup

Delete `useAskPasswordResetMutation` (dead — only definition, no callers).

### `composables/contact.ts`

Remove the `@ts-expect-error: /v1/utils/contact not yet in gui/openapi/api/openapi.json (regenerate to remove this line)` line — openapi regen makes it redundant and the directive itself becomes a TS error if left.

## Page changes

### `/me/items/new` (`gui/app/pages/me/items/new.vue`)

Pull `cap` from runtime config. Add `capToken`, `website`, `capResetSignal` refs. Add a `mapErrorToToast` function (local copy). Gate `submit(data)` on cap solved + honeypot empty + cap configured. On error, clear `capToken` and bump reset signal.

Template adds `<Honeypot>`, `<CapWidget>` (or `<PanelBanner>` fallback) inside the existing `<Panel>`, after `<ItemEditionForm>`. `<ItemEditionForm>` gets a new `:submit-disabled="capToken === '' || !capConfigured"` prop that disables its internal submit button.

### `<ItemEditionForm>`

Add a `submitDisabled?: boolean` prop (default `false`). The form's internal submit button:

```vue
:disabled="!valid || isLoading || submitDisabled"
```

No other change.

### `/me/account/new` (`gui/app/pages/me/account/new.vue`)

Pass cap config + bind `capToken`/`website` v-models on the password step. Wrap the final `createAccount(...)` call in try/catch; on error, run `mapErrorToToast` and call the password form's exposed `bumpResetSignal()`.

```ts
const capToken = ref("");
const website = ref("");
const passwordFormRef = useTemplateRef("passwordFormRef");

async function next() {
	const _modeCounter = unref(modeCounter);
	if (unref(freeze)) return;
	if (_modeCounter === 2) {
		try {
			return await createAccount({
				name: unref(name),
				email: unref(email),
				password: unref(password),
				cap_token: unref(capToken),
				website: unref(website),
			});
		} catch (err) {
			mapErrorToToast(err as FetchError);
			capToken.value = "";
			passwordFormRef.value?.bumpResetSignal();
		}
		return;
	}
	modeCounter.value = _modeCounter + 1;
}
```

### `AccountCreationPasswordForm`

Adds props `apiUrl: string`, `siteKey: string`, models `capToken`, `website`, and an internal `resetSignal` ref exposed via `defineExpose({ bumpResetSignal })`. The submit button `:disabled` adds `capToken === ''`, `website !== ''`, and `!capConfigured`.

### `/me/account/forgotten-password` (`AccountAskPasswordResetPanel`)

Add cap config, refs, `mapErrorToToast`, capReset signal. `useAskPasswordReset(email, capToken)` becomes the new call signature. Template adds `<Honeypot>` + `<CapWidget>` between the email input and submit button. Submit button disabled if `capToken === ''` or `!capConfigured`. The status === "success" / status === "error" PanelBanners stay (composable behaviour preserved; we just add the cap gate + per-status toast for transient failures).

### `/me/contact` (`gui/app/pages/me/contact.vue`)

Swap the inline `<input ... class="honeypot">` for `<Honeypot v-model="website" />`. Delete the `.honeypot { ... }` block from the page's `<style scoped>`. No behaviour change.

## Error mapping (uniform)

```ts
function mapErrorToToast(err: FetchError | null): void {
	const code = err?.status;
	if (code === 400) $toast.error("Captcha invalide, veuillez réessayer.");
	else if (code === 422) $toast.error("Champs invalides.");
	else if (code === 429) $toast.error("Trop d'envois. Réessayez dans quelques minutes.");
	else if (typeof code === "number" && code >= 500) $toast.error("Erreur serveur. Réessayez plus tard.");
	else $toast.error("Problème de connexion. Vérifiez votre réseau.");
}
```

Three copies (one per page module) until a fourth caller emerges. At that point, extract to `gui/app/utils/contact-errors.ts` (or similar).

## Data flow per page

```
User fills inputs
  └── cap widget shown (final step on signup, always shown on item-create + pw-reset)
        └── user solves PoW → widget emits `solve` → page stores capToken
              └── submit button enables
                    └── click submit
                          └── composable POST → server verifies cap + honeypot
                                ├── 204/201 → success path
                                └── error → toast + capToken=""+ resetSignal++
```

## Risks & open questions

- **Three duplicate `mapErrorToToast`** — acceptable now; promote to util on next caller.
- **Password reset email-validity pre-check** still hits `/v1/auth/email/available` before cap — that endpoint isn't behind cap. Acceptable since it doesn't trigger an email send; it's a yes/no probe with its own rate limit at the email-availability layer.
- **Multi-step signup UX wart:** cap appears suddenly on the 3rd step. Acceptable per Q1 decision. A future redesign could pre-load cap on step 1 to let users solve in parallel with filling other fields — out of scope.
- **`bumpResetSignal` via `defineExpose`** is a slightly unusual pattern in this codebase. Alternative: lift the reset signal entirely to the parent and pass it down via prop. Chosen approach keeps the password form self-contained; parent only needs a ref to bump on error.

## Verification

`npx nuxi typecheck` — must exit 0 across the change set. (Today, with the regenerated openapi but no GUI changes, typecheck fails in 5 places — that's the work this spec covers.)

Manual happy paths (one per page, with running API + cap server):
- Anonymous signup → confirm cap challenge appears on password step; solve; submit; pending-validation page reached.
- Anonymous password-reset request → cap challenge in the panel; solve; submit; success banner.
- Authenticated item create → cap challenge below form; solve; submit; redirect to `/me/items`.

Manual error paths (each page):
- 429 toast (burst submissions).
- 400 toast (set `website` non-empty via Vue devtools → submit disabled; or break cap secret in API to force 400 on submit).
- Cap config missing → red `<PanelBanner>` instead of widget; submit disabled.

## Out of scope (follow-up specs)

1. Generalised contact-error toast util.
2. Pre-loading the cap challenge on signup step 1 to let users solve while typing.
3. Cap retrofit on the `/v1/auth/reset-password/{code}` second-step endpoint (server doesn't accept it today).
