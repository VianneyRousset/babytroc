# Navigation AppBack Redesign — Design Spec

**Date:** 2026-05-03
**Scope:** Replace hardcoded navigation blacklist with declarative `appBack` page meta
**Goal:** Each page declares its own back behavior via `definePageMeta({ appBack })`, and `AppPage` auto-renders the back button in both mobile and desktop headers.

---

## 1. The `appBack` Page Meta Option

New property on `definePageMeta`:

| Value | Behavior |
|-------|----------|
| `true` | Show AppBack, fallback to `currentTabRoot` |
| `string` or route object | Show AppBack with custom fallback |
| `false` | Block back navigation entirely (modal pages) |
| `undefined` (not set) | No AppBack shown (root pages like `/me`, `/explore`) |

**Type augmentation** (in `app/types/page-meta.d.ts` or similar):

```ts
declare module '#app' {
  interface PageMeta {
    appBack?: boolean | string | RouteLocationAsRelativeGeneric | RouteLocationAsPathGeneric
  }
}
```

## 2. `goBack()` Changes

In `app/composables/navigation.ts`:

- Remove the hardcoded blacklist array (`/me/account/pending-validation`, `/me/account/validate`)
- Instead, read `route.meta.appBack`:
  - If `appBack === false` → do nothing (blocked)
  - If `appBack` is a string/route object → use it as fallback
  - If `appBack === true` or `undefined` → use `currentTabRoot` as fallback
- Keep the cross-section detection logic (if previous route was different section, use fallback instead of `go(-1)`)

**Priority for fallback destination:**
1. `AppBack` component prop `fallback` (if provided — for rare per-instance overrides)
2. `route.meta.appBack` (if string/route)
3. `currentTabRoot` (automatic default)

## 3. `AppPage` Auto-Rendering

`AppPage` reads `route.meta.appBack` and when truthy:

- **Mobile**: if no `#mobile-header-bar` slot is provided, auto-renders a default mobile header with `AppBack` + page title (from `route.meta.title` or empty)
- **Desktop**: if no `#desktop` slot is provided, auto-renders an `AppHeaderDesktop` with `AppBack` in `#buttons-left`

Pages that provide their own `#mobile-header-bar` or `#desktop` slots override the auto-rendering entirely (they keep full control). The `AppBack` component inside those custom slots should still work — it reads `route.meta.appBack` for its fallback if no prop is passed.

## 4. `AppBack` Component Changes

`AppBack` currently accepts a `fallback` prop. Updated behavior:

- If `fallback` prop is provided → use it (unchanged)
- If not → read `route.meta.appBack` for fallback value
- If `route.meta.appBack === true` or `undefined` → default to `currentTabRoot`

## 5. Migration

All `/me` subpages that currently have manual `AppBack` in `#mobile-header-bar` will be migrated to use `definePageMeta({ appBack: true })` or `appBack: '/custom/fallback'`.

Pages that need custom headers (extra buttons, search, dropdowns) keep their manual slots but benefit from the fallback logic automatically via the `AppBack` component reading meta.

**Pages to update:**

| Page | `appBack` value |
|------|----------------|
| `me/index.vue` | not set (root) |
| `me/profile.vue` | `true` |
| `me/about.vue` | `true` |
| `me/faq.vue` | `true` |
| `me/politics.vue` | `true` |
| `me/contact.vue` | `true` |
| `me/loans/index.vue` | `true` |
| `me/loans/requests.vue` | `true` |
| `me/loans/archived.vue` | `true` |
| `me/borrowings/index.vue` | `true` |
| `me/borrowings/requests.vue` | `true` |
| `me/borrowings/archived.vue` | `true` |
| `me/items/index.vue` | `true` (keeps custom desktop header for "new item" button) |
| `me/items/new.vue` | `true` (keeps custom desktop header) |
| `me/account/index.vue` | `true` |
| `me/account/forgotten-password.vue` | `true` |
| `me/account/reset-password.vue` | `true` |
| `me/account/new.vue` | `'/me/account'` (keeps custom multi-step back logic) |
| `me/account/pending-validation.vue` | `false` |
| `me/account/validate.vue` | `false` |
| `explore/item/[item_id].vue` | `true` (keeps custom headers for actions) |
| `explore/user/[user_id].vue` | `true` (keeps custom headers) |

## 6. What Stays the Same

- Cross-section detection (if previous route was different section → use fallback)
- Route direction tracking plugin (`route.client.ts`)
- Page transition animations
- `AppNavigationMobile` / `AppNavigationDesktop` (section tabs)
- `currentTabRoot` logic in `useTab()`
