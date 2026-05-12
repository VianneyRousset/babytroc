# Contact page + cap widget — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire `/me/contact` to the existing `POST /v1/utils/contact` API endpoint, with a reusable `<CapWidget>` component providing the required cap PoW captcha.

**Architecture:** Three new artefacts in `gui/` — an ambient type file for the `cap-widget` custom element, a reusable `<CapWidget>` wrapper component, and a `useSendContactMessage` composable. The contact page is rewritten to consume them, pre-fill from `useAuth` + `useMe`, expose a hidden honeypot input, and map API errors to toasts.

**Tech Stack:** Nuxt 3, Vue 3 `<script setup>`, `@pinia/colada` (useMutation), `nuxt-open-fetch` (`$api`), `vue3-toastify` (`$toast`), SCSS modules. No new dependencies. Cap widget is loaded from `cdn.jsdelivr.net/npm/cap-widget` via `useHead`.

**Spec:** `docs/superpowers/specs/2026-05-12-contact-cap-design.md`

**Working directory for all paths below:** `/home/vianney/documents/projects/babytroc` (repo root).

---

## File map

| File | Action | Responsibility |
| --- | --- | --- |
| `gui/types/cap-widget.d.ts` | Create | Ambient declaration of the `cap-widget` custom element + `solve`/`expire` event payloads |
| `gui/app/components/ui/CapWidget.vue` | Create | Vue wrapper — loads CDN script via `useHead`, exposes typed props/emits, supports reset via `resetSignal` |
| `gui/app/composables/contact.ts` | Create | `useSendContactMessage()` wrapping `useMutation` against `POST /v1/utils/contact` |
| `gui/nuxt.config.ts` | Modify | Add `runtimeConfig.public.cap = { apiUrl, siteKey }`; mark `cap-widget` as a custom element via `vue.compilerOptions.isCustomElement`; include the new type file via `typescript.tsConfig.include` (only if needed) |
| `gui/app/pages/me/contact.vue` | Modify | Replace fake submit flow with real one — pre-fill, honeypot, message counter, cap widget, error mapping |

---

## Pre-task note on openapi types

`nuxt-open-fetch` types `$api` paths from `gui/openapi/api/openapi.json`. That file is stale and does NOT currently contain `/v1/utils/contact` (the endpoint was added on the API side after the last regeneration). The plan handles this with a `// @ts-expect-error` suppression that mirrors `gui/app/composables/auth-login.ts:16` (existing pattern). If you can regenerate `openapi.json` before starting, the suppression line can be removed and TS picks the typed path up directly.

Regeneration recipe (optional, run if API is available):

```bash
# in api/ — start the API once with all env vars set:
cd api && uv run uvicorn babytroc.app:create_app --factory --port 8000 &

# in repo root — dump the spec:
curl -s http://localhost:8000/openapi.json | python3 -m json.tool > gui/openapi/api/openapi.json

# stop the dev API
kill %1
```

If you skip this, leave the `@ts-expect-error` in place — Task 3 includes the exact line.

---

## Task 1: Runtime config + cap-widget custom-element registration + ambient types

**Files:**
- Create: `gui/types/cap-widget.d.ts`
- Modify: `gui/nuxt.config.ts` — add `runtimeConfig.public.cap`, `vue.compilerOptions.isCustomElement`, `typescript.tsConfig.include` if needed

- [ ] **Step 1.1: Create ambient declaration file for `cap-widget` element + events**

Create `gui/types/cap-widget.d.ts`:

```ts
export {};

/**
 * Ambient typing for the cap-widget custom element loaded from
 * https://cdn.jsdelivr.net/npm/cap-widget.
 *
 * The widget renders a Proof-of-Work captcha and emits CustomEvents:
 *   - "solve" with { detail: { token: string } }
 *   - "expire" (no detail)
 * It also exposes a reset() method on the element instance.
 */
declare global {
  type CapSolveEventDetail = { token: string };
  type CapSolveEvent = CustomEvent<CapSolveEventDetail>;
  type CapExpireEvent = CustomEvent<void>;

  interface CapWidgetElement extends HTMLElement {
    reset?: () => void;
  }

  interface HTMLElementEventMap {
    solve: CapSolveEvent;
    expire: CapExpireEvent;
  }
}
```

- [ ] **Step 1.2: Add cap runtime config + `isCustomElement` to `nuxt.config.ts`**

Locate the `runtimeConfig` block (around `gui/nuxt.config.ts:114`) and extend it. Locate the `vite` block (around `gui/nuxt.config.ts:141`) and add a sibling `vue` block at the same level (one level deep inside `defineNuxtConfig({…})`).

Find this block in `gui/nuxt.config.ts`:

```ts
	runtimeConfig: {
		public: {
			openFetch: {
				api: {
					baseURL: "/api",
				},
			},
		},
	},
```

Replace with:

```ts
	runtimeConfig: {
		public: {
			openFetch: {
				api: {
					baseURL: "/api",
				},
			},
			cap: {
				apiUrl: "",
				siteKey: "",
			},
		},
	},
```

Then, at the same top level as `vite:` / `typescript:` (NOT nested inside `vite`), add a new `vue` key:

```ts
	vue: {
		compilerOptions: {
			isCustomElement: (tag) => tag === "cap-widget",
		},
	},
```

- [ ] **Step 1.3: Run typecheck to confirm the config + ambient types load**

```bash
cd gui && pnpm install --frozen-lockfile  # only if you haven't installed yet
cd gui && pnpm exec nuxi prepare
cd gui && pnpm exec nuxi typecheck
```

Expected: no errors. (If `pnpm` is not the package manager in this repo, use `npm` or `yarn` — check `gui/package.json` `packageManager` or the existence of `pnpm-lock.yaml` / `package-lock.json` / `yarn.lock`.)

- [ ] **Step 1.4: Commit**

```bash
git add gui/types/cap-widget.d.ts gui/nuxt.config.ts
git commit -m "feat(gui): wire cap runtime config and cap-widget custom element"
```

---

## Task 2: `<CapWidget>` reusable component

**Files:**
- Create: `gui/app/components/ui/CapWidget.vue`

- [ ] **Step 2.1: Create the component file**

Create `gui/app/components/ui/CapWidget.vue` with full content:

```vue
<script setup lang="ts">
const props = withDefaults(
	defineProps<{
		apiUrl: string;
		siteKey: string;
		disabled?: boolean;
		resetSignal?: number | string;
	}>(),
	{
		disabled: false,
		resetSignal: 0,
	},
);

const emit = defineEmits<{
	(e: "solve", token: string): void;
	(e: "expire"): void;
}>();

const { apiUrl, siteKey, disabled, resetSignal } = toRefs(props);

const endpoint = computed(() => `${unref(apiUrl)}/${unref(siteKey)}/`);

useHead({
	script: [
		{
			src: "https://cdn.jsdelivr.net/npm/cap-widget",
			key: "cap-widget-script",
			tagPosition: "bodyClose",
		},
	],
});

const el = useTemplateRef<CapWidgetElement>("el");

function onSolve(event: Event) {
	if (unref(disabled)) return;
	const detail = (event as CapSolveEvent).detail;
	emit("solve", detail.token);
}

function onExpire() {
	if (unref(disabled)) return;
	emit("expire");
}

onMounted(() => {
	const node = unref(el);
	if (node == null) return;
	node.addEventListener("solve", onSolve);
	node.addEventListener("expire", onExpire);
});

onBeforeUnmount(() => {
	const node = unref(el);
	if (node == null) return;
	node.removeEventListener("solve", onSolve);
	node.removeEventListener("expire", onExpire);
});

watch(resetSignal, () => {
	const node = unref(el);
	node?.reset?.();
});
</script>

<template>
  <div class="CapWidget">
    <cap-widget
      ref="el"
      :data-cap-api-endpoint="endpoint"
    />
  </div>
</template>

<style scoped lang="scss">
.CapWidget {
  @include flex-row;
  justify-content: center;
}
</style>
```

- [ ] **Step 2.2: Typecheck**

```bash
cd gui && pnpm exec nuxi typecheck
```

Expected: no errors. If TS complains about `cap-widget` in the template, re-verify Step 1.2 — `vue.compilerOptions.isCustomElement` must be set.

- [ ] **Step 2.3: Commit**

```bash
git add gui/app/components/ui/CapWidget.vue
git commit -m "feat(gui): add reusable <CapWidget> wrapper for cap PoW captcha"
```

---

## Task 3: `useSendContactMessage` composable

**Files:**
- Create: `gui/app/composables/contact.ts`

- [ ] **Step 3.1: Create the composable**

Create `gui/app/composables/contact.ts`:

```ts
export type ContactSubmit = {
	name: string;
	email: string;
	subject: string;
	message: string;
	capToken: string;
};

export function useSendContactMessage() {
	const { $api } = useNuxtApp();

	const { mutateAsync: sendContactMessage, ...mutation } = useMutation({
		mutation: (ctx: ContactSubmit) => {
			// @ts-expect-error: /v1/utils/contact not yet in gui/openapi/api/openapi.json (regenerate to remove this line)
			return $api("/v1/utils/contact", {
				method: "POST",
				body: {
					name: ctx.name,
					email: ctx.email,
					subject: ctx.subject,
					message: ctx.message,
					cap_token: ctx.capToken,
					website: "",
				},
			});
		},
	});

	return { sendContactMessage, ...mutation };
}
```

> If you regenerated `openapi.json` in the pre-task step and `/v1/utils/contact` is now in the schema, delete the `// @ts-expect-error` line.

- [ ] **Step 3.2: Typecheck**

```bash
cd gui && pnpm exec nuxi typecheck
```

Expected: no errors. The `@ts-expect-error` directive itself becomes an error if the underlying call type-checks fine — in that case (i.e., schema was regenerated), remove the directive.

- [ ] **Step 3.3: Commit**

```bash
git add gui/app/composables/contact.ts
git commit -m "feat(gui): add useSendContactMessage composable"
```

---

## Task 4: Rewrite `me/contact.vue`

**Files:**
- Modify: `gui/app/pages/me/contact.vue` (complete rewrite of `<script setup>` + `<template>`; keep most of `<style>`)

- [ ] **Step 4.1: Replace the whole file with the wired version**

Replace the entire contents of `gui/app/pages/me/contact.vue` with:

```vue
<script setup lang="ts">
import type { FetchError } from "ofetch";
import { OctagonAlert, Send } from "lucide-vue-next";

definePageMeta({
	layout: "me",
	appBack: true,
	appTitle: "Contact",
});

const { $toast } = useNuxtApp();
const { cap } = useRuntimeConfig().public;

const { loggedIn } = useAuth();
const { me } = useMe();

const nom = ref("");
const email = ref("");
const sujet = ref("");
const message = ref("");
const capToken = ref("");
const website = ref(""); // honeypot
const capResetSignal = ref(0);
const dismissedSuccess = ref(false);

const { sendContactMessage, isLoading, status, error } =
	useSendContactMessage();

// Pre-fill from authenticated session once it resolves
watch(
	[loggedIn, me],
	([loggedInValue, meValue]) => {
		if (loggedInValue !== true || meValue == null) return;
		if (unref(nom) === "") nom.value = meValue.name;
		if (unref(email) === "") email.value = meValue.email;
	},
	{ immediate: true },
);

const capConfigured = computed<boolean>(
	() => cap.apiUrl !== "" && cap.siteKey !== "",
);

const messageTooLong = computed<boolean>(() => unref(message).length > 5000);

const emailValid = computed<boolean>(() =>
	/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(unref(email)),
);

const valid = computed<boolean>(
	() =>
		unref(nom).trim() !== "" &&
		unref(sujet).trim() !== "" &&
		unref(message).trim() !== "" &&
		unref(emailValid) &&
		!unref(messageTooLong) &&
		unref(capToken) !== "" &&
		unref(capConfigured),
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

async function submit() {
	if (!unref(valid) || unref(isLoading)) return;

	try {
		await sendContactMessage({
			name: unref(nom),
			email: unref(email),
			subject: unref(sujet),
			message: unref(message),
			capToken: unref(capToken),
		});
		// success — clear editable fields, reset widget (token consumed)
		sujet.value = "";
		message.value = "";
		capToken.value = "";
		capResetSignal.value += 1;
		dismissedSuccess.value = false;
	} catch {
		mapErrorToToast(unref(error));
		capToken.value = "";
		capResetSignal.value += 1;
	}
}

function resetForNewMessage() {
	dismissedSuccess.value = true;
}
</script>

<template>
  <AppPage
    with-header
    :max-width="600"
  >
    <main>
      <section class="section intro">
        <p>
          Une question, un problème ou une suggestion&nbsp;? Contactez-nous&nbsp;!
        </p>
        <p>
          Email&nbsp;: <a href="mailto:contact@babytroc.ch">contact@babytroc.ch</a>
        </p>
      </section>

      <hr class="divider">

      <section class="section form">
        <h2>Formulaire de contact</h2>

        <transition
          name="pop"
          mode="out-in"
        >
          <div
            v-if="status === 'success' && !dismissedSuccess"
            class="success"
          >
            <p>Merci&nbsp;! Votre message a bien été envoyé.</p>
            <TextButton
              aspect="outline"
              size="small"
              @click="resetForNewMessage"
            >
              Envoyer un autre message
            </TextButton>
          </div>

          <form
            v-else
            @submit.prevent="submit"
          >
            <label>
              Nom
              <TextInput
                v-model="nom"
                placeholder="Votre nom"
                :disabled="loggedIn === true || isLoading"
              />
            </label>
            <label>
              Email
              <TextInput
                v-model="email"
                type="email"
                placeholder="Votre adresse email"
                :disabled="loggedIn === true || isLoading"
              />
            </label>
            <label>
              Sujet
              <TextInput
                v-model="sujet"
                placeholder="Sujet de votre message"
                :disabled="isLoading"
              />
            </label>
            <label>
              Message
              <LongTextInput
                v-model="message"
                placeholder="Votre message..."
                :disabled="isLoading"
              />
              <small
                class="counter"
                :class="{ over: messageTooLong }"
              >{{ message.length }} / 5000</small>
            </label>

            <input
              v-model="website"
              type="text"
              name="website"
              tabindex="-1"
              autocomplete="off"
              aria-hidden="true"
              class="honeypot"
            >

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
              Captcha indisponible. Le formulaire est désactivé.
            </PanelBanner>

            <TextButton
              aspect="flat"
              color="primary"
              :icon="Send"
              :disabled="!valid || isLoading"
              :loading="isLoading"
              @click="submit"
            >
              Envoyer
            </TextButton>
          </form>
        </transition>
      </section>
    </main>
  </AppPage>
</template>

<style scoped lang="scss">
main {
  @include flex-column;
  gap: 0;
  padding: $space-4;
}

.divider {
  border: none;
  border-top: 1px solid $divider;
  margin: $space-2 0;
}

.section {
  padding: $space-6 0;
}

.intro {
  @include flex-column;
  align-items: stretch;
  gap: $space-2;

  p {
    margin: 0;
    color: $text-secondary;
    line-height: 1.6;
  }

  a {
    color: $primary-600;
    font-weight: 600;
  }
}

.form {
  @include flex-column;
  align-items: stretch;
  gap: $space-4;

  h2 {
    font-family: "Plus Jakarta Sans", sans-serif;
    font-size: 1.25rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    margin: 0;
  }

  form {
    @include flex-column;
    align-items: stretch;
    gap: $space-4;
  }

  label {
    @include flex-column;
    align-items: stretch;
    gap: $space-1;
    font-size: 0.875rem;
    font-weight: 500;
    color: $text-secondary;
  }

  .counter {
    font-size: 0.75rem;
    color: $text-tertiary;
    align-self: flex-end;

    &.over {
      color: $red-600;
      font-weight: 600;
    }
  }

  .honeypot {
    position: absolute;
    left: -9999px;
    width: 1px;
    height: 1px;
    opacity: 0;
  }

  .success {
    @include flex-column;
    align-items: center;
    gap: $space-4;
    padding: $space-8 0;
    text-align: center;

    p {
      margin: 0;
      color: $text-primary;
      font-weight: 600;
    }
  }
}
</style>
```

- [ ] **Step 4.2: Typecheck**

```bash
cd gui && pnpm exec nuxi typecheck
```

Expected: no errors. If `PanelBanner` isn't auto-imported, check `gui/app/components/ui/panel/PanelBanner.vue` exists (it does in the current tree).

- [ ] **Step 4.3: Commit**

```bash
git add gui/app/pages/me/contact.vue
git commit -m "feat(gui): wire /me/contact to API with cap captcha + honeypot"
```

---

## Task 5: Manual verification (no commit)

This task has no automated tests — the GUI repo has no test framework. Verify each scenario manually with the dev server.

**Setup:**

```bash
# 1. Start the API with a working cap server, db, redis, and CAP_API_URL/CAP_SITE_KEY/CAP_SECRET_KEY set.
cd api && uv run uvicorn babytroc.app:create_app --factory --port 8000

# 2. In another shell, start the GUI dev server with the public cap config exposed.
cd gui && NUXT_PUBLIC_CAP_API_URL=https://cap.example.com \
        NUXT_PUBLIC_CAP_SITE_KEY=<your-site-key> \
        pnpm dev
```

Navigate to `http://localhost:3000/me/contact`.

- [ ] **Step 5.1: Happy path (anonymous)**

1. Open `/me/contact` while logged out.
2. Fill name, email, subject, message.
3. Solve cap challenge — button enables.
4. Click "Envoyer".
5. Expect: inline success block ("Merci ! ..."). Inbox at `CONTACT_EMAIL` receives the email.

- [ ] **Step 5.2: Happy path (authenticated)**

1. Log in via `/me/account`.
2. Open `/me/contact`.
3. Verify name + email inputs are visibly disabled and pre-filled from the logged-in user.
4. Fill subject + message; solve cap; submit.
5. Expect: inline success block; API logs show `authenticated_user_id` set.

- [ ] **Step 5.3: Honeypot triggers rejection**

1. While the form is open, use devtools to set the hidden `website` input's `.value` to `"http://spam.example"`.
2. Solve cap, submit.
3. Expect: toast "Captcha invalide, veuillez réessayer." (API returns 400 `INVALID_SUBMISSION` for both honeypot and bad cap — server message is intentionally shared).

- [ ] **Step 5.4: Cap config missing**

1. Restart `pnpm dev` without `NUXT_PUBLIC_CAP_API_URL` / `NUXT_PUBLIC_CAP_SITE_KEY`.
2. Open `/me/contact`.
3. Expect: red "Captcha indisponible" banner instead of the widget; "Envoyer" button disabled regardless of field contents.

- [ ] **Step 5.5: Cap token cleared after submit**

1. Submit successfully once (Step 5.1 path).
2. Without reloading the page, click "Envoyer un autre message" to return to the form.
3. Expect: cap widget shows a fresh challenge (already reset on success), submit button disabled until you solve again.

- [ ] **Step 5.6: Rate-limit toast**

1. Anonymous: submit successfully N times in quick succession (N = `CONTACT_RATE_LIMIT_ANON`).
2. On the (N+1)-th submit, expect: toast "Trop d'envois. Réessayez dans quelques minutes." (HTTP 429).

- [ ] **Step 5.7: Message over 5000 chars**

1. Paste a 5001-character message.
2. Expect: counter turns red, "Envoyer" button stays disabled.

- [ ] **Step 5.8: Typecheck final**

```bash
cd gui && pnpm exec nuxi typecheck
```

Expected: clean.

---

## Self-review

Run through this list once you've finished writing the plan (you, the plan author — not the executor).

**Spec coverage**

- §1 architecture (files list) — covered by Task 1–4
- §2 `<CapWidget>` — Task 2
- §3 `useSendContactMessage` — Task 3
- §4 `me/contact.vue` rewrite (pre-fill, honeypot, counter, cap, success/error UX, French copy) — Task 4
- §5 runtime config + env plumbing — Task 1
- §5 fallback banner when cap config missing — Task 4 template + Step 5.4
- §6 error mapping table — Task 4 `mapErrorToToast`
- §7 out-of-scope retrofits — explicitly NOT in this plan (matches design)
- §8 manual verification — Task 5

**Placeholder scan** — none ("TBD"/"TODO" appear only inside comments that quote API behaviour, not as plan placeholders).

**Type consistency**

- `ContactSubmit` type (Task 3) field names `name|email|subject|message|capToken` — page maps from French refs in Task 4 `submit()`.
- `CapWidget` props `apiUrl|siteKey|disabled|resetSignal` (Task 2) — same names used in Task 4 template.
- `CapWidget` emits `solve(token: string)` + `expire()` — used as `@solve="capToken = $event"` + `@expire="capToken = ''"` in Task 4.
- `CapWidgetElement`, `CapSolveEvent` types (Task 1) consumed in Task 2.
- `runtimeConfig.public.cap.apiUrl / siteKey` (Task 1) consumed in Task 4 via `useRuntimeConfig().public.cap`.

All consistent.
