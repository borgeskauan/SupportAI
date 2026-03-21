```markdown
# Design System Specification: The Precision Editorial Dashboard

## 1. Overview & Creative North Star
**Creative North Star: The Digital Curator**
This design system rejects the "standard dashboard" trope of cluttered boxes and heavy borders. Instead, it adopts an **Editorial High-Density** approach—drawing inspiration from the structural rigor of *Linear* and the spatial breathing room of *Notion*. 

We move beyond the template look by utilizing **Intentional Asymmetry** and **Tonal Layering**. The goal is a "back-office" tool that feels like a high-end productivity suite: trustworthy, hyper-efficient, and aesthetically quiet. We prioritize information density without sacrificing readability, using sophisticated surface transitions rather than rigid lines to guide the eye.

---

## 2. Colors & Surface Architecture
The palette is rooted in deep indigos and crisp neutrals, engineered to feel professional and authoritative.

### Surface Hierarchy & Nesting (The "No-Line" Rule)
To achieve a premium feel, **1px solid borders for sectioning are strictly prohibited.** Separation must be achieved through background shifts.
- **Base Layer:** `surface` (#faf8ff) is the canvas.
- **Secondary Workspace:** Use `surface-container-low` (#f2f3ff) for sidebars or utility panels.
- **Content Blocks:** Use `surface-container-lowest` (#ffffff) for the primary work area to make it "pop" with clean, paper-like clarity.
- **Nesting:** If a card must exist inside a workspace, use `surface-container-high` (#e2e7ff) to create a recessed, "milled" effect into the interface.

### The "Glass & Gradient" Rule
Floating elements (Modals, Command Palettes, Tooltips) must use **Glassmorphism**. Apply `surface_variant` at 80% opacity with a `20px` backdrop blur. This ensures the UI feels layered and deep rather than flat and "pasted on."

### Action & Status Tones
- **Primary Action:** `primary` (#4355b9). Use a subtle linear gradient from `primary` to `primary_dim` (#3649ac) for hero buttons to add "soul" and weight.
- **Review Needed:** `tertiary_fixed` (#f8a010) — A high-contrast amber that demands attention without the "danger" of red.
- **Draft:** `secondary_container` (#d5e3fc) — A soft, non-threatening blue.
- **Reviewed:** `on_secondary_fixed_variant` (#4e5c71) — Sophisticated slate-green.
- **Rejected:** `error_container` (#ff8b9a) — A subtle rose, avoiding harsh high-alert reds for internal workflows.

---

## 3. Typography: The Information Hierarchy
We use **Inter** exclusively. The "Editorial" feel comes from drastic scale shifts—large headlines paired with hyper-compact labels.

| Level | Token | Weight | Size | Tracking | Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Display** | `display-sm` | 600 | 2.25rem | -0.02em | Analytics Hero Numbers |
| **Headline** | `headline-sm` | 600 | 1.5rem | -0.01em | Page Titles |
| **Title** | `title-sm` | 500 | 1.0rem | 0 | Module Headers |
| **Body** | `body-md` | 400 | 0.875rem | 0 | Primary Data Points |
| **Label** | `label-sm` | 500 | 0.6875rem | +0.05em | Metadata & All-Caps Micro-labels |

**Editorial Note:** Always use `on_surface_variant` (#445d99) for secondary body text to reduce visual noise while maintaining legibility.

---

## 4. Elevation & Depth: Tonal Layering
Traditional drop shadows are too heavy for a high-density "Linear" aesthetic. We use **Ambient Shadows** and **Tonal Stacking**.

- **The Stacking Principle:** A card does not sit "on top" of a page; it is a "sheet" placed on a surface. Use `surface-container-lowest` on top of `surface-container` to create a natural lift.
- **Floating Shadows:** For popovers, use a shadow color of `on_surface` (#113069) at **4% opacity** with a `32px` blur and `8px` Y-offset. It should feel like a soft glow, not a dark smudge.
- **The "Ghost Border":** Where containment is vital (e.g., Input fields), use `outline_variant` (#98b1f2) at **20% opacity**. This provides a "suggestion" of a boundary that disappears into the clean aesthetic.

---

## 5. Components

### Compact Data Tables
*   **Structure:** No vertical lines. Use `0.9rem` (Spacing 4) vertical padding. 
*   **Row Hover:** Transition background to `surface_container_high` (#e2e7ff).
*   **Confidence Scores:** Use `percentage pills`. A background of `primary_container` (#dee0ff) with a foreground bar of `primary` (#4355b9) at `0.25rem` height.

### Buttons & Chips
*   **Primary Button:** `primary` background, `on_primary` text. Radius: `md` (0.375rem).
*   **Status Chips:** Use `label-sm` typography. Backgrounds should be the "fixed" variants (e.g., `tertiary_fixed_dim`) with 10% opacity for a soft, professional tint.
*   **Action Chips:** Borderless. Use `surface_container_highest` (#d9e2ff) only on hover.

### Input Fields
*   **State:** Default state is a "Ghost Border" (20% opacity `outline_variant`). 
*   **Focus:** Transition to 100% opacity `primary` with a 2px outer "halo" of `primary_container`.

### Cards & Lists
*   **Constraint:** Forbid divider lines between list items. Use `spacing-2` (0.4rem) of vertical white space to define rows.
*   **Detail View:** Use "Nested Layers." An open record should appear as a `surface-container-lowest` panel sliding over the `surface` background.

---

## 6. Do’s and Don’ts

### Do
*   **Do** use `label-sm` in all-caps for non-interactive metadata to create an architectural feel.
*   **Do** lean on the `surface-container` tiers to create hierarchy. If everything is white, nothing is important.
*   **Do** use asymmetric layouts (e.g., a wide main column and a narrow utility sidebar) to break the "grid" feel.

### Don't
*   **Don't** use pure black (#000) for text. Always use `on_surface` (#113069) to maintain the indigo-tinted professional tone.
*   **Don't** use standard `1px` borders to separate headers from content. Use a `spacing-px` height box with `surface_variant` color if a line is strictly required.
*   **Don't** use high-saturation reds for "Rejected" states. It creates unnecessary anxiety in a back-office tool; stick to the muted rose `error_container`.