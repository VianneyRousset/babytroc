# Airbnb-Style UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform Babytroc's UI into a clean, airy, Airbnb-inspired design while keeping the sage green brand identity.

**Architecture:** Component-first approach. Update design tokens and base SCSS first, then rework UI components, then navigation, then pages, then add mobile patterns. Each task produces a visually testable change.

**Tech Stack:** Nuxt 4 / Vue 3 / Tailwind CSS / SCSS / Radix Vue / Lucide icons

---

## File Map

**Design Tokens (modified):**
- `app/assets/styles/_colors.scss` — add new semantic color variables
- `app/assets/styles/_constants.scss` — add spacing, radius, shadow, typography tokens
- `app/assets/styles/_mixings.scss` — add new utility mixins
- `app/assets/styles/_fonts.scss` — remove Instrument Sans declarations
- `app/assets/styles/main.scss` — rework global styles (typography, inputs, layout)
- `app/assets/styles/animations.scss` — refine transition timings and add new animations
- `tailwind.config.js` — update border radius, shadows, colors to match tokens

**UI Components (modified):**
- `app/components/ui/inputs/TextButton.vue` — remove bezel, pill shape, refined sizes
- `app/components/ui/inputs/TextInput.vue` — new focus style, height, radius
- `app/components/ui/inputs/SearchInput.vue` — shadow states, height
- `app/components/ui/slab/Slab.vue` — refined hover, padding, chevron color
- `app/components/ui/panel/Panel.vue` — max-width 1200, padding updates
- `app/components/ui/Drawer.vue` — bottom sheet on mobile with drag handle
- `app/components/ui/Overlay.vue` — lighter backdrop with blur
- `app/components/ui/list/ListEmpty.vue` — center-aligned, generous padding
- `app/components/ui/list/ListError.vue` — softer styling
- `app/components/ui/list/ListLoader.vue` — pulse animation
- `app/components/ui/loading/LoadingAnimation.vue` — pulse variant
- `app/components/ui/ImageGallery.vue` — rounded images, full-screen mobile gallery

**Navigation (modified):**
- `app/components/app/navigation/AppNavigationMobile.vue` — refined colors, no shadow, safe area
- `app/components/app/navigation/AppNavigationDesktop.vue` — white bg, pill active state
- `app/components/app/header/AppHeaderMobileBar.vue` — white bg, scroll shadow

**Pages (modified):**
- `app/components/item/card/ItemCard.vue` — refined proportions, typography
- `app/components/item/card/ItemCardsCollection.vue` — CSS grid columns, gap refinement
- `app/components/chat/ChatMessage.vue` — new bubble colors, radius
- `app/pages/explore/index.vue` — background color, card refinements
- `app/pages/me/index.vue` — card-based layout
- `app/pages/saved.vue` — empty state
- `app/layouts/default.vue` — minor adjustments

**Font files to delete:**
- `app/assets/fonts/instrument-sans-v1-latin-*.woff2` (all 8 files)

---

### Task 1: Update Design Tokens — Colors and Constants

**Files:**
- Modify: `app/assets/styles/_colors.scss`
- Modify: `app/assets/styles/_constants.scss`

- [ ] **Step 1: Add semantic color variables to `_colors.scss`**

Append these lines at the end of `app/assets/styles/_colors.scss`:

```scss
// Semantic colors for Airbnb-style redesign
$text-primary: #1a1a1a;
$text-secondary: #6a6a6a;
$text-tertiary: #767676;

$bg-page: #f7f7f7;
$bg-surface: #fff;
$bg-tag: #f7f7f7;
$bg-tag-active: #1a1a1a;

$text-tag: #444;
$text-tag-active: #fff;

$divider: #ebebeb;

$primary-text-safe: #3d6145; // 5.8:1 contrast on white for small text

$shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.06);
$shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
$shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);
```

- [ ] **Step 2: Update `_constants.scss` with spacing and radius tokens**

Replace the entire content of `app/assets/styles/_constants.scss` with:

```scss
$golden-ratio: 1.61803;

// Typography sizes
$text-md: 15px;
$text-sm: 13px;
$text-xs: 12px;

// Spacing scale (4px base grid)
$space-1: 4px;
$space-2: 8px;
$space-3: 12px;
$space-4: 16px;
$space-5: 20px;
$space-6: 24px;
$space-8: 32px;
$space-10: 40px;
$space-12: 48px;
$space-16: 64px;

// Border radius
$radius-sm: 8px;
$radius-md: 12px;
$radius-lg: 16px;
$radius-pill: 2rem;

// Animation easing
$ease-spring: cubic-bezier(0.32, 0.72, 0, 1);
```

- [ ] **Step 3: Verify the app still builds**

Run: `cd /home/vianney/documents/projects/babytroc/gui && npx nuxi typecheck`
Expected: No errors related to SCSS compilation.

- [ ] **Step 4: Commit**

```bash
git add app/assets/styles/_colors.scss app/assets/styles/_constants.scss
git commit -m "style: add semantic design tokens for Airbnb-style redesign"
```

---

### Task 2: Update Design Tokens — Mixins and Tailwind Config

**Files:**
- Modify: `app/assets/styles/_mixings.scss`
- Modify: `tailwind.config.js`

- [ ] **Step 1: Add new utility mixins to `_mixings.scss`**

Append these at the end of the file:

```scss
@mixin hover-only {
  @media (hover: hover) {
    &:hover {
      @content;
    }
  }
}

@mixin touch-feedback {
  &:active {
    opacity: 0.7;
    transition: opacity 60ms ease;
  }
}

@mixin safe-area-bottom {
  padding-bottom: env(safe-area-inset-bottom);
}
```

- [ ] **Step 2: Update `tailwind.config.js` border radius and shadows**

Replace the `borderRadius` and add `boxShadow` in the `extend` section of `tailwind.config.js`. The `extend` block should become:

```js
extend: {
  colors: {
    border: 'hsl(var(--border))',
    input: 'hsl(var(--input))',
    ring: 'hsl(var(--ring))',
    background: 'hsl(var(--background))',
    foreground: 'hsl(var(--foreground))',
    primary: {
      DEFAULT: 'hsl(var(--primary))',
      foreground: 'hsl(var(--primary-foreground))',
    },
    secondary: {
      DEFAULT: 'hsl(var(--secondary))',
      foreground: 'hsl(var(--secondary-foreground))',
    },
    destructive: {
      DEFAULT: 'hsl(var(--destructive))',
      foreground: 'hsl(var(--destructive-foreground))',
    },
    muted: {
      DEFAULT: 'hsl(var(--muted))',
      foreground: 'hsl(var(--muted-foreground))',
    },
    accent: {
      DEFAULT: 'hsl(var(--accent))',
      foreground: 'hsl(var(--accent-foreground))',
    },
    popover: {
      DEFAULT: 'hsl(var(--popover))',
      foreground: 'hsl(var(--popover-foreground))',
    },
    card: {
      DEFAULT: 'hsl(var(--card))',
      foreground: 'hsl(var(--card-foreground))',
    },
  },
  borderRadius: {
    xl: '16px',
    lg: '12px',
    md: '8px',
    sm: '4px',
    pill: '2rem',
  },
  boxShadow: {
    sm: '0 1px 2px rgba(0, 0, 0, 0.06)',
    md: '0 4px 12px rgba(0, 0, 0, 0.08)',
    lg: '0 8px 24px rgba(0, 0, 0, 0.12)',
  },
  keyframes: {
    'accordion-down': {
      from: { height: 0 },
      to: { height: 'var(--radix-accordion-content-height)' },
    },
    'accordion-up': {
      from: { height: 'var(--radix-accordion-content-height)' },
      to: { height: 0 },
    },
    'collapsible-down': {
      from: { height: 0 },
      to: { height: 'var(--radix-collapsible-content-height)' },
    },
    'collapsible-up': {
      from: { height: 'var(--radix-collapsible-content-height)' },
      to: { height: 0 },
    },
    'pulse-loading': {
      '0%, 100%': { opacity: 0.4 },
      '50%': { opacity: 1 },
    },
  },
  animation: {
    'accordion-down': 'accordion-down 0.2s ease-out',
    'accordion-up': 'accordion-up 0.2s ease-out',
    'collapsible-down': 'collapsible-down 0.2s ease-in-out',
    'collapsible-up': 'collapsible-up 0.2s ease-in-out',
    'pulse-loading': 'pulse-loading 1.5s ease-in-out infinite',
  },
},
```

- [ ] **Step 3: Commit**

```bash
git add app/assets/styles/_mixings.scss tailwind.config.js
git commit -m "style: add utility mixins and update Tailwind config for redesign"
```

---

### Task 3: Remove Instrument Sans and Update Typography

**Files:**
- Modify: `app/assets/styles/_fonts.scss`
- Modify: `app/assets/styles/main.scss`
- Delete: `app/assets/fonts/instrument-sans-v1-latin-*.woff2` (8 files)

- [ ] **Step 1: Remove all Instrument Sans `@font-face` declarations from `_fonts.scss`**

Remove lines 1–71 of `app/assets/styles/_fonts.scss` (all 8 `@font-face` blocks for Instrument Sans). The file should start with the `/* plus-jakarta-sans-200 - latin */` block.

- [ ] **Step 2: Delete Instrument Sans font files**

```bash
rm app/assets/fonts/instrument-sans-v1-latin-*.woff2
```

- [ ] **Step 3: Update global typography in `main.scss`**

Replace the `body` block (lines 1–15) with:

```scss
body {
  margin: 0;
  font-family: 'Inter', sans-serif;
  font-size: 0.95rem;
  color: $text-primary;
  background: $bg-page;

  --loader-color: #69717d;

  /* Toastify */
  --toastify-font-family: "Plus Jakarta Sans", sans-serif;
  --toastify-color-success: #729577;
  --toastify-color-error: #c90c0c;
  --toastify-icon-color-success: var(--toastify-color-success);
  --toastify-icon-color-error: var(--toastify-color-error);
  --toastify-color-progress-success: var(--toastify-color-success);
  --toastify-color-progress-error: var(--toastify-color-error);
}
```

Replace the heading styles (lines 17–35) with:

```scss
h1,
h2,
h3,
h4,
h5 {
  font-family: "Plus Jakarta Sans", sans-serif;
  margin: 0;
}

h1 {
  font-weight: 700;
  font-size: 1.75rem;
  letter-spacing: -0.02em;
  color: $text-primary;
}

h2 {
  color: $text-secondary;
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: -0.01em;
}
```

Replace the `input, textarea` block (lines 37–59) with:

```scss
input,
textarea {
  border: 1px solid #ddd;
  border-radius: $radius-sm;

  outline: none;

  padding: 0.6em 0.8em;

  font-family: 'Inter', sans-serif;
  font-size: 1em;

  &::placeholder {
    color: $text-tertiary;
  }

  &[disabled=false]:focus,
  &[disabled=false]:hover {
    outline: none;
    border-color: $text-primary;
  }
}
```

Replace the standalone `input` block (lines 61–63) with:

```scss
input {
  font-size: 1rem;
  height: 48px;
  box-sizing: border-box;
}
```

Replace the `.page h2` block inside `.page` (lines 87–96) with:

```scss
  h2 {
    color: $text-secondary;
    font-size: 1.25rem;
    font-weight: 600;
    letter-spacing: -0.01em;

    &:first-child {
      margin-top: 0;
    }
  }
```

- [ ] **Step 4: Verify the app builds**

Run: `cd /home/vianney/documents/projects/babytroc/gui && npx nuxi typecheck`
Expected: No SCSS compilation errors.

- [ ] **Step 5: Commit**

```bash
git add -A app/assets/styles/ app/assets/fonts/
git commit -m "style: remove Instrument Sans, update typography to design spec"
```

---

### Task 4: Update Animations

**Files:**
- Modify: `app/assets/styles/animations.scss`

- [ ] **Step 1: Replace animations.scss with refined timings**

Replace the full content of `app/assets/styles/animations.scss` with:

```scss
/* pop */
.pop-enter-active,
.pop-leave-active {
  transition: all 0.2s cubic-bezier(0.65, 0.54, 0.6, 1.5);
}

.pop-enter-from,
.pop-leave-to {
  transform: scale(0.5);
  opacity: 0;
}

/* slide-up (bottom sheet) */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 300ms $ease-spring, opacity 300ms ease-out;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translate(0, 100%);
  opacity: 0;
}

/* page-slide-forward and page-slide-backward */
.page-slide-forward-enter-active,
.page-slide-forward-leave-active,
.page-slide-backward-enter-active,
.page-slide-backward-leave-active {
  transition: transform 200ms $ease-spring, filter 200ms ease-out;
}

.page-slide-forward-enter-from,
.page-slide-backward-leave-to {
  transform: translateX(100%);
  z-index: 1;
}

.page-slide-forward-leave-to,
.page-slide-backward-enter-from {
  filter: brightness(0.9);
}

/* fade */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 150ms ease-in-out;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* pulse (for skeleton loaders) */
@keyframes pulse {
  0%, 100% {
    opacity: 0.4;
  }
  50% {
    opacity: 1;
  }
}

.skeleton-pulse {
  animation: pulse 1.5s ease-in-out infinite;
  background: $divider;
  border-radius: $radius-sm;
}
```

- [ ] **Step 2: Commit**

```bash
git add app/assets/styles/animations.scss
git commit -m "style: refine animations with spring easing and skeleton pulse"
```

---

### Task 5: Rework TextButton Component

**Files:**
- Modify: `app/components/ui/inputs/TextButton.vue`

- [ ] **Step 1: Remove `bezel` from props and classes**

In the `<script setup>` section, change the `aspect` prop type from `'flat' | 'outline' | 'bezel'` to `'flat' | 'outline'`.

In the `classes` computed, remove the line `bezel: unref(aspect) === 'bezel',`.

- [ ] **Step 2: Replace the `<style>` section**

Replace the entire `<style scoped lang="scss">` block with:

```scss
<style scoped lang="scss">
.TextButton {
  @include reset-link;

  display: block;
  position: relative;
  color: white;
  text-align: center;
  cursor: pointer;
  user-select: none;
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 0.95rem;
  border-radius: $radius-pill;

  padding: 0 $space-6;
  height: 40px;
  line-height: 40px;

  transition: background 200ms ease-out, border-color 200ms ease-out, color 200ms ease-out;

  --color-50: #{$neutral-50};
  --color-100: #{$neutral-100};
  --color-200: #{$neutral-200};
  --color-300: #{$neutral-300};
  --color-400: #{$neutral-400};
  --color-500: #{$neutral-500};
  --color-600: #{$neutral-600};
  --color-700: #{$neutral-700};
  --color-800: #{$neutral-800};
  --color-900: #{$neutral-900};

  .loader {
    @include flex-row-center;
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
  }

  .content {
    @include flex-row;
    align-content: center;
    justify-content: center;
    gap: $space-2;

    .icon {
      display: flex;
      align-items: center;
    }
  }

  &.loading > .content {
    opacity: 0.1;
  }

  &.primary {
    --color-50: #{$primary-50};
    --color-100: #{$primary-100};
    --color-200: #{$primary-200};
    --color-300: #{$primary-300};
    --color-400: #{$primary-400};
    --color-500: #{$primary-500};
    --color-600: #{$primary-600};
    --color-700: #{$primary-700};
    --color-800: #{$primary-800};
    --color-900: #{$primary-900};
  }

  &.red {
    --color-50: #{$red-50};
    --color-100: #{$red-100};
    --color-200: #{$red-200};
    --color-300: #{$red-300};
    --color-400: #{$red-400};
    --color-500: #{$red-500};
    --color-600: #{$red-600};
    --color-700: #{$red-700};
    --color-800: #{$red-800};
    --color-900: #{$red-900};
  }

  &.small {
    height: 36px;
    line-height: 36px;
    padding: 0 $space-4;
    font-size: 0.85rem;
  }

  &.large {
    height: 48px;
    line-height: 48px;
    padding: 0 $space-8;
    font-size: 1.05rem;
  }

  &.flat {
    background: var(--color-500);

    @include hover-only {
      background: var(--color-600);
    }

    @include touch-feedback;

    &.disabled, &.loading {
      background: var(--color-100);
      color: var(--color-400);
      cursor: default;
    }
  }

  &.outline {
    color: var(--color-500);
    border: 1.5px solid var(--color-500);
    background: transparent;

    /* compensate for the border width */
    height: 37px;
    line-height: 37px;

    &.small {
      height: 33px;
      line-height: 33px;
    }

    &.large {
      height: 45px;
      line-height: 45px;
    }

    @include hover-only {
      color: var(--color-600);
      border-color: var(--color-600);
    }

    @include touch-feedback;

    &.disabled, &.loading {
      color: var(--color-200);
      border-color: var(--color-200);
      cursor: default;
    }
  }
}
</style>
```

- [ ] **Step 3: Verify the app builds**

Run: `cd /home/vianney/documents/projects/babytroc/gui && npx nuxi typecheck`
Expected: No type errors. Any existing `aspect="bezel"` usages will need to be found and changed.

- [ ] **Step 4: Find and fix any `bezel` usages across the codebase**

```bash
cd /home/vianney/documents/projects/babytroc/gui && grep -rn 'bezel' app/
```

For each result, change `aspect="bezel"` to `aspect="flat"`.

- [ ] **Step 5: Commit**

```bash
git add -A app/components/ui/inputs/TextButton.vue
git add -u  # any files that had bezel references
git commit -m "style: rework TextButton — pill shape, drop bezel, refined sizes"
```

---

### Task 6: Rework TextInput and SearchInput

**Files:**
- Modify: `app/components/ui/inputs/TextInput.vue`
- Modify: `app/components/ui/inputs/SearchInput.vue`

- [ ] **Step 1: Update TextInput styles**

Replace the `<style scoped lang="scss">` section in `TextInput.vue` with:

```scss
<style scoped lang="scss">
.TextInput {
  @include flex-row;
  position: relative;

  input {
    flex: 1;
    font-size: 1rem;
    height: 48px;
    box-sizing: border-box;
    border: 1px solid #ddd;
    border-radius: $radius-sm;
    padding: 0 $space-4;
    transition: border-color 200ms ease-out;

    padding-right: v-bind("`max(${space-4}, calc(${iconsWidth}px + 12px))`");

    &:focus {
      border-color: $text-primary;
    }

    &:disabled {
      background: $bg-page;
      color: $text-tertiary;
    }

    &.error {
      border-color: $red-600;
    }
  }

  .icons-wrapper {
    @include flex-row;
    gap: $space-2;
    position: absolute;
    right: $space-3;
    color: $text-secondary;

    .LoadingAnimation {
      width: 24px;
    }

    .visibility {
      cursor: pointer;
    }

    .error {
      color: $red-600;
    }

    .success {
      color: $primary-text-safe;
    }
  }
}
</style>
```

- [ ] **Step 2: Update SearchInput styles**

Replace the `<style scoped lang="scss">` section in `SearchInput.vue` with:

```scss
<style scoped lang="scss">
.SearchInput {
  @include flex-row;
  position: relative;
  flex-grow: 1;

  input {
    width: 100%;
    height: 48px;
    box-sizing: border-box;
    padding: 0 $space-10;
    border: 1px solid #ddd;
    border-radius: $radius-sm;
    font-size: 1rem;
    box-shadow: $shadow-sm;
    transition: box-shadow 200ms ease-out, border-color 200ms ease-out;

    &:focus {
      box-shadow: $shadow-md;
      border-color: $text-primary;
    }
  }

  svg {
    position: absolute;
    stroke: $text-tertiary;

    &.search-icon {
      left: $space-3;
    }

    &.x-icon {
      right: $space-3;
      cursor: pointer;
    }
  }
}
</style>
```

- [ ] **Step 3: Commit**

```bash
git add app/components/ui/inputs/TextInput.vue app/components/ui/inputs/SearchInput.vue
git commit -m "style: rework TextInput and SearchInput with refined spacing and focus states"
```

---

### Task 7: Rework Slab and Panel Components

**Files:**
- Modify: `app/components/ui/slab/Slab.vue`
- Modify: `app/components/ui/panel/Panel.vue`

- [ ] **Step 1: Update Slab styles**

Replace the `<style scoped lang="scss">` block in `Slab.vue` with:

```scss
<style scoped lang="scss">
a {
  @include reset-link;
}

.Slab {
  @include flex-row;
  gap: $space-4;
  justify-content: flex-start;
  padding: $space-4;
  position: relative;
  border: 1px solid transparent;
  transition: background 150ms ease-out;

  @include hover-only {
    background: $bg-page !important;
    border-color: transparent !important;
  }

  @include touch-feedback;

  :deep(.title) {
    @include flex-column;
    align-items: stretch;
    gap: $space-1;
    flex: 1;

    font-family: "Plus Jakarta Sans";
    overflow: hidden;

    div {
      @include ellipsis-overflow;
      color: $text-primary;
      font-size: 1rem;
      font-weight: 500;

      &.sub {
        color: $text-secondary;
        font-size: 0.85rem;
        font-weight: 400;
      }
    }
  }

  .mini {
    @include ellipsis-overflow;
    max-width: 70%;
    position: absolute;
    bottom: $space-1;
    right: $space-4;
    color: $text-tertiary;
    font-size: 0.75rem;
  }

  .badge {
    @include flex-column-center;
    background: $red-600;
    min-height: 8px;
    min-width: 8px;
    border-radius: 50%;
  }

  /* chevron */
  & > svg {
    color: #ccc;
  }
}
</style>
```

- [ ] **Step 2: Update Panel styles**

Replace the `<style scoped lang="scss">` block in `Panel.vue`. Change the `.content` max-width default and padding:

```scss
<style scoped lang="scss">
.Panel {
  display: flex;
  flex-direction: column;
  align-items: center;

  .header {
    @include flex-row;
    justify-content: space-between;
    gap: $space-4;
    padding: 0 $space-6;
    height: 64px;
  }

  .content {
    box-sizing: border-box;
    width: 100%;
    max-width: v-bind("maxWidth ? `${maxWidth}px` : '1200px'");
    @include flex-column;
    align-items: stretch;
    gap: $space-4;
    padding: $space-4;

    @media (min-width: 1000px) {
      padding: $space-4 $space-6;
    }

    :deep(.legend) {
      font-style: italic;
      color: $text-secondary;
    }

    :deep(.h) {
      @include flex-row;
      align-items: stretch;
      gap: $space-4;
    }

    :deep(.v) {
      @include flex-column;
      align-items: stretch;
      gap: $space-4;
    }

    :deep(.golden-left) {
      & > *:nth-child(1) {
        flex: $golden-ratio;
      }

      & > *:nth-child(2) {
        flex: 1;
      }
    }

    :deep(.golden-right) {
      & > *:nth-child(1) {
        flex: 1;
      }

      & > *:nth-child(2) {
        flex: $golden-ratio;
      }
    }
  }
}
</style>
```

- [ ] **Step 3: Commit**

```bash
git add app/components/ui/slab/Slab.vue app/components/ui/panel/Panel.vue
git commit -m "style: rework Slab and Panel — refined spacing, hover, contrast"
```

---

### Task 8: Rework Drawer and Overlay for Bottom Sheet Pattern

**Files:**
- Modify: `app/components/ui/Drawer.vue`
- Modify: `app/components/ui/Overlay.vue`

- [ ] **Step 1: Replace Drawer.vue with bottom sheet support on mobile**

Replace the entire content of `app/components/ui/Drawer.vue` with:

```vue
<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    position?: 'left' | 'right' | 'bottom'
  }>(), {
    position: 'left',
  },
)

const { position } = toRefs(props)

const model = defineModel<boolean>({ default: false })

const slots = useSlots()
const device = useDevice()

// On mobile, force bottom position for bottom-sheet behavior
const effectivePosition = computed(() =>
  device.isMobile ? 'bottom' : unref(position),
)
</script>

<template>
  <div
    class="Drawer"
    :class="{ open: model }"
    :position="effectivePosition"
  >
    <div
      v-if="effectivePosition === 'bottom'"
      class="drag-handle"
    />
    <div
      v-if="slots.header"
      class="header"
    >
      <slot name="header" />
    </div>
    <slot />
  </div>
</template>

<style scoped lang="scss">
.Drawer {
  position: fixed;
  box-sizing: border-box;
  background: $bg-surface;
  overflow-y: auto;
  z-index: 10;

  transition: transform 300ms $ease-spring;

  &[position=right] {
    top: 0;
    bottom: 0;
    right: 0;
    width: 90%;
    max-width: 400px;
    transform: translate(100%, 0);
    box-shadow: $shadow-lg;
  }

  &[position=left] {
    top: 0;
    bottom: 0;
    left: 0;
    width: 90%;
    max-width: 400px;
    transform: translate(-100%, 0);
    box-shadow: $shadow-lg;
  }

  &[position=bottom] {
    left: 0;
    right: 0;
    bottom: 0;
    max-height: 90vh;
    border-radius: $radius-lg $radius-lg 0 0;
    transform: translate(0, 100%);
    box-shadow: $shadow-lg;
  }

  &.open {
    transform: translate(0, 0);
  }

  .drag-handle {
    display: flex;
    justify-content: center;
    padding: $space-3 0;

    &::after {
      content: '';
      width: 36px;
      height: 4px;
      border-radius: 2px;
      background: #ddd;
    }
  }

  .header {
    @include flex-row;
    justify-content: space-between;
    gap: $space-4;
    padding: 0 $space-4;
    height: 56px;
  }
}
</style>
```

- [ ] **Step 2: Update Overlay with lighter backdrop and blur**

Replace the `<style scoped lang="scss">` block in `Overlay.vue`:

```scss
<style scoped lang="scss">
.Overlay {
  @include flex-column-center;

  z-index: 9;

  position: fixed;
  overflow-x: hidden;
  overflow-y: auto;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;

  height: 100vh;
  width: 100vw;

  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(2px);
}
</style>
```

- [ ] **Step 3: Commit**

```bash
git add app/components/ui/Drawer.vue app/components/ui/Overlay.vue
git commit -m "style: rework Drawer as mobile bottom sheet, lighten Overlay backdrop"
```

---

### Task 9: Rework List States and Loading Animation

**Files:**
- Modify: `app/components/ui/list/ListEmpty.vue`
- Modify: `app/components/ui/list/ListError.vue`
- Modify: `app/components/ui/list/ListLoader.vue`
- Modify: `app/components/ui/loading/LoadingAnimation.vue`

- [ ] **Step 1: Read the current content of all four files**

```bash
cat app/components/ui/list/ListEmpty.vue app/components/ui/list/ListError.vue app/components/ui/list/ListLoader.vue app/components/ui/loading/LoadingAnimation.vue
```

- [ ] **Step 2: Update ListEmpty.vue styles**

Add/replace the `<style>` block to center content with generous padding:

```scss
<style scoped lang="scss">
.ListEmpty {
  @include flex-column-center;
  padding: $space-16 $space-4;
  color: $text-secondary;
  text-align: center;
  font-size: 0.95rem;

  svg {
    color: $text-tertiary;
    margin-bottom: $space-4;
  }
}
</style>
```

- [ ] **Step 3: Update ListError.vue styles**

Same pattern as ListEmpty — center-aligned with generous vertical padding:

```scss
<style scoped lang="scss">
.ListError {
  @include flex-column-center;
  padding: $space-16 $space-4;
  color: $text-secondary;
  text-align: center;
  font-size: 0.95rem;

  svg {
    color: $text-tertiary;
    margin-bottom: $space-4;
  }
}
</style>
```

- [ ] **Step 4: Update ListLoader to use skeleton pulse**

Replace the ListLoader content (if it currently wraps LoadingAnimation) with a simpler pulse block:

```vue
<template>
  <div class="ListLoader">
    <div class="skeleton-bar skeleton-pulse" />
    <div class="skeleton-bar skeleton-pulse" style="width: 70%;" />
    <div class="skeleton-bar skeleton-pulse" style="width: 85%;" />
  </div>
</template>

<style scoped lang="scss">
.ListLoader {
  @include flex-column;
  align-items: stretch;
  gap: $space-3;
  padding: $space-8 $space-4;

  .skeleton-bar {
    height: 16px;
    border-radius: $radius-sm;
    background: $divider;
  }
}
</style>
```

Remove the `<script>` section if it only imported LoadingAnimation.

- [ ] **Step 5: Commit**

```bash
git add app/components/ui/list/ app/components/ui/loading/
git commit -m "style: rework list states with centered layouts and skeleton pulse loader"
```

---

### Task 10: Rework Mobile Navigation

**Files:**
- Modify: `app/components/app/navigation/AppNavigationMobile.vue`

- [ ] **Step 1: Replace the `<style>` section**

Replace the entire `<style scoped lang="scss">` block with:

```scss
<style scoped lang="scss">
nav {
  @include flex-row;
  @include font-inter;
  @include safe-area-bottom;
  justify-content: space-evenly;
  font-size: 10px;
  font-weight: 500;
  background: $bg-surface;
  border-top: 1px solid $divider;
  height: 64px;

  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  box-sizing: border-box;
  z-index: 5;

  a {
    @include flex-column;
    @include reset-link;
    align-items: center;
    justify-content: center;
    margin: 0;
    width: 20%;
    gap: 2px;

    color: $text-tertiary;

    @include touch-feedback;

    &[active="true"] {
      color: $text-primary;
      font-weight: 600;
    }
  }

  a[section="saved"][logged-in=false],
  a[section="chats"][logged-in=false] {
    opacity: 0.4;
  }

  a[section="newitem"] {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    position: relative;
    bottom: 20px;

    background: $neutral-200;
    border: 2px solid $neutral-300;

    svg {
      stroke: $neutral-400;
      transform: translate(0, 1px);
    }

    &[active="true"] {
      background: $neutral-300;
      border-color: $neutral-400;
      svg {
        stroke: $bg-surface;
      }
    }

    &[logged-in=true] {
      background: $primary-200;
      border-color: $primary-300;

      svg {
        stroke: $primary-text-safe;
      }

      &[active="true"] {
        background: $primary-300;
        border-color: $primary-400;

        svg {
          stroke: $primary-50;
        }
      }
    }

    .icon {
      position: relative;
    }

    .badge {
      @include flex-column-center;
      position: absolute;
      right: -0.8rem;
      top: -0.3rem;
      background: $red-600;
      min-height: 8px;
      min-width: 8px;
      border-radius: 50%;
    }
  }
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add app/components/app/navigation/AppNavigationMobile.vue
git commit -m "style: rework mobile nav — clean border, no shadow, refined colors"
```

---

### Task 11: Rework Desktop Navigation

**Files:**
- Modify: `app/components/app/navigation/AppNavigationDesktop.vue`

- [ ] **Step 1: Replace the `<style>` section**

Replace the entire `<style scoped lang="scss">` block with:

```scss
<style scoped lang="scss">
nav {
  @include flex-row;
  justify-content: space-between;
  box-sizing: border-box;
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 14px;
  color: $text-secondary;
  background: $bg-surface;
  border-bottom: 1px solid $divider;
  padding: 0 $space-6;

  *[active="true"] {
    font-weight: 600;
    color: $text-primary;
  }

  & > div {
    @include flex-row;
    justify-content: space-between;
    padding: 0 $space-4;
    gap: $space-12;
  }

  .logo {
    font-family: "Plus Jakarta Sans", sans-serif;
    font-weight: 700;
    font-size: 1.25rem;
    color: $text-primary;
    letter-spacing: -0.02em;
  }

  ul {
    @include reset-list;
    @include flex-row;
    gap: $space-8;
    justify-content: space-evenly;
    height: 56px;

    li {
      position: relative;
      cursor: pointer;
      padding: $space-2 $space-3;
      border-radius: $radius-sm;
      transition: background 150ms ease-out;

      @include hover-only {
        background: $bg-page;
      }

      @include touch-feedback;

      &[active="true"] {
        background: $bg-page;
      }

      .badge {
        position: absolute;
        right: -4px;
        top: -2px;
        background: $red-600;
        min-height: 8px;
        min-width: 8px;
        border-radius: 50%;
      }
    }
  }
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add app/components/app/navigation/AppNavigationDesktop.vue
git commit -m "style: rework desktop nav — white bg, pill active states, Inter font"
```

---

### Task 12: Rework Mobile Header Bar

**Files:**
- Modify: `app/components/app/header/AppHeaderMobileBar.vue`

- [ ] **Step 1: Replace the `<style>` section**

Replace the entire `<style scoped lang="scss">` block with:

```scss
<style scoped lang="scss">
.AppHeaderMobileBar {
  @include flex-row;
  gap: $space-4;
  height: 56px;

  transform: translate(0, 0);
  transition: transform 100ms ease-out, opacity 100ms ease-out, box-shadow 200ms ease-out;

  padding: 0 $space-4;

  background-color: $bg-surface;
  color: $text-primary;
  border-bottom: 1px solid $divider;

  /* shadow appears on scroll — controlled by JS class toggle */
  box-shadow: none;

  &.scrolled {
    box-shadow: $shadow-sm;
  }

  &.hidden {
    transform: translate(0, -100%);
    opacity: 0;
    box-shadow: none;
  }

  :deep(& > svg) {
    stroke: $text-primary;
  }

  :deep(h1) {
    @include ellipsis-overflow;
    @include font-jakarta;
    position: relative;
    color: $text-primary;
    flex-grow: 1;
    margin: 0;
    font-weight: 600;
    font-size: 1.1rem;
    text-align: center;
  }
}
</style>
```

- [ ] **Step 2: Add scroll-based shadow class toggle**

In the `<script setup>` section, add a computed for `scrolled` class, and update the template to use it. After the existing `scrollingDown` ref, add:

```ts
const scrolled = computed(() => unref(y) > 0)
```

In the template, update the class binding on the header element:

```html
<header
  ref="header"
  class="AppHeaderMobileBar"
  :class="{
    hidden: hideOnScroll && y > (scrollOffset ?? appHeaderBarHeight) && scrollingDown,
    scrolled: scrolled
  }"
>
```

- [ ] **Step 3: Commit**

```bash
git add app/components/app/header/AppHeaderMobileBar.vue
git commit -m "style: rework mobile header — white bg, scroll shadow, centered title"
```

---

### Task 13: Rework ItemCard and ItemCardsCollection

**Files:**
- Modify: `app/components/item/card/ItemCard.vue`
- Modify: `app/components/item/card/ItemCardsCollection.vue`

- [ ] **Step 1: Update ItemCard styles**

Replace the `<style scoped lang="scss">` block in `ItemCard.vue`:

```scss
<style scoped lang="scss">
a {
  @include reset-link;
}

.ItemCard {
  display: flex;
  box-sizing: border-box;
  aspect-ratio: 1;
  flex-direction: column;
  justify-content: space-between;
  border-radius: $radius-lg;
  background-repeat: no-repeat;
  background-size: cover;
  background-position: center;
  cursor: pointer;
  color: $neutral-50;
  overflow: hidden;
  transition: box-shadow 200ms ease-out;

  @include hover-only {
    box-shadow: $shadow-md;
  }

  @include touch-feedback;

  &:target {
    scroll-margin-top: 20vh;
  }

  .status {
    display: flex;
    gap: $space-3;
    justify-content: right;
    padding: $space-3;

    svg {
      filter: drop-shadow(0px 0px 3px rgba(0, 0, 0, 0.5));
    }

    .not-available {
      color: $neutral-100;
    }

    .saved {
      color: $neutral-100;
      fill: $neutral-100;
    }
  }

  .info {
    padding: $space-3 $space-4;
    background: linear-gradient(transparent, rgba(0, 0, 0, 0.5));

    .age {
      color: $primary-300;
      font-size: 0.78rem;
      font-weight: 500;
      margin-bottom: $space-1;
    }

    .name {
      @include font-jakarta;
      @include ellipsis-overflow;
      color: white;
      font-size: 1.1em;
      font-weight: 600;
    }
  }
}
</style>
```

- [ ] **Step 2: Update ItemCardsCollection for CSS grid breakpoints**

Replace the `<style lang="scss" scoped>` block in `ItemCardsCollection.vue`:

```scss
<style lang="scss" scoped>
.ItemCardsCollection {
  .cards {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: $space-4;

    @media (min-width: 640px) {
      grid-template-columns: repeat(3, 1fr);
    }

    @media (min-width: 1024px) {
      grid-template-columns: repeat(4, 1fr);
    }
  }
}
</style>
```

Note: The JS-based `columnsCount` and `fontSize` bindings from the script are no longer used in CSS. The `v-bind` references in the old CSS are removed. The JS logic can remain (it's used for other things like the empty/loading states) but the grid now uses pure CSS media queries.

- [ ] **Step 3: Commit**

```bash
git add app/components/item/card/ItemCard.vue app/components/item/card/ItemCardsCollection.vue
git commit -m "style: rework ItemCard proportions and CSS grid breakpoints"
```

---

### Task 14: Rework ChatMessage Bubbles

**Files:**
- Modify: `app/components/chat/ChatMessage.vue`

- [ ] **Step 1: Update ChatMessage styles**

Replace the entire `<style scoped lang="scss">` block with:

```scss
<style scoped lang="scss">
.ChatMessage {
  --message-large-border-radius: $radius-lg;
  --message-small-border-radius: $space-1;

  @include flex-column;
  padding: $space-1 $space-4;
  padding-bottom: calc($space-1 + 2px);

  .bubble {
    @include flex-column;
    align-items: stretch;
    gap: $space-4;

    line-height: 1.35;
    max-width: 85%;
    min-width: 5rem;
    padding: $space-3 $space-4;
    position: relative;
    word-wrap: break-word;
    padding-bottom: $space-5;
    font-size: 0.95rem;

    :deep(.text) {
      @include flex-row;
      gap: $space-3;
      white-space: preserve wrap;

      svg {
        flex-shrink: 0;
      }
    }

    :deep(.buttons) {
      @include flex-row;
      gap: $space-4;

      & > * {
        flex: 1;
      }
    }
  }

  /* system messages */
  &[origin="system"] {
    .bubble {
      border: 1px solid $divider;
      align-self: center;
      color: $text-secondary;
      border-radius: $radius-sm;
      width: 70%;
    }
  }

  /* user messages */
  &[origin="me"],
  &[origin="interlocutor"] {
    .bubble {
      border-radius: $radius-lg;
      position: relative;
      box-sizing: border-box;
    }

    &:last-child {
      .bubble::after {
        content: ' ';
        width: 8px;
        height: 8px;
        border-radius: 50%;
        position: absolute;
        bottom: 0px;
      }
    }

    /* me */
    &[origin="me"] {
      .bubble {
        align-self: flex-end;
        background: $primary-text-safe;
        color: white;
      }

      &:has(~ div) {
        .bubble {
          border-bottom-right-radius: $space-1;
        }
      }

      &:not(:first-child) {
        .bubble {
          border-top-right-radius: $space-1;
        }
      }

      &:last-child {
        .bubble {
          border-bottom-right-radius: 0;
          &::after {
            background: $primary-text-safe;
            right: -4px;
          }
        }
      }
    }

    /* interlocutor */
    &[origin="interlocutor"] {
      .bubble {
        align-self: flex-start;
        background: #f0f0f0;
        color: $text-primary;
      }

      &:has(~ div) {
        .bubble {
          border-bottom-left-radius: $space-1;
        }
      }

      &:not(:first-child) {
        .bubble {
          border-top-left-radius: $space-1;
        }
      }

      &:last-child {
        .bubble {
          border-bottom-left-radius: 0;
          &::after {
            background: #f0f0f0;
            left: -4px;
          }
        }
      }
    }
  }

  .hour-and-check {
    @include flex-row;
    color: $text-tertiary;
    gap: $space-1;
    position: absolute;
    bottom: $space-1;
    right: $space-2;
    font-size: 0.7rem;
    white-space: nowrap;
  }
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add app/components/chat/ChatMessage.vue
git commit -m "style: rework chat bubbles — green on white, lighter interlocutor bg"
```

---

### Task 15: Rework Explore Page

**Files:**
- Modify: `app/pages/explore/index.vue`

- [ ] **Step 1: Read the current explore page**

Read `app/pages/explore/index.vue` fully to understand the current template and styles.

- [ ] **Step 2: Update explore page styles**

In the scoped styles, ensure:
- The page background uses `$bg-page`
- Card containers use `$bg-surface` (white) backgrounds with `$shadow-sm` and `$shadow-md` on hover
- The filter bar pills use neutral styling (gray bg, dark when active)
- Gaps use `$space-4` (16px)

The specific changes depend on the current explore page CSS. Apply the design tokens throughout.

- [ ] **Step 3: Commit**

```bash
git add app/pages/explore/index.vue
git commit -m "style: rework explore page with design tokens"
```

---

### Task 16: Rework Me Page and Saved Page

**Files:**
- Modify: `app/pages/me/index.vue`
- Modify: `app/pages/saved.vue`

- [ ] **Step 1: Read both pages**

Read `app/pages/me/index.vue` and `app/pages/saved.vue` to understand current styles.

- [ ] **Step 2: Update Me page styles**

Apply card-based layout for menu sections with `$bg-surface` cards, `$shadow-sm` resting shadow, `$radius-md` border radius. Use `$space-*` tokens for all spacing.

- [ ] **Step 3: Update Saved page empty state**

Ensure the empty state uses centered layout with `$space-16` vertical padding and a CTA button to explore.

- [ ] **Step 4: Commit**

```bash
git add app/pages/me/index.vue app/pages/saved.vue
git commit -m "style: rework Me and Saved pages with card layouts and design tokens"
```

---

### Task 17: Update nuxt.config.ts Theme Color and Gitignore

**Files:**
- Modify: `nuxt.config.ts`
- Modify: `../.gitignore`

- [ ] **Step 1: Update theme color to white**

In `nuxt.config.ts`, change the three `content: '#f6f7f6'` meta values to `content: '#ffffff'`:

```ts
meta: [
  { name: 'theme-color', content: '#ffffff' },
  { name: 'msapplication-navbutton-color', content: '#ffffff' },
  { name: 'apple-mobile-web-app-status-bar-style', content: '#ffffff' },
],
```

- [ ] **Step 2: Add `.superpowers/` to `.gitignore`**

Append `.superpowers/` to the root `.gitignore` if not already present:

```bash
echo ".superpowers/" >> /home/vianney/documents/projects/babytroc/.gitignore
```

- [ ] **Step 3: Commit**

```bash
git add nuxt.config.ts ../.gitignore
git commit -m "chore: update theme color to white, add .superpowers to gitignore"
```

---

### Task 18: Rework ImageGallery and ProgressiveImage

**Files:**
- Modify: `app/components/ui/ImageGallery.vue`
- Modify: `app/components/ui/ProgressiveImage.vue`

- [ ] **Step 1: Update ImageGallery styles**

Replace the `<style scoped lang="scss">` block in `ImageGallery.vue` with:

```scss
<style scoped lang="scss">
.ImageGallery {
  border-radius: $radius-lg;
  overflow: hidden;
  position: relative;

  img {
    display: block;
    width: 100%;
    height: 100%;
    aspect-ratio: 1;
    object-fit: cover;
  }

  .edit {
    @include flex-column-center;
    position: absolute;
    top: $space-4;
    right: $space-4;
    cursor: pointer;
    z-index: 2;
    aspect-ratio: 1;
    border-radius: 50%;

    @include hover-only {
      svg {
        filter: drop-shadow(0 0 12px rgba(255, 255, 255, 0.6));
      }
    }
  }

  .empty {
    @include flex-column-center;
    gap: $space-4;

    width: 100%;
    height: 100%;
    aspect-ratio: 1;
    background: $bg-page;

    color: $text-tertiary;
    font-size: 1rem;
    font-weight: 500;

    & > svg {
      width: 30%;
      height: 30%;
    }

    & > div {
      width: 40%;
      text-align: center;
    }
  }

  .carousel__slide {
    transition: opacity 200ms ease-out;
    aspect-ratio: 1;

    &:not(.carousel__slide--active) {
      opacity: 0.5;
    }
  }
}
</style>
```

- [ ] **Step 2: Update ProgressiveImage styles**

Replace the `<style scoped lang="scss">` block in `ProgressiveImage.vue` with:

```scss
<style scoped lang="scss">
img {
  transition: filter 300ms ease-out;
  filter: blur(0px);
  border-radius: $radius-lg;

  &.placeholder {
    filter: blur(12px);
  }
}
</style>
```

- [ ] **Step 3: Commit**

```bash
git add app/components/ui/ImageGallery.vue app/components/ui/ProgressiveImage.vue
git commit -m "style: rework ImageGallery and ProgressiveImage with rounded corners"
```

---

### Task 19: Rework Item Detail Page

**Files:**
- Modify: `app/pages/explore/item/[item_id].vue`

- [ ] **Step 1: Update Item Detail page styles**

Replace the `<style scoped lang="scss">` block with:

```scss
<style scoped lang="scss">
:deep(.Panel.desktop .content) {
  gap: $space-8;

  .name-description {
    h1 {
      margin: 0;
      font-size: 1.75rem;
      letter-spacing: -0.02em;
    }

    p {
      color: $text-secondary;
      line-height: 1.5;
    }
  }

  section {
    font-size: clamp(0.6em, 2vw, 1em);

    .ItemAge {
      color: $text-tertiary;
      font-style: italic;
    }

    .ItemRegionsList {
      font-size: clamp(0.6em, 1.4vw, 0.8em);
      padding: $space-8 0;
    }
  }
}

.LoadingAnimation {
  width: 100%;
  height: 10em;
}

/* Mobile-specific: description collapsible */
.name-description {
  .description {
    color: $text-secondary;
    line-height: 1.5;
  }
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add app/pages/explore/item/[item_id].vue
git commit -m "style: rework item detail page with design tokens"
```

---

### Task 20: Rework New Item (Creation Studio) Page

**Files:**
- Modify: `app/components/item/ItemEditionForm.vue`

- [ ] **Step 1: Read the current file**

Read `app/components/item/ItemEditionForm.vue` to understand current styles.

- [ ] **Step 2: Update styles**

In the scoped styles, apply:
- Form spacing: `$space-6` (24px) gap between field groups
- Image upload area: `border: 2px dashed #ddd`, `border-radius: $radius-lg`, `min-height: 200px`
- All inputs use the new token-based sizing from Task 6

The specific changes depend on the current ItemEditionForm CSS. Apply design tokens throughout.

- [ ] **Step 3: Commit**

```bash
git add app/components/item/ItemEditionForm.vue
git commit -m "style: rework creation studio form with design tokens"
```

---

### Task 21: Visual QA Pass

**Files:**
- All modified files from Tasks 1–20

- [ ] **Step 1: Start the dev server**

```bash
cd /home/vianney/documents/projects/babytroc/gui && npx nuxi dev
```

- [ ] **Step 2: Check each page visually**

Open the app in a browser and verify:
- Explore page: `$bg-page` background, white cards with shadow, refined card proportions
- Item detail: proper typography hierarchy, spacing
- Chat: green bubbles for own messages, light gray for others
- Me page: card-based sections
- Saved page: proper empty state
- Navigation: mobile bottom tabs clean with border, desktop nav with pill active state
- All buttons: pill-shaped, no bezel anywhere

- [ ] **Step 3: Check mobile viewport**

Use browser devtools to simulate a mobile viewport (375px width):
- Bottom tabs render correctly with safe area
- Drawer opens as bottom sheet
- Header bar is white with scroll shadow
- Page transitions work smoothly
- Touch feedback (opacity on :active) works

- [ ] **Step 4: Check contrast**

Verify with browser devtools accessibility checker:
- `$text-secondary` (#6a6a6a) on white: 5.7:1 (pass)
- `$text-tertiary` (#767676) on white: 4.5:1 (pass)
- Green button text (white on #527759): 4.6:1 (pass AA large)
- Chat bubble text (white on #3d6145): 5.8:1 (pass)

- [ ] **Step 5: Fix any issues found**

Address any visual inconsistencies, broken layouts, or contrast failures.

- [ ] **Step 6: Commit any fixes**

```bash
git add -u
git commit -m "fix: visual QA fixes for Airbnb-style redesign"
```
