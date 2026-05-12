# Cap retrofit (signup + item-create + pw-reset) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire the existing `<CapWidget>` + a new `<Honeypot>` component into the three pages the antibot API rollout broke (`/me/account/new`, `/me/items/new`, `/me/account/forgotten-password`), regenerate `gui/openapi/api/openapi.json`, and harmonise error UX with the contact page.

**Architecture:** Build one new shared `<Honeypot>` component. Regenerate the OpenAPI schema so all three endpoint paths get typed `cap_token` + `website` fields. Update three composables to consume the wider body types. Pages own `capToken`/`website` refs and gate submit until cap is solved + honeypot empty. Same `mapErrorToToast` function (per-page copy, no premature extraction) handles 400/422/429/5xx/network toasts.

**Tech Stack:** Nuxt 3, Vue 3 `<script setup>`, `@pinia/colada` (useMutation), `nuxt-open-fetch` (`$api`), `vue3-toastify` (`$toast`), SCSS. No new npm dependencies.

**Spec:** `docs/superpowers/specs/2026-05-12-cap-retrofit-design.md`

**Working directory for all paths:** `/home/vianney/documents/projects/babytroc` (repo root).

**Package manager:** npm.

---

## File map

| File | Action |
| --- | --- |
| `gui/openapi/api/openapi.json` | Replace with the regenerated spec (already curled from `http://localhost/api/openapi.json` during brainstorming; currently unstaged) |
| `gui/app/components/ui/Honeypot.vue` | Create |
| `gui/app/composables/contact.ts` | Drop the `@ts-expect-error` line (now redundant after openapi regen) |
| `gui/app/mutations/auth.ts` | Delete the dead `useAskPasswordResetMutation` export |
| `gui/app/types/item.ts` | Add `ItemFormData` type (`Omit<ItemCreate, 'cap_token' \| 'website'>`) |
| `gui/app/components/item/ItemEditionForm.vue` | Emit `ItemFormData` instead of `ItemCreate`; accept `submitDisabled?: boolean` prop |
| `gui/app/pages/me/items/new.vue` | Add cap+honeypot refs, error mapping, build full body in submit handler |
| `gui/app/composables/auth-account-create.ts` | Accept `UserCreate` (now includes `cap_token` + `website`) — page already builds the full body |
| `gui/app/components/account/AccountCreationPasswordForm.vue` | Add `<Honeypot>` + `<CapWidget>` inside the panel; expose `capToken`/`website` v-models + `bumpResetSignal()` |
| `gui/app/pages/me/account/new.vue` | Pass cap props + capToken/website models to the password form; wrap `createAccount(...)` in try/catch with toast mapping |
| `gui/app/composables/auth-password-reset.ts` | Accept `capToken: MaybeRefOrGetter<string>` arg; include `cap_token` + `website` in body |
| `gui/app/components/account/AccountAskPasswordResetPanel.vue` | Add `<Honeypot>` + `<CapWidget>`; pass capToken into composable; toast errors |
| `gui/app/pages/me/contact.vue` | Swap inline honeypot for `<Honeypot v-model="website" />`; delete the `.honeypot` CSS rule (now in `<Honeypot>`) |

---

## Task 1: Regenerate openapi, drop dead code, drop `@ts-expect-error`

**Files:**
- Modify: `gui/openapi/api/openapi.json` (already modified in working tree, currently unstaged)
- Modify: `gui/app/composables/contact.ts`
- Modify: `gui/app/mutations/auth.ts`

This task lands an intentionally-incomplete state — after it, `npx nuxi typecheck` will still fail in 3 places (item form, password-reset composable, account-new page). Those failures are the work of tasks 3, 4, 5. Keep going.

- [ ] **Step 1.1: Verify the regenerated openapi is in the working tree**

```bash
git diff --stat gui/openapi/api/openapi.json
```

Expected: shows the file as modified (it was regenerated during brainstorming). If it's NOT modified, regenerate now:

```bash
curl -s http://localhost/api/openapi.json | python3 -m json.tool > gui/openapi/api/openapi.json
```

- [ ] **Step 1.2: Regenerate Nuxt types from the new schema**

```bash
cd gui && npx nuxi prepare 2>&1 | tail -5
```

Expected: `◆  Types generated in .nuxt.`

- [ ] **Step 1.3: Drop the `@ts-expect-error` directive in `composables/contact.ts`**

Read `gui/app/composables/contact.ts`. Find this exact 2-line block:

```ts
		mutation: (ctx: ContactSubmit) => {
			// @ts-expect-error: /v1/utils/contact not yet in gui/openapi/api/openapi.json (regenerate to remove this line)
			return $api("/v1/utils/contact", {
```

Replace with:

```ts
		mutation: (ctx: ContactSubmit) => {
			return $api("/v1/utils/contact", {
```

(Delete only the `@ts-expect-error` comment line.)

- [ ] **Step 1.4: Delete the dead `useAskPasswordResetMutation` from `mutations/auth.ts`**

Open `gui/app/mutations/auth.ts`. Find this exact block (lines 13-23):

```ts
export const useAskPasswordResetMutation = defineMutation(() => {
	const { $api } = useNuxtApp();
	return useMutation({
		mutation: (context: { email: string }) => {
			return $api("/v1/auth/reset-password", {
				method: "POST",
				body: context,
			});
		},
	});
});
```

Delete the entire block (including any blank line trailing). Verify no other file references this symbol:

```bash
grep -rn "useAskPasswordResetMutation" gui/app/
```

Expected: zero matches (it was the definition only).

- [ ] **Step 1.5: Typecheck — expect 3 remaining errors**

```bash
cd gui && npx nuxi typecheck 2>&1 | tail -25
```

Expected output (file paths in this exact set; the messages are the cap-related missing-field errors):
- `app/components/item/ItemEditionForm.vue` — `Argument of type '{ name: ...; ... }' is missing the following properties: cap_token, website` — fixed in Task 3.
- `app/composables/auth-password-reset.ts` — `Type '{ email: string; }' is missing the following properties: cap_token, website` — fixed in Task 5.
- `app/pages/me/account/new.vue` — `Argument of type '{ name: ...; email: ...; password: ... }' is missing the following properties: cap_token, website` — fixed in Task 4.

If any other error appears, stop and re-read the failing file before continuing.

- [ ] **Step 1.6: Commit**

```bash
git add gui/openapi/api/openapi.json gui/app/composables/contact.ts gui/app/mutations/auth.ts
git commit -m "chore(gui): regen openapi, drop dead pw-reset mutation, drop contact @ts-expect-error"
```

---

## Task 2: `<Honeypot>` component + retrofit `/me/contact`

**Files:**
- Create: `gui/app/components/ui/Honeypot.vue`
- Modify: `gui/app/pages/me/contact.vue`

- [ ] **Step 2.1: Create `gui/app/components/ui/Honeypot.vue`**

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

- [ ] **Step 2.2: Replace inline honeypot in `gui/app/pages/me/contact.vue`**

In `gui/app/pages/me/contact.vue`, find this block in `<template>`:

```html
            <input
              v-model="website"
              type="text"
              name="website"
              tabindex="-1"
              autocomplete="off"
              aria-hidden="true"
              class="honeypot"
            >
```

Replace with:

```html
            <Honeypot v-model="website" />
```

Then find this block in `<style scoped lang="scss">` (inside `.form { ... }`):

```scss
  .honeypot {
    position: absolute;
    left: -9999px;
    width: 1px;
    height: 1px;
    opacity: 0;
  }
```

Delete it entirely.

- [ ] **Step 2.3: Typecheck**

```bash
cd gui && npx nuxi typecheck 2>&1 | tail -25
```

Expected: same 3 errors as Task 1 (item form, pw-reset composable, account-new). No new errors. No errors in `contact.vue` or `Honeypot.vue`.

- [ ] **Step 2.4: Commit**

```bash
git add gui/app/components/ui/Honeypot.vue gui/app/pages/me/contact.vue
git commit -m "feat(gui): extract <Honeypot> component, retrofit on /me/contact"
```

---

## Task 3: Item create flow — form type, form prop, page wiring

**Files:**
- Modify: `gui/app/types/item.ts`
- Modify: `gui/app/components/item/ItemEditionForm.vue`
- Modify: `gui/app/pages/me/items/new.vue`

This task ends typecheck-clean for these files (the remaining errors from Task 1 in account-new + password-reset composable still stand; they're fixed in Tasks 4 and 5).

- [ ] **Step 3.1: Add `ItemFormData` to `gui/app/types/item.ts`**

Open `gui/app/types/item.ts`. After the `ItemCreate` export, add a new export:

```ts
export type ItemFormData = Omit<ItemCreate, "cap_token" | "website">;
```

The full file (after edit) should have `ItemFormData` declared as a sibling of `ItemUpdate`.

- [ ] **Step 3.2: Update `ItemEditionForm.vue` — emit `ItemFormData`, accept `submitDisabled`**

In `gui/app/components/item/ItemEditionForm.vue`:

Find:

```ts
const emit = defineEmits<(event: "submit", data: ItemCreate) => void>();

const props = withDefaults(
	defineProps<{
		item?: ItemData;
		isLoading?: boolean;
	}>(),
	{
		isLoading: false,
	},
);
```

Replace with:

```ts
const emit = defineEmits<(event: "submit", data: ItemFormData) => void>();

const props = withDefaults(
	defineProps<{
		item?: ItemData;
		isLoading?: boolean;
		submitDisabled?: boolean;
	}>(),
	{
		isLoading: false,
		submitDisabled: false,
	},
);
```

Then find the submit button in the template (around line 198):

```html
    <TextButton
      aspect="flat"
      color="primary"
      :disabled="!valid"
      :loading="props.isLoading"
      @click="onclick"
    >
      Enregistrer
    </TextButton>
```

Replace `:disabled="!valid"` with `:disabled="!valid || props.submitDisabled"`:

```html
    <TextButton
      aspect="flat"
      color="primary"
      :disabled="!valid || props.submitDisabled"
      :loading="props.isLoading"
      @click="onclick"
    >
      Enregistrer
    </TextButton>
```

- [ ] **Step 3.3: Rewrite `gui/app/pages/me/items/new.vue`**

Replace the entire file contents with:

```vue
<script setup lang="ts">
import { OctagonAlert, X } from "lucide-vue-next";
import type { FetchError } from "ofetch";

definePageMeta({
	layout: "empty",
	appBack: true,
});

const { $toast } = useNuxtApp();
const { cap } = useRuntimeConfig().public;

const capToken = ref("");
const website = ref("");
const capResetSignal = ref(0);

const { mutateAsync: create, isLoading } = useCreateItemMutation();

const capConfigured = computed<boolean>(
	() => cap.apiUrl !== "" && cap.siteKey !== "",
);

function mapErrorToToast(err: FetchError | null): void {
	const code = err?.status;
	if (code === 400) {
		$toast.error("Captcha invalide, veuillez réessayer.");
	} else if (code === 422) {
		$toast.error("Champs invalides.");
	} else if (code === 429) {
		$toast.error("Trop d'envois. Réessayez dans quelques minutes.");
	} else if (typeof code === "number" && code >= 500) {
		$toast.error("Erreur serveur. Réessayez plus tard.");
	} else {
		$toast.error("Problème de connexion. Vérifiez votre réseau.");
	}
}

async function submit(data: ItemFormData) {
	if (
		unref(capToken) === "" ||
		unref(website) !== "" ||
		!unref(capConfigured)
	) {
		return;
	}
	try {
		await create({
			...data,
			cap_token: unref(capToken),
			website: "",
		});
		await navigateTo("/me/items");
	} catch (err) {
		mapErrorToToast(err as FetchError);
		capToken.value = "";
		capResetSignal.value += 1;
	}
}
</script>

<template>
  <AppPage
    logged-in-only
    with-header
  >
    <!-- Header bar (mobile only) -->
    <template #mobile-header-bar>
      <AppBack
        :icon="X"
      />
      <h1>Nouvel objet</h1>
    </template>

    <!-- Desktop page -->
    <template #desktop>
      <AppHeaderDesktop>
        <template #buttons-left>
          <AppBack />
        </template>
      </AppHeaderDesktop>
    </template>

    <main>
      <Panel :max-width="600">
        <ItemEditionForm
          :is-loading="isLoading"
          :submit-disabled="capToken === '' || !capConfigured"
          @submit="submit"
        />

        <Honeypot v-model="website" />

        <CapWidget
          v-if="capConfigured"
          :api-url="cap.apiUrl"
          :site-key="cap.siteKey"
          :reset-signal="capResetSignal"
          :disabled="isLoading"
          @solve="capToken = $event"
          @expire="capToken = ''"
        />
        <PanelBanner
          v-else
          color="red"
          :icon="OctagonAlert"
        >
          Captcha indisponible. Création désactivée.
        </PanelBanner>
      </Panel>
    </main>
  </AppPage>
</template>

<style scoped lang="scss">
</style>
```

- [ ] **Step 3.4: Verify `useCreateItemMutation` still type-checks**

`useCreateItemMutation` in `gui/app/mutations/item.ts` already takes `ItemCreate` (which now equals `ApiRequestBody<"create_client_item_v1_me_items_post">` and includes `cap_token`/`website`). No change needed there. Verify by typechecking next.

- [ ] **Step 3.5: Typecheck**

```bash
cd gui && npx nuxi typecheck 2>&1 | tail -25
```

Expected: 2 remaining errors only (account-new and password-reset composable). No errors in `item.ts`, `ItemEditionForm.vue`, or `me/items/new.vue`.

- [ ] **Step 3.6: Commit**

```bash
git add gui/app/types/item.ts gui/app/components/item/ItemEditionForm.vue gui/app/pages/me/items/new.vue
git commit -m "feat(gui): wire cap+honeypot on /me/items/new"
```

---

## Task 4: Signup flow — password form + page rewrite

**Files:**
- Modify: `gui/app/components/account/AccountCreationPasswordForm.vue`
- Modify: `gui/app/pages/me/account/new.vue`

`useCreateAccount` already accepts `UserCreate` which now includes `cap_token` + `website` (post-regen). No composable change needed.

- [ ] **Step 4.1: Rewrite `AccountCreationPasswordForm.vue`**

Replace the entire file contents with:

```vue
<script setup lang="ts">
import { OctagonAlert } from "lucide-vue-next";

const props = defineProps<{
	loading?: boolean;
	disabled?: boolean;
	apiUrl: string;
	siteKey: string;
}>();

const { loading, disabled, apiUrl, siteKey } = toRefs(props);

const password = defineModel<string>("password", { default: "" });
const valid = defineModel<boolean>("valid");
const capToken = defineModel<string>("capToken", { default: "" });
const website = defineModel<string>("website", { default: "" });

const emit = defineEmits(["next"]);

const capConfigured = computed<boolean>(
	() => unref(apiUrl) !== "" && unref(siteKey) !== "",
);

const canSubmit = computed<boolean>(
	() =>
		unref(valid) === true &&
		unref(capToken) !== "" &&
		unref(website) === "" &&
		unref(capConfigured),
);

const resetSignal = ref(0);

function bumpResetSignal() {
	resetSignal.value += 1;
	capToken.value = "";
}

defineExpose({ bumpResetSignal });

const next = () => unref(canSubmit) && emit("next");
</script>

<template>
  <section class="AccountCreationPasswordForm">
    <AccountPasswordInput
      v-model:password="password"
      v-model:valid="valid"
      msg-placement="top"
      :tabindex="0"
      :disabled="loading || disabled"
      autofocus
      @next="next"
    />

    <Honeypot v-model="website" />

    <CapWidget
      v-if="capConfigured"
      :api-url="apiUrl"
      :site-key="siteKey"
      :reset-signal="resetSignal"
      :disabled="loading"
      @solve="capToken = $event"
      @expire="capToken = ''"
    />
    <PanelBanner
      v-else
      color="red"
      :icon="OctagonAlert"
    >
      Captcha indisponible.
    </PanelBanner>

    <TextButton
      aspect="flat"
      size="large"
      color="primary"
      :loading="loading"
      :disabled="!canSubmit || loading || disabled"
      @click="next"
    >
      Créer un compte
    </TextButton>
  </section>
</template>

<style scoped lang="scss">
.AccountCreationPasswordForm {
  @include flex-column;
  align-items: stretch;
  gap: 1em;
}
</style>
```

- [ ] **Step 4.2: Update `gui/app/pages/me/account/new.vue` — script**

Read the file first. Find the existing `<script setup lang="ts">` block. Apply these specific edits:

(a) Below the existing imports, add:

```ts
import type { FetchError } from "ofetch";
```

(b) After the existing refs (`const name = ref("")`, etc., currently ending with `password`), add three new refs:

```ts
const capToken = ref("");
const website = ref("");
const passwordFormRef = useTemplateRef("passwordFormRef");
```

(c) After the existing `const { $toast } = useNuxtApp();` line — IF it exists in the file; otherwise add it as a new line near the top of the setup:

```ts
const { $toast } = useNuxtApp();
const { cap } = useRuntimeConfig().public;
```

If `useNuxtApp()` is not yet imported/used, add the full `const { $toast } = useNuxtApp();` line just below the imports.

(d) Add a `mapErrorToToast` function above the `next()` function:

```ts
function mapErrorToToast(err: FetchError | null): void {
	const code = err?.status;
	if (code === 400) {
		$toast.error("Captcha invalide, veuillez réessayer.");
	} else if (code === 422) {
		$toast.error("Champs invalides.");
	} else if (code === 429) {
		$toast.error("Trop d'envois. Réessayez dans quelques minutes.");
	} else if (typeof code === "number" && code >= 500) {
		$toast.error("Erreur serveur. Réessayez plus tard.");
	} else {
		$toast.error("Problème de connexion. Vérifiez votre réseau.");
	}
}
```

(e) Find the existing `next()` function. It currently looks like:

```ts
async function next() {
	const _modeCounter = unref(modeCounter);

	if (unref(freeze)) return;

	if (_modeCounter === 2)
		return await createAccount({
			name: unref(name),
			email: unref(email),
			password: unref(password),
		});

	modeCounter.value = _modeCounter + 1;
}
```

Replace with:

```ts
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
			passwordFormRef.value?.bumpResetSignal();
			return;
		}
	}

	modeCounter.value = _modeCounter + 1;
}
```

- [ ] **Step 4.3: Update `gui/app/pages/me/account/new.vue` — template**

In the same file, find the existing `<AccountCreationPasswordForm>` component usage. It currently looks something like:

```html
        <Panel v-else-if="mode === 'password'">
          <PanelBanner :icon="KeyRound">
            <h2>Choisissez un mot de passe</h2>
          </PanelBanner>
          <AccountCreationPasswordForm
            v-model:password="password"
            ...
            @next="next"
          />
        </Panel>
```

Update the `<AccountCreationPasswordForm>` open tag to bind cap + ref:

```html
          <AccountCreationPasswordForm
            ref="passwordFormRef"
            v-model:password="password"
            v-model:cap-token="capToken"
            v-model:website="website"
            :loading="isLoading"
            :disabled="freeze"
            :api-url="cap.apiUrl"
            :site-key="cap.siteKey"
            @next="next"
          />
```

(Adapt to whatever existing v-models / props are there — preserve them; add the four new bindings: `ref="passwordFormRef"`, `v-model:cap-token`, `v-model:website`, `:api-url`, `:site-key`. Keep existing `v-model:password`, `:loading`, `:disabled`, `@next`.)

- [ ] **Step 4.4: Typecheck**

```bash
cd gui && npx nuxi typecheck 2>&1 | tail -25
```

Expected: 1 remaining error only — `auth-password-reset.ts` (fixed in Task 5). No errors in `me/account/new.vue` or `AccountCreationPasswordForm.vue`.

- [ ] **Step 4.5: Commit**

```bash
git add gui/app/components/account/AccountCreationPasswordForm.vue gui/app/pages/me/account/new.vue
git commit -m "feat(gui): wire cap+honeypot on /me/account/new password step"
```

---

## Task 5: Password reset flow — composable + panel

**Files:**
- Modify: `gui/app/composables/auth-password-reset.ts`
- Modify: `gui/app/components/account/AccountAskPasswordResetPanel.vue`

- [ ] **Step 5.1: Update `useAskPasswordReset` signature in `auth-password-reset.ts`**

Open `gui/app/composables/auth-password-reset.ts`. Find:

```ts
export function useAskPasswordReset(email: MaybeRefOrGetter<string>) {
	const { $api } = useNuxtApp();
	const { value: touched } = useThrottle(useTouched(email), 1000);

	// email trimmed and without consecutive whitespaces
	const cleanedEmail = computed(() =>
		avoidConsecutiveWhitespaces(toValue(email).trim()),
	);

	// ask password reset mutation
	const { mutateAsync: askPasswordReset, ...mutation } = useMutation({
		mutation: () => {
			return $api("/v1/auth/reset-password", {
				method: "POST",
				body: {
					email: unref(cleanedEmail),
				},
			});
		},
	});
```

Replace the function signature and the mutation body so the body includes `cap_token` + `website`:

```ts
export function useAskPasswordReset(
	email: MaybeRefOrGetter<string>,
	capToken: MaybeRefOrGetter<string>,
) {
	const { $api } = useNuxtApp();
	const { value: touched } = useThrottle(useTouched(email), 1000);

	// email trimmed and without consecutive whitespaces
	const cleanedEmail = computed(() =>
		avoidConsecutiveWhitespaces(toValue(email).trim()),
	);

	// ask password reset mutation
	const { mutateAsync: askPasswordReset, ...mutation } = useMutation({
		mutation: () => {
			return $api("/v1/auth/reset-password", {
				method: "POST",
				body: {
					email: unref(cleanedEmail),
					cap_token: toValue(capToken),
					website: "",
				},
			});
		},
	});
```

Leave the rest of the function (the `useAccountEmailAvailable` block, `validationError`, `validationStatus`, return statement) unchanged.

- [ ] **Step 5.2: Rewrite `AccountAskPasswordResetPanel.vue`**

Replace the entire file contents with:

```vue
<script setup lang="ts">
import { Check, KeyRound, OctagonAlert } from "lucide-vue-next";
import type { FetchError } from "ofetch";

const emit = defineEmits(["done"]);

const { $toast } = useNuxtApp();
const { cap } = useRuntimeConfig().public;

const email = ref("");
const capToken = ref("");
const website = ref("");
const capResetSignal = ref(0);

const capConfigured = computed<boolean>(
	() => cap.apiUrl !== "" && cap.siteKey !== "",
);

const {
	askPasswordReset,
	isLoading,
	status,
	validationStatus,
	validationError,
} = useAskPasswordReset(email, capToken);

function mapErrorToToast(err: FetchError | null): void {
	const code = err?.status;
	if (code === 400) {
		$toast.error("Captcha invalide, veuillez réessayer.");
	} else if (code === 422) {
		$toast.error("Champs invalides.");
	} else if (code === 429) {
		$toast.error("Trop d'envois. Réessayez dans quelques minutes.");
	} else if (typeof code === "number" && code >= 500) {
		$toast.error("Erreur serveur. Réessayez plus tard.");
	} else {
		$toast.error("Problème de connexion. Vérifiez votre réseau.");
	}
}

const canSubmit = computed<boolean>(
	() =>
		unref(validationStatus) === "success" &&
		unref(capToken) !== "" &&
		unref(website) === "" &&
		unref(capConfigured),
);

async function go() {
	if (!unref(canSubmit)) return;

	try {
		await askPasswordReset();
		emit("done");
	} catch (err) {
		mapErrorToToast(err as FetchError);
		capToken.value = "";
		capResetSignal.value += 1;
	}
}
</script>

<template>
  <Panel class="AccountAskPasswordReset">
    <!-- Banner -->
    <transition
      name="pop"
      mode="out-in"
      appear
    >
      <!-- Success -->
      <PanelBanner
        v-if="status === 'success'"
        color="primary"
        :icon="Check"
      >
        Demande envoyée. Un email vous a été envoyé.
      </PanelBanner>

      <!-- Error -->
      <PanelBanner
        v-else-if="status === 'error'"
        color="red"
        :icon="OctagonAlert"
      >
        Une erreur est survenue
      </PanelBanner>

      <!-- Idle (logged out) -->
      <PanelBanner
        v-else
        :icon="KeyRound"
      />
    </transition>

    <!-- Form -->
    <h2>Vous avez oublié votre mot de passe?</h2>
    <p>Pas de soucis, on ne vous en veut pas. Entrez ici votre adresse email et nous vous enverrons un courriel pour le réinitialiser.</p>
    <WithDropdownMessage
      :status="validationStatus"
      :msg-error="validationError"
      msg-placement="top"
    >
      <TextInput
        v-model="email"
        type="email"
        placeholder="Email"
        :tabindex="1"
        autofocus
        :status="validationStatus"
        :disabled="isLoading || status === 'success'"
        @keyup.enter="go"
      />
    </WithDropdownMessage>

    <Honeypot v-model="website" />

    <CapWidget
      v-if="capConfigured"
      :api-url="cap.apiUrl"
      :site-key="cap.siteKey"
      :reset-signal="capResetSignal"
      :disabled="isLoading"
      @solve="capToken = $event"
      @expire="capToken = ''"
    />
    <PanelBanner
      v-else
      color="red"
      :icon="OctagonAlert"
    >
      Captcha indisponible.
    </PanelBanner>

    <TextButton
      aspect="flat"
      size="large"
      color="neutral"
      :loading="isLoading"
      :disabled="!canSubmit || isLoading || status === 'success'"
      @click="go"
    >
      Réinitialiser
    </TextButton>
  </Panel>
</template>

<style scoped lang="scss">
.AccountAskPasswordResetPanel {
}
</style>
```

- [ ] **Step 5.3: Typecheck**

```bash
cd gui && npx nuxi typecheck 2>&1 | tail -25
```

Expected: zero errors. Empty output, exit code 0.

If errors remain, stop and investigate before committing.

- [ ] **Step 5.4: Commit**

```bash
git add gui/app/composables/auth-password-reset.ts gui/app/components/account/AccountAskPasswordResetPanel.vue
git commit -m "feat(gui): wire cap+honeypot on /me/account/forgotten-password"
```

---

## Task 6: Manual verification (no commit)

No GUI test framework exists. Verify each scenario in a running dev environment.

**Setup:**

```bash
# 1. API must be running with cap, db, redis up — use existing docker setup.

# 2. GUI dev server with cap env vars:
cd gui && NUXT_PUBLIC_CAP_API_URL=https://your-cap.example.com \
        NUXT_PUBLIC_CAP_SITE_KEY=<your-site-key> \
        npm run dev
```

Navigate to `http://localhost:3000` and run each step.

- [ ] **Step 6.1: Anonymous signup happy path**

1. Go to `/me/account/new`.
2. Step 1 (name) → enter a valid name → "Suivant".
3. Step 2 (email) → enter a new email → "Suivant".
4. Step 3 (password) → enter a valid password. Cap widget appears below.
5. Solve cap. "Créer un compte" becomes enabled.
6. Click "Créer un compte".
7. Expect: redirect to `/me/account/pending-validation` after ~1.2s.

- [ ] **Step 6.2: Item create happy path (authenticated)**

1. Log in.
2. Go to `/me/items/new`.
3. Fill form (name, description, age, region, ≥1 image).
4. Solve cap below the form.
5. "Enregistrer" enables.
6. Click — expect redirect to `/me/items` and the new item shows up.

- [ ] **Step 6.3: Password reset happy path**

1. Logged out, go to `/me/account/forgotten-password`.
2. Enter a real email (validation shows green).
3. Solve cap.
4. "Réinitialiser" enables.
5. Click — expect success banner; reset email arrives.

- [ ] **Step 6.4: Honeypot via Vue devtools**

1. On `/me/items/new` (with all fields filled and cap solved): open Vue devtools, locate the page component's `website` ref, set it to `"http://spam.example"`.
2. Expect: "Enregistrer" disables.
3. Reset `website` to `""` — button re-enables.

Repeat on `/me/account/new` (password step) and `/me/account/forgotten-password`.

- [ ] **Step 6.5: Cap config missing**

1. Restart `npm run dev` without `NUXT_PUBLIC_CAP_API_URL` / `NUXT_PUBLIC_CAP_SITE_KEY`.
2. Visit each of the three pages.
3. Expect: red `<PanelBanner>` "Captcha indisponible." in place of the widget. Submit disabled.

- [ ] **Step 6.6: Error toasts**

1. Stop the API (or block the cap server) → submit any of the three forms → expect "Problème de connexion" toast.
2. Burst-submit the password-reset form until 429 → expect "Trop d'envois" toast.
3. Force a 400 (mismatched cap secret on the API) → expect "Captcha invalide" toast.

- [ ] **Step 6.7: Contact page still works**

Quick sanity check: `/me/contact` form still submits, the swapped-in `<Honeypot>` behaves the same as before.

- [ ] **Step 6.8: Final typecheck**

```bash
cd gui && npx nuxi typecheck 2>&1 | tail -5
```

Expected: clean (zero errors, exit 0).

---

## Self-review

**Spec coverage** (against `docs/superpowers/specs/2026-05-12-cap-retrofit-design.md`):

| Spec section | Plan task |
| --- | --- |
| §"Architecture / New files" — `<Honeypot>` | Task 2 |
| §"Architecture / Modified files" — openapi regen | Task 1 |
| §"Architecture / Modified files" — `contact.ts` @ts-expect-error drop | Task 1 |
| §"Architecture / Modified files" — `useCreateAccount` | Task 4 (no code change; UserCreate now wider — covered implicitly via type) |
| §"Architecture / Modified files" — `useCreateItemMutation` | Task 3 (no body change; type widens automatically) |
| §"Architecture / Modified files" — `useAskPasswordReset` signature | Task 5 |
| §"Architecture / Modified files" — `mutations/auth.ts` cleanup | Task 1 |
| §"Architecture / Modified files" — `me/items/new.vue` | Task 3 |
| §"Architecture / Modified files" — `AccountCreationPasswordForm` | Task 4 |
| §"Architecture / Modified files" — `me/account/new.vue` | Task 4 |
| §"Architecture / Modified files" — `AccountAskPasswordResetPanel` | Task 5 |
| §"Architecture / Modified files" — `ItemEditionForm` `submitDisabled` | Task 3 |
| §"Architecture / Modified files" — `contact.vue` honeypot swap | Task 2 |
| §"Components / <Honeypot>" | Task 2 |
| §"Components / <CapWidget>" — reused unchanged | — |
| §"Composables" — all three | Tasks 1, 3, 4, 5 |
| §"Page changes" — three pages | Tasks 3, 4, 5 |
| §"Error mapping" — uniform 5-branch toast | Tasks 3, 4, 5 (one copy each) |
| §"Verification" — typecheck clean | Step 6.8 |
| §"Verification" — manual paths | Task 6 |

No gaps.

**Placeholder scan** — none.

**Type consistency**

- `ItemFormData` declared in Task 3.1, consumed by `ItemEditionForm.vue` emit (3.2) and `me/items/new.vue` submit handler (3.3). Names match.
- `ItemCreate` continues to denote the full body (with cap_token+website) post-regen — consumed by `useCreateItemMutation` (no edit needed; openapi type widens automatically).
- `UserCreate` similarly widens — `me/account/new.vue` now passes `{ name, email, password, cap_token, website }` matching the new shape.
- `AccountCreationPasswordForm` exposes `bumpResetSignal` via `defineExpose` (Task 4.1); `me/account/new.vue` accesses it via `passwordFormRef.value?.bumpResetSignal()` (Task 4.2). Names match.
- `capToken`, `website`, `capResetSignal`, `capConfigured`, `mapErrorToToast` — all used consistently across pages with identical types (`Ref<string>`, `Ref<number>`, `ComputedRef<boolean>`, `(err: FetchError | null) => void`).

All consistent.
