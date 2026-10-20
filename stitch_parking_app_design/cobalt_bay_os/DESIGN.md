---
name: Cobalt Bay OS
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#434655'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#747686'
  outline-variant: '#c4c5d7'
  surface-tint: '#2151da'
  primary: '#0037b0'
  on-primary: '#ffffff'
  primary-container: '#1d4ed8'
  on-primary-container: '#cad3ff'
  inverse-primary: '#b7c4ff'
  secondary: '#565e74'
  on-secondary: '#ffffff'
  secondary-container: '#dae2fd'
  on-secondary-container: '#5c647a'
  tertiary: '#004b59'
  on-tertiary: '#ffffff'
  tertiary-container: '#006577'
  on-tertiary-container: '#75e3ff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dce1ff'
  primary-fixed-dim: '#b7c4ff'
  on-primary-fixed: '#001551'
  on-primary-fixed-variant: '#0039b5'
  secondary-fixed: '#dae2fd'
  secondary-fixed-dim: '#bec6e0'
  on-secondary-fixed: '#131b2e'
  on-secondary-fixed-variant: '#3f465c'
  tertiary-fixed: '#acedff'
  tertiary-fixed-dim: '#4cd7f6'
  on-tertiary-fixed: '#001f26'
  on-tertiary-fixed-variant: '#004e5c'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-lg:
    fontFamily: JetBrains Mono
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 20px
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 16px
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-lg: 1.5rem
  margin: 1.5rem
  margin-sm: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

## Brand & Style
The design system is engineered for high-throughput parking management, toll terminals, and multi-deck facility monitoring. It merges modern technical utility with executive clarity, serving two distinct personas: booth operators conducting rapid transactions under demanding lighting conditions, and facility managers reviewing occupancy yields, revenue velocity, and automation telemetry.

The visual style blends **Technical Minimalism** with **Structured Data Architecture**:
- Clean slate surfaces eliminate visual clutter and lower cognitive strain during 8-hour shifts.
- High-contrast status accents deliver unambiguous readability at a glance from distances over one meter.
- Tight grid alignment, mono-spaced identifiers, and distinct state indicators establish a durable, industrial-grade operational aesthetic.

## Colors
The color palette relies on an authoritative cobalt anchor complemented by high-signal functional states essential for parking logistics:

### Functional & Parking State Semantics
- **Primary Action & Navigation:** `#1D4ED8` (Cobalt Blue) with `#2563EB` for hover/interaction.
- **Available / Vacant Bay:** Emerald `#10B981` (Surface: `#ECFDF5`, Border: `#A7F3D0`).
- **Occupied Bay / Active Violation:** Crimson `#EF4444` (Surface: `#FEF2F2`, Border: `#FECACA`).
- **Reserved / Subscription:** Amber `#F59E0B` (Surface: `#FFFBEB`, Border: `#FDE68A`).
- **EV Charging Bay:** Electric Turquoise `#06B6D4` (Surface: `#ECFEFF`, Border: `#A5F3FC`).
- **Maintenance / Out-of-Service:** Slate Purple `#8B5CF6` or Muted Slate `#64748B`.

### Dark Mode & Low-Glare Operation
For control rooms and subterranean toll booths, surfaces invert to `#0F172A` (background canvas), `#1E293B` (panel surfaces), and `#334155` (structural borders), preserving semantic tokens with recalibrated luminance to avoid ocular fatigue.

## Typography
Typography is separated strictly by operational utility:
- **Headlines (`Plus Jakarta Sans`):** Clean, open letterforms that anchor screens, analytical widgets, and executive metrics.
- **Body & Data Tables (`Inter`):** Neutral, tall x-height sans-serif configured for numeric clarity (`tnum` tabular figures enabled by default across all financial and duration values).
- **Machine Identifiers & Codes (`JetBrains Mono`):** Dedicated to vehicle license plates (LPR), barcode/QR payloads, ticket UUIDs, and hardware bay coordinates (e.g., `BAY-L2-048`). This guarantees absolute distinction between ambiguous characters (`0` vs `O`, `1` vs `I`).

## Layout & Spacing
The layout model is optimized for desktop and industrial touchscreens (1280px to 4K displays):
- **Desktop Grid:** 12-column fluid grid system with `gutter-lg` (24px) for data dashboards and `gutter` (16px) for POS checkout screens.
- **Console Shell:** Fixed 240px collapsable navigation rail on the left, sticky operational top bar (holding active shift timers, gate connection health, and global plate search), and a dynamic multi-pane main work area.
- **Split-Screen Ergonomics:** POS and incident triage modes use a 60/40 split: the larger viewport renders live camera LPR feeds or interactive level maps, while the 40% panel hosts calculation tallies, receipt preview, and tender keys.
- **Rhythm:** Dense, standardized spacing based on 4px baseline increments. Dense states default to `space-xs` and `space-sm` to maximize visible table records without scrolling.

## Elevation & Depth
Depth conveys physical hierarchy without visual distraction:
- **Level 0 (Canvas):** Flat base neutral (`#F8FAFC` in light mode, `#0F172A` in dark mode).
- **Level 1 (Panels & Metric Cards):** Pure surface (`#FFFFFF` or `#1E293B`) framed by a crisp 1px border (`#E2E8F0` or `#334155`). Shadows are ultra-subtle (`0 1px 3px rgba(15, 23, 42, 0.05)`).
- **Level 2 (Interactive Bays & Dropdowns):** Subtle elevation (`0 4px 6px -1px rgba(15, 23, 42, 0.08)`), applied when hovering parking stalls or expanding rate schedules.
- **Level 3 (Modal Dialogs & Emergency Overrides):** Floating depth (`0 20px 25px -5px rgba(15, 23, 42, 0.15)`) accompanied by a 40% darkened neutral backdrop scrim to force immediate operator focus.

## Shapes
The system utilizes compact, precision-focused radius tokens (`roundedness: 1`):
- Standard controls (inputs, buttons, table rows) feature an exact `4px` (`0.25rem`) corner radius.
- Cards, data grids, and bay grid modules use `8px` (`0.5rem`).
- Status pills, badge indicators, and vehicle category identifiers use `9999px` full-pill geometries to create immediate distinction against rectangular data panels.
- Bay slots in spatial maps feature hard internal corners with softened exterior containment, reflecting actual painted architectural bays.

## Components

### 1. Bay Map Cell (Parking Space Visualizer)
- **Geometry:** 80x120px ratio block containing stall code (`label-sm`), state badge, elapsed time, and live plate thumbnail.
- **States:** Color-coded border top (4px accent): Emerald (Vacant), Crimson (Occupied), Amber (Reserved), Turquoise (EV Charging).
- **Interactivity:** Single click opens quick-action flyout (Force Gate Open, Assign Abonado, Re-classify Plate).

### 2. Rapid LPR Search Field
- **Structure:** 48px height input with a prominent optical scan icon, integrated clear action, and an inline keyboard shortcut tag (`⌘ + K` or `F2`).
- **Typography:** Uses `label-lg` uppercase mono characters with tracking.
- **Validation:** Live regex matching against local plate formats; returns instant floating preview matching vehicle make, color, and entry timestamp.

### 3. POS Billing & Breakdown Terminal
- **Layout:** Vertical summary card with tabular currency rows (Tariff tier, Stay duration, Tax, Grace period deduction).
- **Grand Total Display:** Oversized display (`32px` bold) in Cobalt Blue.
- **Payment Tender Bar:** Fixed keypad buttons with single-key shortcuts (`F9: Cash`, `F10: Card`, `F11: App/QR`).

### 4. Metric Cards (KPIs)
- Bordered Level 1 container. Top row: metric title (`body-sm` muted slate) and period badge. Middle: big value (`headline-lg`). Bottom: inline mini trend pill (`+4.2%` with directional arrow) paired with absolute stall counts (`412 / 500`).

### 5. Data Tables & Status Badges
- High-density rows (36px height) with light horizontal dividers (`#F1F5F9`).
- Status badges feature pastel tinted backgrounds with saturated text and a 6px status dot to guarantee accessibility for color-blind users.

### 6. Buttons & Interactive Controls
- **Primary:** Cobalt background (`#1D4ED8`), white text, crisp 4px radius, hover shift to `#2563EB`. Active state shifts 1px down.
- **Danger Override:** `#EF4444` solid fill reserved strictly for barrier open overrides and alarm silencing.
- **Form Inputs:** Monospaced inputs for technical codes; neutral outline with high-contrast 2px Cobalt focus ring.