# Airbnb-Style UI Redesign — Design Spec

**Date:** 2026-05-03
**Scope:** Full app redesign, component-first approach
**Goal:** Elevate Babytroc's UI to an Airbnb-level clean, airy, polished aesthetic while retaining the sage green brand identity. Responsive across desktop and mobile.

---

## 1. Design Tokens

### 1.1 Typography

Two font families (drop Instrument Sans):

| Role | Font | Weight | Size | Letter-spacing |
|------|------|--------|------|----------------|
| Display (page titles) | Plus Jakarta Sans | 700 | 1.75rem | -0.02em |
| Heading (section titles) | Plus Jakarta Sans | 600 | 1.25rem | -0.01em |
| Body | Inter | 400 | 0.95rem | 0 |
| Body strong | Inter | 600 | 0.95rem | 0 |
| Caption | Inter | 400 | 0.8rem | 0 |
| Label (tags, badges) | Inter | 500 | 0.78rem | 0 |

### 1.2 Spacing

4px base grid: `4, 8, 12, 16, 20, 24, 32, 40, 48, 64`

Mapped to Tailwind `space-1` through `space-16`.

### 1.3 Border Radius

Three standardized values:

- `sm`: 8px — inputs, tags, small elements
- `md`: 12px — cards, buttons
- `lg`: 16px — modals, drawers, image containers

Exception: CTA buttons use `border-radius: 2rem` (full pill).

### 1.4 Shadows

- `shadow-sm`: `0 1px 2px rgba(0,0,0,0.06)` — cards at rest
- `shadow-md`: `0 4px 12px rgba(0,0,0,0.08)` — cards on hover, dropdowns
- `shadow-lg`: `0 8px 24px rgba(0,0,0,0.12)` — modals, bottom sheets

### 1.5 Colors

**Sage green palette retained**, refined usage:

- Primary green `#527759` — CTAs and key interactive elements only
- Primary green (small text safe): `#3d6145` — ensures 5.8:1 contrast on white
- Page backgrounds: `#f7f7f7`
- Card/surface backgrounds: `#fff`
- Text primary: `#1a1a1a`
- Text secondary: `#6a6a6a` (5.7:1 on white)
- Text tertiary: `#767676` (4.5:1 on white — AA compliant)
- Dividers: `#ebebeb`
- Tag background: `#f7f7f7`, tag text: `#444`
- Active tag/filter: `#1a1a1a` bg, white text
- Error red: `#ef1313` (current palette)
- Info blue: `#3396d3` (current palette)

**Accessibility requirements:**
- All text: minimum 4.5:1 contrast ratio (WCAG AA)
- All interactive elements: minimum 3:1 contrast against adjacent colors (WCAG 2.1)
- Green on green-tinted backgrounds: verified >= 4.5:1

---

## 2. Base UI Components

### 2.1 TextButton

- Drop `bezel` aspect. Keep `flat` and `outline`.
- Flat primary: sage green bg, white text, `border-radius: 2rem` (pill)
- Outline: `1.5px` border, no fill, pill radius
- Hover (desktop only): subtle 5% darken, no scale transform
- Sizes: 36px (small), 40px (default), 48px (large)
- Loading: spinner replaces text, button width stays fixed

### 2.2 Tags / Badges

- Default: `#f7f7f7` bg, `#444` text, `border-radius: 2rem`, no border
- Active/selected: `#1a1a1a` bg, white text
- Green variant: reserved for status indicators only (e.g., "Disponible")

### 2.3 TextInput / SearchInput

- Border: `1px solid #ddd`, radius `sm` (8px)
- Focus: border transitions to `#1a1a1a` (not green)
- Height: 48px (generous touch target)
- SearchInput: `shadow-sm` at rest, `shadow-md` on focus

### 2.4 Slab (list item)

- Hover: `background: #f7f7f7` (subtle, no color)
- Padding: 16px vertical
- Chevron color: `#ccc`

### 2.5 Panel

- Max-width: 1200px
- Padding: 24px horizontal on desktop, 16px on mobile

### 2.6 Drawer / Overlay → Bottom Sheet (mobile)

**Mobile behavior (bottom sheet):**
- Slides up from bottom, `shadow-lg`
- Drag handle: 4px x 36px bar, centered, `#ddd`
- Rounded top corners: 16px (`lg`)
- Backdrop: `rgba(0,0,0,0.3)` + `blur(2px)`
- Drag-to-dismiss: dismiss when dragged > 40% of sheet height
- Snap points: half-screen (default), full-screen (long content)
- Animation: 300ms `cubic-bezier(0.32, 0.72, 0, 1)`

**Desktop behavior:**
- Side drawer or centered modal (keep current approach)

### 2.7 ImageGallery / ProgressiveImage

- Images: `border-radius: lg` (16px)
- Progressive loading: fade-in from LQIP, 300ms ease
- Full-screen gallery on mobile: see Section 4.2

### 2.8 ListEmpty / ListError / ListLoader

- Center-aligned, 80px+ vertical padding
- Softer icons, lighter text (`#6a6a6a`)
- Loader: pulse animation (not spinner)

---

## 3. Navigation

### 3.1 Mobile Bottom Tabs

- Height: 64px
- Top border: `1px solid #ebebeb` (no shadow)
- Icons: 24px Lucide, `#767676` inactive, `#1a1a1a` active
- Active tab: icon + label darken, weight 500 → 600. No colored indicator bar, no dot.
- Labels: 10px Inter, always visible
- Safe area: `padding-bottom: env(safe-area-inset-bottom)`

### 3.2 Desktop Side Nav

- White background
- Items: 14px Inter 500, `#6a6a6a` default, `#1a1a1a` active
- Active item: `#f7f7f7` background pill, no left border accent
- Icons: 20px, same color as text
- Notification badge: 8px red dot, no count
- Spacing: 8px gap between items, 48px item height

### 3.3 Mobile Header Bar

- White background, no shadow at rest
- Shadow appears on scroll (`shadow-sm`, triggered at scroll > 0)
- Title: Plus Jakarta Sans 600, 1.1rem, centered
- Back button: chevron-left, no background

---

## 4. Mobile Patterns

### 4.1 Bottom Sheets

- Used for: filters, item actions, confirmations, user menus
- Animation: slide up 300ms `cubic-bezier(0.32, 0.72, 0, 1)`
- Drag handle, snap points, backdrop dismiss as described in Section 2.6

### 4.2 Full-Screen Photo Gallery

- Black backdrop, fade-in 200ms
- Swipe horizontal between photos, pinch-to-zoom
- Close: X button top-right (white, 40px touch target) or swipe-down to dismiss
- Counter: "2 / 5" top-center, white text
- Dots: bottom-center, white active / `rgba(255,255,255,0.4)` inactive

### 4.3 Page Transitions

- Forward: slide in from right, 200ms
- Back: slide out to right, 200ms
- Tab switch: fade, 150ms
- Easing: `cubic-bezier(0.32, 0.72, 0, 1)` for all

### 4.4 Pull-to-Refresh

- Overscroll reveals sage green spinner
- Threshold: 60px pull distance
- Elastic snap-back animation
- Applied to: explore, saved, chats list

### 4.5 Touch Interactions

- Tap feedback: `opacity: 0.7` on `:active` (60ms)
- Hover effects scoped to desktop: `@media (hover: hover)`
- Minimum touch targets: 44px (WCAG)

---

## 5. Page Refinements

### 5.1 Explore

- Page background: `#f7f7f7`
- Cards: white bg, `shadow-sm` rest, `shadow-md` hover
- Card image: `border-radius: lg` top corners only
- Card spacing: 16px gap, 16px internal padding below image
- Filter bar: horizontal scroll of neutral pills, dark when active
- Loading: skeleton pulsing (not spinner)
- Grid: 2 col mobile, 3 col tablet, 4 col desktop (CSS grid, not device detection)
- Current card layout retained — refined proportions, spacing, typography

### 5.2 Item Detail

- Mobile: full-width image carousel at top (no border radius), swipe, dot indicators
- Desktop: image gallery left (60%), info right (40%), sticky on scroll
- Info: title, location, neutral tags, divider, user row with inline CTA
- "Emprunter" button: full-width sticky bottom (mobile), inline pill (desktop)
- Description: collapsible after 4 lines with "Voir plus"

### 5.3 Chat

- Message bubbles: own = `#3d6145` bg + white text (5.8:1 contrast), theirs = `#f0f0f0` + `#1a1a1a` text
- Bubble radius: 16px, tail corner 4px
- Input bar: sticky bottom, 48px height, `shadow-lg` above
- Timestamps: centered, `#767676`, shown between groups (>10min gap)

### 5.4 Profile / Me

- Card-based layout for menu sections
- Avatar: 80px, centered on mobile
- Stats row: items, loans, rating — horizontal, evenly spaced
- Menu items: refined Slab pattern

### 5.5 New Item (Creation Studio)

- Progress: thin bar at top (green fill), not numbered steps
- Image upload: dashed border `#ddd`, 16px radius, 200px height
- Form spacing: 24px between fields

### 5.6 Saved

- Same card grid as explore
- Empty state: centered illustration + "Pas encore de favoris" + CTA to explore

---

## 6. Implementation Strategy

**Approach: Component-first**

1. Update design tokens (SCSS variables, Tailwind config, CSS custom properties)
2. Rework base UI components (`app/components/ui/`)
3. Update layouts (`default.vue`, navigation components)
4. Refine page-by-page (explore → item detail → chat → profile → new item → saved)
5. Add mobile patterns (bottom sheet, full-screen gallery, pull-to-refresh)
6. Accessibility audit pass (contrast verification, touch targets, focus states)

**Technical notes:**
- Migrate responsive logic from `useDevice()` / `useNarrowWindow()` to CSS-based (`@media` queries, CSS grid) where possible for the explore grid. Keep device detection for behavioral differences (bottom sheet vs modal).
- Drop Instrument Sans font files and references.
- Add `.superpowers/` to `.gitignore`.
