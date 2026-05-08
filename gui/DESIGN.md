---
name: Babytroc
description: La plateforme lausannoise de pret d'articles pour enfants entre particuliers
colors:
  sage-garden: "#527759"
  sage-garden-safe: "#3d6145"
  sage-garden-light: "#729577"
  morning-dew: "#f3f6f4"
  morning-dew-mid: "#e1eae1"
  hedge-mist: "#c4d6c5"
  meadow-grey: "#88a98c"
  porch-light: "#f7f7f7"
  linen-surface: "#f6f7f6"
  deep-loam: "#1a1a1a"
  worn-stone: "#6a6a6a"
  faded-path: "#767676"
  soft-divider: "#ebebeb"
  fence-line: "#dddddd"
  alert-red: "#dc2626"
  quiet-blue: "#3b82f6"
  chat-received: "#f0f0f0"
typography:
  display:
    fontFamily: "Plus Jakarta Sans, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Plus Jakarta Sans, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Inter, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
  label:
    fontFamily: "Inter, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: "normal"
  caption:
    fontFamily: "Inter, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: "normal"
rounded:
  sm: "8px"
  md: "12px"
  lg: "16px"
  pill: "2rem"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  2xl: "48px"
  3xl: "64px"
components:
  button-primary:
    backgroundColor: "{colors.sage-garden}"
    textColor: "{colors.morning-dew}"
    rounded: "{rounded.pill}"
    padding: "12px 24px"
  button-primary-hover:
    backgroundColor: "{colors.sage-garden-safe}"
    textColor: "{colors.morning-dew}"
    rounded: "{rounded.pill}"
    padding: "12px 24px"
  button-outline:
    backgroundColor: "transparent"
    textColor: "{colors.deep-loam}"
    rounded: "{rounded.pill}"
    padding: "12px 24px"
  button-outline-hover:
    backgroundColor: "{colors.porch-light}"
    textColor: "{colors.deep-loam}"
    rounded: "{rounded.pill}"
    padding: "12px 24px"
  input-default:
    backgroundColor: "{colors.linen-surface}"
    textColor: "{colors.deep-loam}"
    rounded: "{rounded.sm}"
    height: "48px"
    padding: "0 16px"
  chip-default:
    backgroundColor: "{colors.porch-light}"
    textColor: "{colors.worn-stone}"
    rounded: "{rounded.pill}"
    padding: "8px 16px"
  chip-active:
    backgroundColor: "{colors.deep-loam}"
    textColor: "{colors.porch-light}"
    rounded: "{rounded.pill}"
    padding: "8px 16px"
  card-surface:
    backgroundColor: "{colors.linen-surface}"
    rounded: "{rounded.md}"
    padding: "16px"
  slab-item:
    backgroundColor: "{colors.linen-surface}"
    textColor: "{colors.deep-loam}"
    rounded: "{rounded.md}"
    height: "56px"
    padding: "0 16px"
  nav-tab-active:
    backgroundColor: "{colors.morning-dew}"
    textColor: "{colors.sage-garden-safe}"
    rounded: "{rounded.sm}"
    padding: "10px 16px"
---

# Design System: Babytroc

## 1. Overview

**Creative North Star: "The Porch Exchange"**

Babytroc feels like handing a stroller over the porch railing to a neighbor you trust. Every surface carries the informal warmth of a shared space between families: not a storefront, not a transaction counter, but someone's front porch on a mild afternoon. The light is natural, the materials are honest, and nothing demands attention that doesn't deserve it.

The system rejects the cold efficiency of generic marketplaces (Leboncoin, Amazon), the metric-driven density of SaaS dashboards, and the sterile flatness of AI-generated minimalism. It also avoids the bright, cartoonish aesthetic of children's retail. The users are adults sharing within a community; the interface respects that.

Warmth comes from tinted neutrals, generous but varied spacing, and typography that feels handpicked rather than defaulted. Every interaction, from browsing items to starting a chat, should carry the same low-pressure friendliness of a neighbor saying "take your time, bring it back whenever."

**Key Characteristics:**
- Sage-tinted neutrals that feel organic, never clinical
- Pill-shaped actions that invite touch without shouting
- Ambient depth through soft shadows, never hard edges
- Two-font pairing: geometric headings (Plus Jakarta Sans) grounded by a workhorse body (Inter)
- Mobile-first rhythm designed for one-handed, distracted use

## 2. Colors

A restrained palette anchored by a single sage green, surrounded by warm neutrals that carry just enough tint to feel alive.

### Primary

- **Sage Garden** (#527759): The identity color. Used for primary buttons, active navigation states, and key interactive affordances. Present but never dominant; it earns trust through restraint, not saturation.
- **Sage Garden Safe** (#3d6145): The accessible sibling (5.8:1 on white). Used for text set against light backgrounds, chat bubbles from the current user, and anywhere green must meet AA contrast on white.
- **Sage Garden Light** (#729577): Hover and secondary emphasis states. Lighter touch for less critical green accents.

### Neutral

- **Morning Dew** (#f3f6f4): The lightest green tint. Active backgrounds behind navigation, subtle highlight for selected states. Not a page background; a signal that something is gently active.
- **Morning Dew Mid** (#e1eae1): Slightly stronger green tint for borders and dividers within green-context areas.
- **Hedge Mist** (#c4d6c5): Mid-tone green-grey. Secondary text within green panels, disabled green states.
- **Meadow Grey** (#88a98c): The bridge between green and neutral. Placeholder text in green contexts, muted icons.
- **Porch Light** (#f7f7f7): Page background. Warm enough to distinguish from pure white surfaces, neutral enough to disappear. The porch itself.
- **Linen Surface** (#f6f7f6): Card and input backgrounds. Nearly identical to Porch Light but with a faint green lean that ties surfaces to the brand.
- **Deep Loam** (#1a1a1a): Primary text. Rich near-black with enough warmth to avoid harshness.
- **Worn Stone** (#6a6a6a): Secondary text. Descriptions, timestamps, supporting copy.
- **Faded Path** (#767676): Tertiary text. Hints, disabled labels, the quietest readable tone.
- **Soft Divider** (#ebebeb): Horizontal rules and section separators.
- **Fence Line** (#dddddd): Input borders and card outlines at rest.

### Semantic

- **Alert Red** (#dc2626): Destructive actions and error states only. Never decorative.
- **Quiet Blue** (#3b82f6): Informational accents and secondary interactive states. Rare.
- **Chat Received** (#f0f0f0): Incoming message bubbles. Neutral enough to stay in the background.

### Named Rules

**The Porch Rule.** Sage Garden appears on no more than 10% of any screen. Its rarity makes it meaningful. When everything is green, nothing is.

**The No Pure White Rule.** Neither #000 nor #fff appears anywhere. Every surface and every text color carries a faint tint, warm or green, that keeps the palette cohesive.

## 3. Typography

**Display Font:** Plus Jakarta Sans (with system sans-serif fallback)
**Body Font:** Inter (with system sans-serif fallback)

**Character:** Plus Jakarta Sans brings geometric confidence to headings without feeling corporate; its slightly rounded terminals echo the pill shapes used throughout the UI. Inter handles everything else with quiet competence: highly legible at small sizes, neutral enough to disappear into content, distinctive enough to feel chosen.

### Hierarchy

- **Display** (700, 1.75rem/28px, line-height 1.2, tracking -0.02em): Page titles and primary headings. Plus Jakarta Sans. One per screen, maximum.
- **Headline** (600, 1.25rem/20px, line-height 1.3, tracking -0.01em): Section headings, card titles, modal headers. Plus Jakarta Sans. The workhorse heading level.
- **Body** (400, 0.95rem/15px, line-height 1.5): All running text, descriptions, chat messages. Inter. Capped at 65-75ch line length for readability.
- **Label** (500, 0.8125rem/13px, line-height 1.4): Form labels, metadata, timestamps, button text. Inter. Weight 500 distinguishes from body without shouting.
- **Caption** (400, 0.75rem/12px, line-height 1.4): Fine print, helper text beneath inputs, tertiary metadata. Inter. The quietest level; use sparingly.

### Named Rules

**The Two-Voice Rule.** Plus Jakarta Sans speaks for structure (headings, navigation labels). Inter speaks for content (body, inputs, metadata). They never swap roles. Mixing them within the same hierarchy level is forbidden.

**The Scale Jump Rule.** Adjacent hierarchy levels maintain at least a 1.25x size ratio. Flat scales (16/15/14) make everything look the same. The jumps (28 to 20 to 15 to 13 to 12) are deliberate.

## 4. Elevation

Babytroc uses ambient shadows: gentle, diffuse, suggesting objects resting on a surface rather than floating above it. Depth is a whisper, not a statement. Most elements sit flat; shadows appear only when an element needs to feel liftable or when a layer genuinely overlaps another (dropdowns, drawers).

### Shadow Vocabulary

- **Subtle** (`0 1px 2px rgba(0,0,0,0.06)`): Cards at rest, input fields. Barely visible; just enough to separate surface from background. The default elevation.
- **Medium** (`0 4px 12px rgba(0,0,0,0.08)`): Hover states on cards, floating action elements. A gentle lift that says "this responds to you."
- **Prominent** (`0 8px 24px rgba(0,0,0,0.12)`): Dropdowns, drawers, overlays. Reserved for elements that genuinely float above the page. The maximum depth in the system.

### Named Rules

**The Flat-By-Default Rule.** Surfaces are flat at rest. Shadows appear only as a response to state (hover, focus, overlay) or genuine layering (dropdown over content). If an element doesn't move or overlap, it doesn't shadow.

## 5. Components

### Buttons

Soft and reassuring. Pill-shaped by default, sized for comfortable one-handed tapping.

- **Shape:** Fully rounded ends (pill, 2rem radius). Never squared, never subtly rounded.
- **Primary (flat):** Sage Garden background, Morning Dew text. Padding varies by size: small (8px 16px, 36px height), normal (10px 20px, 40px height), large (14px 28px, 48px height).
- **Hover:** Background shifts to Sage Garden Safe. Transition on background (200ms ease).
- **Outline:** Transparent background, Deep Loam text, Fence Line border (1px). Hover fills with Porch Light.
- **Disabled / Loading:** Opacity 0.5. Loading state shows inline spinner replacing text.
- **Touch feedback:** On touch devices, `:active` drops opacity to 0.7 (60ms) for immediate tactile response.

### Chips / Tags

Filter pills and category tags. Same pill shape as buttons but lighter presence.

- **Default:** Porch Light background, Worn Stone text. No border.
- **Active:** Deep Loam background, Porch Light text. The inversion signals selection clearly.
- **Transition:** Background and color shift (200ms ease).

### Cards / Containers

- **Corner style:** Gently curved (12px radius). Enough softness to feel friendly, not so much it feels bubbly.
- **Background:** Linen Surface (#f6f7f6) or white, depending on context.
- **Shadow:** Subtle at rest. Medium on hover when the card is interactive (item cards in the grid).
- **Border:** None by default. Fence Line (1px) only when the card sits on a same-color background and needs separation.
- **Internal padding:** 16px standard. 12px for compact contexts (chat bubbles, small metadata cards).

### Inputs / Fields

- **Style:** Linen Surface background, Fence Line border (1px), gently curved (8px radius). Height 48px for comfortable touch targets.
- **Focus:** Border shifts to Sage Garden. No glow, no ring; the color change alone signals focus.
- **Error:** Border shifts to Alert Red. Warning icon appears inline (right side).
- **Disabled:** Opacity reduction, no interaction.
- **States:** Idle, pending (inline spinner), success (green checkmark), error (red triangle + red border).

### Navigation

- **Desktop sidebar:** Vertical tab list. Logo at top (Plus Jakarta Sans, weight 200, ~1.5rem). Tabs below as rounded rectangles (8px radius). Active tab: Morning Dew background, Sage Garden Safe text. Inactive: no background, Worn Stone text.
- **Mobile footer:** Horizontal tab bar pinned to bottom with safe-area inset. Same active/inactive treatment, icon + label per tab.
- **Transitions:** Background color fade (200ms).

### Slab (Signature Component)

A horizontal action row used throughout the "Me" section: icon on the left, title centered, optional badge and chevron on the right. Functions as a list item and navigation trigger.

- **Shape:** Gently curved (12px radius), 56px height.
- **Background:** Linen Surface. Hover shifts to Porch Light.
- **Internal layout:** Icon (20px, Worn Stone) with 16px left padding, title (Label weight, Deep Loam), chevron (16px, Faded Path) flush right.
- **Badge:** Small red dot or count, positioned before the chevron.

## 6. Do's and Don'ts

### Do:

- **Do** tint every neutral toward sage green (chroma 0.005-0.01 in OKLCH). Pure greys feel clinical; the green lean ties the whole palette to the brand.
- **Do** use pill shapes for all interactive affordances (buttons, chips, search input). The consistent rounded form is part of the identity.
- **Do** vary spacing for rhythm. Tighter grouping within related content (8-12px), generous breathing room between sections (32-48px). Same padding everywhere is monotony.
- **Do** design every touch target at 44px minimum height. Parents tap with one thumb while holding a child.
- **Do** use the spring easing curve (`cubic-bezier(0.32, 0.72, 0, 1)`) for transitions that should feel responsive and organic.
- **Do** keep body text at 65-75ch line length on desktop. Let it run full-width on mobile.

### Don't:

- **Don't** make it look like a generic marketplace. No product grids with price tags, no "Add to Cart" language, no seller ratings. Babytroc is about sharing, not selling. (From PRODUCT.md: "Generic marketplaces (Amazon, eBay, Leboncoin): transactional, cold, impersonal.")
- **Don't** add SaaS patterns: dashboards, metrics cards, upsell banners, progress bars toward goals. This is a community tool, not a business tool. (From PRODUCT.md: "Corporate SaaS: dashboards, metrics, upsell banners, empty productivity aesthetics.")
- **Don't** flatten the design into sterile AI minimalism. Every surface should have texture: a tinted background, a considered shadow, a deliberate type choice. If it looks like a wireframe with color, it's too minimal. (From PRODUCT.md: "AI-generated minimalism: the sterile, flattened, over-simplified look that strips away personality.")
- **Don't** use bright primary colors, cartoonish illustrations, or playful display fonts. The users are adults. (From PRODUCT.md: "Children's toy store aesthetic.")
- **Don't** use `border-left` or `border-right` greater than 1px as a colored accent stripe on any element.
- **Don't** use gradient text (`background-clip: text` with gradient).
- **Don't** nest cards inside cards. If a card contains structured content, use spacing and dividers, not inner cards.
- **Don't** use `#000` or `#fff` anywhere. Every extreme should carry tint.
- **Don't** reach for a modal as the first solution. Inline expansion, drawers, and progressive disclosure come first.
