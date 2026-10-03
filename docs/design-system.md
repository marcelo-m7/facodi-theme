# FACODI Design System — Tactile Academic Neobrutalism

> Status: **official visual source of truth for `theme_facodi`**
>
> Scope: FACODI Website, eLearning, curriculum surfaces, portal, editorial pages and reusable Website Builder components.
>
> Implementation name: **Campus Paper**  
> Visual direction: **Tactile Academic Neobrutalism**

This document defines how FACODI should look, feel and behave across public pages and learning interfaces. It exists to stop visual drift: new pages must reuse the same tokens and primitives, while existing pages and components should converge progressively toward this system.

The goal is not maximalist neobrutalism. FACODI adapts neobrutalist ideas to an academic product: strong outlines, tactile offset shadows, paper-like surfaces, bright annotation colors and explicit hierarchy, balanced by whitespace, readable typography and restrained motion.

---

## 1. Visual principles

Every FACODI screen should satisfy these principles.

### 1.1 One product, not a collection of pages

A learner moving between the homepage, Courses, Roadmaps, Curricular Units, Portal, Blog or Contact should recognise the same:

- typography;
- spacing rhythm;
- border weight;
- radius scale;
- card anatomy;
- button behaviour;
- metadata treatment;
- focus state;
- highlight language;
- responsive logic.

Do not create a page-specific design system.

### 1.2 Neobrutalism with academic restraint

Use:

- visible 1–2 px ink borders;
- small offset shadows;
- high-contrast actions;
- paper and graph-paper surfaces;
- compact mono labels for metadata;
- occasional highlighter/post-it treatments;
- simple geometric composition.

Avoid:

- giant black shadows everywhere;
- decorative chaos;
- unreadable rotations;
- excessive stickers;
- gradients as the primary visual language;
- glassmorphism;
- generic “AI startup” neon;
- animations that compete with learning content.

### 1.3 Content remains primary

Visual emphasis should explain information hierarchy, not replace it. Educational content, search, filters, navigation and progress must remain immediately understandable without animation.

### 1.4 Standard-first Odoo ownership

The theme owns presentation. It must not duplicate Odoo or FACODI business logic.

- Website owns pages, menus, translations and Website Builder state.
- `website_slides` owns courses, lessons, enrolment and learner progress.
- Portal owns authentication/account navigation.
- `facodi-learning` owns curriculum objects and learning-domain semantics.
- `theme_facodi` owns reusable visual patterns and focused QWeb presentation.

---

## 2. Naming

Use the following terminology consistently:

- **FACODI visual system** — the complete design system.
- **Tactile Academic Neobrutalism** — the visual direction.
- **Campus Paper** — the implementation vocabulary already used in SCSS and releases.
- **Paper primitive** — sheet, note, post-it or graph-paper surface.
- **Learning card** — course, roadmap, curricular-unit or resource card sharing the common FACODI card anatomy.

Do not invent additional theme names for individual pages.

---

## 3. Canonical color palette

The canonical implementation is in:

- `theme_facodi/static/src/scss/primary_variables.scss`
- `theme_facodi/static/src/scss/campus_paper_tokens.scss`

Do not hard-code new brand colors in page-specific SCSS when an existing token can express the role.

### 3.1 Core palette

| Token | Value | Role |
|---|---:|---|
| Ink | `#142846` | primary text, outlines, structural contrast |
| Ink Deep | `#0B1325` | deepest dark surface / dark-mode foundation |
| Paper | `#F9FAFB` | neutral page surface |
| Paper Warm | `#FDFCF7` | editorial/study paper surface |
| White | `#FFFFFF` | clean sheet/card surface |
| Cyan | `#37BED2` | discovery, interaction, supporting emphasis |
| Blue | `#3979C8` | institutional/academic structure |
| Mint | `#A7E8BE` | community, supportive/positive context |
| Sun | `#EFFF00` | primary CTA and highlighter accent |

### 3.2 Extended accents

| Token | Value | Use |
|---|---:|---|
| Sky | `#38BDF8` | secondary information accent |
| Coral | `#FF8A7A` | rare editorial annotation |
| Pink | `#FF70A6` | rare note/tape accent |
| Orange | `#FFAE33` | rare warning/editorial annotation |
| Success | `#107C41` | semantic success only |
| Error | `#BA1A1A` | semantic error only |

Extended accents are not interchangeable with the core palette. They should not become arbitrary section colors.

### 3.3 Highlighter palette

The Campus Paper highlighter aliases are:

- `--facodi-marker-yellow`
- `--facodi-marker-mint`
- `--facodi-marker-cyan`
- `--facodi-marker-pink`
- `--facodi-marker-orange`

Use marker colors for annotation, labels, tape or editorial emphasis — not for large page backgrounds.

### 3.4 Color hierarchy

Preferred hierarchy:

1. **Ink + Paper** provide structure.
2. **Sun** identifies the main action or one strong emphasis.
3. **Cyan / Blue / Mint** differentiate meaning.
4. Extended accents appear sparingly.

A page should not use every FACODI color at equal intensity.

### 3.5 Dark mode

Dark mode must use the native FACODI dark tokens in `campus_paper_tokens.scss`. Never implement dark mode by CSS inversion.

Dark surfaces should preserve:

- readable hierarchy;
- cyan structural border;
- visible focus rings;
- controlled Sun contrast;
- the same component anatomy as light mode.

Do not create light-only component variants.

---

## 4. Typography

Canonical stacks:

```css
--facodi-font-display: "Space Grotesk", Inter, "Segoe UI", sans-serif;
--facodi-font-body: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
--facodi-font-mono: "JetBrains Mono", SFMono-Regular, Menlo, Consolas, monospace;
```

### 4.1 Roles

**Display / Space Grotesk**
- H1–H3;
- wordmark;
- large statistics;
- strong editorial statements.

**Body / Inter**
- paragraphs;
- navigation;
- forms;
- explanations;
- learning content.

**Mono / JetBrains Mono**
- labels;
- metadata;
- badges;
- IDs/codes;
- technical/academic cues;
- small eyebrow text.

Do not use mono for long paragraphs.

### 4.2 Heading behaviour

Headings should:

- use compact line-height;
- wrap naturally;
- avoid forced line breaks except in controlled hero compositions;
- use `overflow-wrap` where user/content data can be long;
- preserve semantic H1 → H2 → H3 order.

Never reduce heading size simply to force text into a rigid card height.

---

## 5. Geometry

### 5.1 Borders

Canonical structural border:

```css
--facodi-border: 2px solid var(--facodi-ink);
```

Use 2 px for principal tactile components and 1 px for metadata dividers or secondary boundaries.

Do not mix 1 px, 2 px, 3 px and 4 px borders arbitrarily on equivalent components.

### 5.2 Radius scale

Use the existing token scale:

| Role | Token |
|---|---|
| tiny annotation | `--facodi-radius-sm` |
| standard control | `--facodi-radius` |
| larger sheet | `--facodi-radius-lg` |
| tag | `--facodi-radius-tag` |
| button | `--facodi-radius-btn` |
| card | `--facodi-radius-card` |
| panel | `--facodi-radius-panel` |
| hero | `--facodi-radius-hero` |
| pill | `--facodi-radius-pill` |

Do not add a new radius value in a page stylesheet before checking these tokens.

### 5.3 Shadows

Neobrutalist depth is created by **offset shadows**, not blur-heavy elevation.

Canonical family:

- small: 2 px;
- button: 3 px;
- card: 4 px;
- strong/featured: 6 px.

Use one shadow direction consistently.

Interactive components may compress the shadow on press or increase it slightly on hover, but should not glow unless the interaction explicitly calls for a spotlight treatment.

### 5.4 Rotation

Small rotations are allowed only for note/post-it metaphors. Use them sparingly and remove them on small screens or reduced-motion contexts when they compromise reading.

Never rotate primary navigation, forms, course cards or dense academic data.

---

## 6. Spacing and layout

Base spacing tokens:

- `--facodi-space-xs`: 0.25rem
- `--facodi-space-sm`: 0.5rem
- `--facodi-space-md`: 1rem
- `--facodi-space-lg`: 1.5rem
- `--facodi-space-xl`: 2rem

Section-level spacing may use responsive `clamp()`, but internal component spacing should stay aligned to this rhythm.

### Layout rules

- Use `min-width: 0` on grid/flex children that contain dynamic text.
- Use CSS Grid for card catalogues and dense learning layouts.
- Avoid fixed widths for translated text.
- Avoid fixed heights for content cards unless the content is strictly constrained.
- Keep page-level horizontal overflow at zero.
- Tables may scroll internally on narrow screens; pages may not.

Target acceptance widths:

- 1440 px desktop;
- 1024 px tablet;
- 390 px mobile;
- 320 px minimum safety gate.

---

## 7. Paper primitives

Reuse the primitives from `paper_primitives.scss`.

### `.facodi-paper`

Base editorial/page surface.

### `.facodi-grid-paper` / `.facodi-grid-matrix`

Graph-paper background for learning context, hero support or restrained visual zones.

Do not put graph paper behind every section.

### `.facodi-sheet`

Canonical white/paper panel with structural border and offset shadow.

Use for:
- reference panels;
- form framing;
- metadata panels;
- curriculum blocks;
- structured editorial content.

### `.facodi-note`

Mint study note. Use for supportive context, tips or community framing.

### `.facodi-postit`

Sun annotation. Use for one small high-attention note, never as the default card style.

### `.facodi-highlight` / marker utilities

Use to simulate academic highlighter emphasis within headings or short phrases. Do not highlight full paragraphs.

---

## 8. Canonical components

Before writing a new component, verify whether one of these families already solves the problem.

### 8.1 Buttons

Use:

- `.facodi-button`
- `.facodi-button-primary`
- `.facodi-button-secondary`
- standard Odoo/Bootstrap `.btn*` where native behaviour owns the control.

Primary:
- Sun background;
- Ink text/border;
- tactile offset shadow.

Secondary:
- paper/white surface;
- Ink border;
- Mint hover.

Rules:
- one primary CTA per local action group;
- minimum touch target around 44 px;
- do not create page-specific button colors;
- never remove focus indication.

### 8.2 Cards

Base class:

```text
.facodi-card
```

Semantic variants:

- `.facodi-card--learning` → Cyan accent;
- `.facodi-card--resource` → Mint accent;
- `.facodi-card--institutional` → Blue accent;
- `.facodi-card--editorial` → Sun accent.

Equivalent cards should share:
- border;
- radius;
- shadow;
- title hierarchy;
- metadata location;
- CTA placement;
- focus/hover behaviour.

Variation comes from semantic accents and content, not a completely new card design.

### 8.3 Badges and labels

Use:
- `.facodi-badge`;
- `.facodi-badge--sun`;
- `.facodi-badge--mint`;
- `.facodi-badge--cyan`;
- `.facodi-badge--pill`;
- `.facodi-label`;
- `.facodi-tab`.

Badge text should be short. Academic codes and metadata are ideal candidates.

Do not use badges as decorative confetti.

### 8.4 Links

Use `.facodi-text-link` for compact editorial/action links.

Regular paragraph links should remain normal accessible links and not be forced into the mono-uppercase treatment.

### 8.5 Forms

Preserve native Odoo Website form mechanics.

Visual rules:
- 2 px or controlled high-contrast borders;
- consistent radius;
- clear label;
- explicit error state;
- visible focus;
- no placeholder-only labels;
- no page-specific form theme.

### 8.6 Navigation

Header, dropdown and mobile navigation must reuse Odoo Website/Portal ownership.

The FACODI visual layer may style and compose the desktop header, but must not create a parallel authentication or menu system.

Navigation should remain shallow:

- Explore;
- Learn;
- Community;
- Project;
- Search/language/account utilities;
- Contribute CTA.

Deep content belongs in dropdowns/mega menus or landing hubs, not as dozens of top-level items.

### 8.7 Footer

The footer is part of the global shell and must use the same:
- border language;
- typography;
- link treatment;
- spacing;
- semantic color system.

Do not build page-specific footers.

---

## 9. Homepage rules

The homepage is the strongest expression of the visual system and should not introduce one-off patterns that cannot be reused elsewhere.

Preferred structure:

1. Header
2. Hero
3. Discovery/Search
4. Courses / Roadmaps / Curricular Units / Resources entry grid
5. Featured or Continue Learning
6. Knowledge-with-context explanation
7. Subject areas
8. Discover → Learn → Contribute
9. Real metrics
10. Community
11. Partners & Network
12. Editorial/news
13. Final CTA
14. Footer

### Hero

The hero should express **“open digital campus”**, not generic SaaS marketing.

Allowed:
- graph/dot-grid visual;
- one text entrance animation;
- one subtle tactile CTA interaction;
- small knowledge-graph metaphor.

Avoid:
- huge decorative 3D objects;
- large gradients;
- full-screen particle overload;
- multiple competing animations.

---

## 10. Motion and React Bits-style effects

Interactive effects are progressive enhancement. FACODI must remain understandable and usable when they do not run.

Recommended families for FACODI:

- Dot Grid → hero/background knowledge field;
- Split/Staggered text → one hero heading entrance;
- Magnet → one primary CTA;
- Bento → Explore entry layout;
- Spotlight → selected featured cards only;
- Count Up → real metrics only;
- Scroll Reveal → major storytelling milestones.

### Odoo implementation rule

Do **not** introduce a React application just to reproduce a React Bits effect.

Prefer:
1. extract the interaction principle;
2. implement it with scoped CSS/vanilla JS/Odoo frontend infrastructure;
3. reuse FACODI tokens;
4. keep semantic QWeb content rendered server-side;
5. support `prefers-reduced-motion`;
6. ensure the page remains complete without JavaScript.

Existing progressive-enhancement files such as `facodi_dot_grid.js` and `facodi_home_motion.js` should remain small and presentation-only.

Do not let visual JS:
- call Odoo RPC for business actions;
- mutate progress/completion;
- own navigation;
- hide SEO content;
- duplicate Supabase/Odoo domain logic.

---

## 11. Accessibility

Minimum target: WCAG 2.2 AA intent, with explicit testing rather than visual assumptions.

Required:
- visible `:focus-visible`;
- keyboard-accessible menus and disclosure controls;
- 44 px touch targets where practical;
- semantic landmarks/headings;
- labels for form controls;
- sufficient contrast;
- no information communicated only by color;
- `prefers-reduced-motion`;
- accessible link/button semantics;
- no page-level horizontal overflow at 320 px.

Neobrutalism does not justify inaccessible contrast or noisy focus states.

---

## 12. Internationalization

English remains the canonical QWeb source language; PT/ES/FR use native Odoo translations.

Design for translation expansion:
- no fixed-width navigation labels;
- no fixed-height text blocks;
- cards must tolerate longer titles;
- CTA labels must wrap safely;
- metadata rows must flex/wrap.

Never hard-code a language-specific duplicate of a visual component.

---

## 13. Existing-page convergence plan

This table is the official visual-refactor checklist. It does not imply every route is currently broken; it defines the surfaces that must be checked and brought into the same system.

| Priority | Surface | Cohesion target |
|---|---|---|
| P0 | Global header / desktop navigation | one menu hierarchy, canonical buttons, dropdowns, account/language treatment |
| P0 | Mobile header/navigation | native Odoo ownership, clear hierarchy, no desktop menu squeezed into mobile |
| P0 | Homepage hero | canonical hero composition, tokens, search/discovery, restrained motion |
| P0 | Homepage cards/entry grid | one card family for Courses/Roadmaps/UCs/Resources |
| P0 | Global footer | same typography, spacing, link and disclosure language |
| P1 | `/courses` / `/slides` catalogue | shared learning-card anatomy, filters, empty/loading states |
| P1 | Course detail / Study Player | Campus Paper study shell, metadata hierarchy, native progress/action semantics |
| P1 | Roadmaps | same learning-card/pathway vocabulary |
| P1 | Curricular Units | same card/reference-sheet vocabulary, academic-boundary copy retained |
| P1 | `/my/home` Portal | student-desk treatment using shared cards, labels and actions |
| P1 | Contact/submission forms | standard forms + FACODI framing, contextual metadata preserved |
| P2 | About / Manifesto / How / Contribution | shared editorial sheet, timeline, quote and CTA primitives |
| P2 | Partners & Network | institutional card family; no one-off partner microsites |
| P2 | Blog/news | Campus Bulletin editorial language, native Blog ownership |
| P2 | Error/empty states | shared paper-note vocabulary and CTA hierarchy |

### Refactor sequence

When correcting an inconsistent page:

1. identify the existing FACODI/Odoo primitive that should own the pattern;
2. replace local hard-coded values with tokens;
3. consolidate duplicate markup/classes;
4. preserve standard Odoo mechanics;
5. test desktop + tablet + mobile;
6. test keyboard focus and reduced motion;
7. test translated strings;
8. remove superseded local styles;
9. add/update a contract test when the pattern is reusable.

Do not “fix” visual inconsistency by adding another `*-fix.scss` layer.

---

## 14. Anti-patterns

Do not introduce:

- new hard-coded brand colors in page SCSS;
- arbitrary border-radius values;
- multiple card systems for equivalent content;
- blurred SaaS shadows;
- glass panels;
- large decorative gradients;
- page-specific header/footer implementations;
- duplicate authentication controls;
- custom mobile menus when Odoo already owns the behaviour;
- business-data queries inside theme QWeb;
- fake counts, testimonials, instructors or academic claims;
- hard-coded progress;
- hidden content that only appears after animation;
- React/runtime dependencies solely for decorative effects;
- `!important` as the normal way to win specificity;
- monolithic “final-fix” stylesheets.

---

## 15. Component authoring checklist

Before merging a new visual component, answer **yes** to all applicable checks:

- [ ] Uses existing FACODI color tokens.
- [ ] Uses the radius/shadow scale.
- [ ] Reuses a canonical card/sheet/button primitive where possible.
- [ ] Works in light and dark theme.
- [ ] Works at 1440 / 1024 / 390 / 320 px.
- [ ] Has no page-level horizontal overflow.
- [ ] Has visible keyboard focus.
- [ ] Does not rely on hover to expose essential information.
- [ ] Respects reduced motion.
- [ ] Allows translated text to expand.
- [ ] Does not duplicate Odoo/FACODI business logic.
- [ ] Does not invent data.
- [ ] Is editable through Website Builder when it represents editorial content.
- [ ] Keeps native Odoo links/forms/actions intact when styling standard surfaces.

---

## 16. Definition of done for a refactored page

A page is visually complete only when:

1. its components look like members of the same FACODI family;
2. no local color/radius/shadow system competes with the canonical tokens;
3. the page has a clear primary action and information hierarchy;
4. mobile is intentionally composed, not merely stacked;
5. keyboard focus and reduced motion work;
6. long and translated content remain contained;
7. native Odoo functionality is preserved;
8. empty/partial/error states look intentional;
9. no fake learning or institutional data is introduced;
10. the relevant repository contracts and integrated browser gate pass.

---

## 17. Source files and ownership

### Tokens
- `theme_facodi/static/src/scss/primary_variables.scss`
- `theme_facodi/static/src/scss/campus_paper_tokens.scss`

### Primitives
- `theme_facodi/static/src/scss/paper_primitives.scss`
- `theme_facodi/static/src/scss/components.scss`

### Surface layers
- `theme_facodi/static/src/scss/snippets.scss`
- `theme_facodi/static/src/scss/website.scss`
- `theme_facodi/static/src/scss/website_slides.scss`
- `theme_facodi/static/src/scss/website_slides_player.scss`
- `theme_facodi/static/src/scss/curriculum.scss`
- `theme_facodi/static/src/scss/portal.scss`
- `theme_facodi/static/src/scss/editorial_interfaces.scss`
- `theme_facodi/static/src/scss/website_blog.scss`
- `theme_facodi/static/src/scss/website_public.scss`

### Global shell
- `theme_facodi/views/header.xml`
- `theme_facodi/views/customizations.xml`

### Reusable Website Builder blocks
- `theme_facodi/views/snippets/`
- `theme_facodi/views/snippets/components/`

Architecture boundaries remain defined in `docs/architecture.md`; release evidence remains defined in `docs/validation.md`.

---

## 18. Governing rule

When deciding between a visually impressive one-off implementation and a slightly simpler reusable FACODI pattern, choose the reusable pattern.

**FACODI should feel expressive because its system is coherent — not because every page invents a new visual trick.**
