# FACODI Campus Paper Visual System — Design Specification

Date: 2026-09-25  
Repository: `marcelo-m7/facodi-theme`  
Target module: `theme_facodi`  
Branch: `design/facodi-campus-paper`  
Status: approved direction (Option B), written specification pending user review

## 1. Purpose

Refactor the FACODI visual identity and homepage around a reusable Odoo-native design system inspired by the approved Stitch direction and the supplied FACODI visual references.

The target experience is not a generic education website and not a literal copy of the Stitch prototype. It should feel like an open digital campus built from the visual language of study: paper, grids, notebooks, highlighters, sticky notes, labels, tabs, handwritten annotations, course cards, learning routes and public collaboration.

The design system must be reusable across:

- homepage;
- Website editorial pages;
- eLearning catalogue and course surfaces;
- Roadmaps;
- Curricular Units;
- contribution flows;
- community/institutional pages;
- blog/editorial content;
- forms and CTAs where the FACODI theme is active.

The implementation must preserve Odoo Website Builder, standard Odoo navigation/authentication, native translation mechanisms and `website_slides` ownership of courses and learning content.

## 2. Product idea

FACODI should communicate one simple idea:

> A digital campus that feels like a living study notebook — open, collaborative and visibly under construction.

The identity should make learning feel navigable, remixable and shareable rather than institutional or bureaucratic.

Three product qualities guide every visual decision:

1. **Open** — content should look accessible, public and easy to enter.
2. **Guided** — users should always see a next step, route or context.
3. **Participatory** — the interface should make contribution, curation and improvement visible.

## 3. Approved visual direction

The approved direction is **Option B — FACODI Campus Paper Design System**.

The references establish the following recurring visual motifs:

- off-white paper backgrounds;
- square-grid / graph-paper textures;
- strong dark ink outlines;
- lime highlighter accents;
- mint, cyan, sky and coral/pink secondary accents;
- post-it / note-card surfaces;
- taped or pinned paper metaphors;
- offset shadows;
- compact mono labels;
- editorial headings with strong typographic contrast;
- deliberately imperfect but controlled visual rhythm;
- academic objects such as notebooks, course cards, highlighters, paper clips and study notes.

The implementation must translate those motifs into reusable Odoo components and SCSS primitives instead of importing Tailwind, a standalone SPA or copied static HTML.

## 4. Design principles

### 4.1 Paper, not glass

The primary surface metaphor is paper, not glassmorphism.

Use:

- subtle paper / warm-white backgrounds;
- 1–2 px dark outlines;
- small offset shadows;
- layered cards;
- grid textures used sparingly;
- highlighted text / marker strokes;
- visible section boundaries.

Avoid:

- excessive blur;
- large translucent overlays;
- gradient-heavy SaaS styling;
- generic rounded-card dashboards;
- floating glass panels disconnected from the study metaphor.

### 4.2 Expressive but structured

FACODI may look playful, but hierarchy must remain strong.

Every section should make the following visually obvious:

- what this area is;
- what the user can do;
- what the next step is;
- whether the content is editorial, dynamic or institutional.

Decorative details must never compete with the primary action.

### 4.3 System before page

No new visual pattern should exist only for one page if it can be represented as a reusable primitive.

Prefer:

- tokens;
- utility-like FACODI classes;
- stable reusable snippet components;
- page compositions built from snippets.

Avoid:

- large page-specific SCSS blocks;
- inline styles;
- duplicated QWeb markup;
- hard-coded business data inside visual components.

### 4.4 Odoo-native first

The FACODI identity must sit on top of Odoo rather than fighting it.

Preserve:

- Website Builder editing;
- Odoo color combinations;
- Website menus;
- Portal login/user state;
- standard form controls;
- `website_slides` routes;
- native dynamic snippets;
- standard translation extraction and PO catalogues.

### 4.5 Editorial honesty

Do not use UI labels that imply capabilities or live states that are not backed by real data.

Examples:

- do not display “live” or “real-time” merely as decoration;
- do not show invented enrolment counts;
- do not show fake course progress;
- do not use fictitious course data when Odoo already contains published course records;
- do not imply academic equivalence, recognition or accreditation unless explicitly supported by FACODI data and review state.

## 5. Token system

The current FACODI palette remains the source of truth, expanded into semantic design tokens.

### 5.1 Core colors

- `--facodi-ink: #142846`
- `--facodi-ink-deep: #0B1325`
- `--facodi-sun: #EFFF00`
- `--facodi-sun-bright: #FAFF00`
- `--facodi-mint: #A7E8BE`
- `--facodi-mint-strong: #86EFAC`
- `--facodi-cyan: #37BED2`
- `--facodi-blue: #3979C8`
- `--facodi-sky: #38BDF8`
- `--facodi-coral: #FF8A7A`
- `--facodi-pink: #F9A8D4`
- `--facodi-paper: #F9FAFB`
- `--facodi-paper-warm: #FDFCF7`
- `--facodi-white: #FFFFFF`
- `--facodi-line: #40536D`

Secondary accents must remain subordinate to ink + paper + sun.

### 5.2 Semantic surfaces

Define reusable semantic variables such as:

- `--facodi-surface-page`
- `--facodi-surface-sheet`
- `--facodi-surface-note`
- `--facodi-surface-highlight`
- `--facodi-border`
- `--facodi-shadow`
- `--facodi-shadow-hover`
- `--facodi-focus-ring`

### 5.3 Geometry

Use a limited radius scale:

- small: 4 px;
- default: 8 px;
- large: 12 px;
- pills only for tags/badges where semantically appropriate.

The new identity should rely more on shape, line and composition than on very large border radii.

### 5.4 Shadows

Primary card shadow language:

- compact offset;
- hard or semi-hard edge;
- ink-derived;
- no large blurred floating shadows.

Example conceptual pattern:

```scss
box-shadow: 4px 4px 0 color-mix(in srgb, var(--facodi-ink) 82%, transparent);
```

Hover elevation should increase slightly rather than animate dramatically.

### 5.5 Typography

Continue to use Odoo-compatible/local font stacks.

The hierarchy should visually resemble the supplied references:

- bold editorial display headings;
- clean readable body text;
- compact mono-style labels / metadata;
- optional handwritten accent only where a local/approved font strategy exists.

Do not introduce remote Google Font requests from the theme.

## 6. Reusable visual primitives

The theme should expose a small vocabulary of reusable primitives.

### 6.1 Paper surfaces

- `.facodi-paper`
- `.facodi-grid-paper`
- `.facodi-sheet`
- `.facodi-note`
- `.facodi-postit`

Responsibilities:

- surface color;
- border;
- texture;
- controlled offset shadow;
- spacing.

### 6.2 Editorial decoration

- `.facodi-highlight`
- `.facodi-marker-line`
- `.facodi-tape`
- `.facodi-pin`
- `.facodi-label`
- `.facodi-tab`

Decorative elements must have an accessibility-safe mode and must not contain critical information only as decoration.

### 6.3 Navigation/actions

Build on the existing FACODI button system:

- `.facodi-button`
- `.facodi-button-primary`
- `.facodi-button-secondary`
- `.facodi-button-ghost`
- `.facodi-text-link`

Primary actions use sun/highlighter with dark ink.

Secondary actions use paper/white surfaces with ink border.

### 6.4 Cards

Standardize:

- `.facodi-card`
- `.facodi-learning-card`
- `.facodi-course-card`
- `.facodi-route-card`
- `.facodi-unit-card`
- `.facodi-community-card`

All should share:

- common border language;
- shared shadow/elevation system;
- consistent metadata hierarchy;
- predictable hover/focus treatment.

### 6.5 Section headings

Create a single composable heading system:

- kicker / category;
- title;
- supporting copy;
- optional action;
- optional visual accent.

Existing `.facodi-kicker` and `.facodi-section-heading` should be evolved rather than replaced unnecessarily.

## 7. Website Builder component library

Keep the existing stable snippet IDs where practical and evolve their composition.

The FACODI Website Builder group should expose reusable components rather than one monolithic homepage.

Target library:

1. FACODI Hero / Campus Hero
2. Learning Entry Cards
3. Learning Journey
4. Dynamic Course Showcase
5. Academic Areas
6. Community / Contribution CTA
7. Institutional / SEA-EU block
8. Learning Principles
9. Ecosystem / Partners
10. Roadmap / Community Process
11. FAQ
12. Course Catalogue CTA
13. Editorial Intro
14. Editorial Routes
15. Editorial Pathway

New visual primitives should be shared through SCSS; snippet-specific SCSS should be limited to layout and component composition.

## 8. Homepage v3 composition

The homepage becomes the reference composition for the new design system.

### 8.1 Campus status strip

Purpose:

- establish FACODI as an open digital campus;
- optionally surface a short project/status statement;
- remain visually light and editorial.

Do not use fake dynamic data.

### 8.2 Header

Preserve the current Odoo-native navigation/authentication behavior.

Visual changes may include:

- stronger paper/ink separation;
- compact border;
- FACODI sun accent for the primary portal/login action;
- active navigation treatment;
- refined mobile spacing.

Do not create a new authentication flow or parallel menu system.

### 8.3 Hero — “Aprender em público”

Hero objective:

- communicate what FACODI is immediately;
- make “start learning” the primary action;
- present the notebook/campus metaphor in the first viewport.

Suggested content structure:

- FACODI kicker;
- large headline;
- short explanation;
- primary CTA into learning discovery;
- secondary CTA into “About / how FACODI works”;
- visual study-board composition on the right.

The right-side composition should be made from reusable HTML/CSS primitives, not a single baked image, unless a decorative image is explicitly required later.

Possible visual objects:

- UC card;
- roadmap card;
- sticky note;
- learning path line;
- highlighted annotation;
- paper sheet;
- status tag.

### 8.4 “Por onde queres começar?”

Three primary entry points:

- Courses;
- Roadmaps;
- Curricular Units.

Each is a large learning card with:

- distinct accent;
- small metadata/kicker;
- title;
- one sentence;
- clear action.

Routes must use the existing public routes.

### 8.5 “Da curiosidade ao próximo clique”

Explain the learning flow with three simple steps:

1. choose a question;
2. study at your own pace;
3. follow the next useful thread / contribute back.

Presentation should resemble a sequence of notes/cards rather than a corporate process timeline.

### 8.6 Dynamic course catalogue

Reuse the existing standard Odoo dynamic snippet infrastructure.

Source:

- published `slide.channel` records;
- existing `website.snippet.filter`;
- existing FACODI dynamic card template.

Do not place ORM searches in QWeb.

The visual treatment should use the new course-card primitive and paper/study metadata language.

### 8.7 Community discovery block

Purpose:

- show that FACODI grows through public contribution;
- make contribution visible without overwhelming first-time learners.

Actions may include:

- suggest a resource;
- improve a translation;
- collaborate with FACODI.

Use real existing routes only.

### 8.8 Institutional / project block

Present FACODI’s institutional context as supporting trust, not as the dominant homepage story.

Use:

- concise project context;
- SEA-EU / UAlg references where editorially appropriate;
- link to a dedicated “About” or project page.

Avoid turning the homepage into a funding/institutional landing page.

### 8.9 Footer

Refactor the footer to the Campus Paper system:

- ink-heavy base or clearly separated paper strip;
- grouped navigation;
- languages;
- licensing / open-learning note;
- project / Monynha attribution where currently appropriate;
- compact visual rhythm.

The footer must remain responsive and compatible with Website Builder-managed content.

## 9. eLearning visual integration

`website_slides` remains authoritative.

The new system may style:

- catalogue headings;
- course cards;
- course hero/header;
- lesson/content hierarchy;
- join/enrol actions;
- progress surfaces;
- metadata/tags;
- resource lists.

Do not:

- replace Odoo controllers;
- create parallel course pages;
- create custom learner-progress models;
- change completion semantics.

FACODI visual patterns must decorate and clarify the standard eLearning experience, not fork it.

## 10. Curriculum and Roadmap integration

Roadmaps and Curricular Units should visually share the same study-object vocabulary.

Suggested mapping:

- Roadmap → route card / study path;
- Curricular Unit → reference sheet / UC card;
- Course → course card;
- Module → tabbed/stacked learning card;
- Resource → compact note/resource item.

Visual hierarchy should make it clear when something is:

- an official external academic reference;
- a FACODI-reviewed mapping;
- a course;
- a learning resource;
- a suggested relation.

Do not visually blur these concepts into academic accreditation.

## 11. SCSS architecture

Preserve and refine the current file split.

Recommended target:

```text
theme_facodi/static/src/scss/
├── primary_variables.scss
├── bootstrap_overridden.scss
├── campus_paper_tokens.scss
├── components.scss
├── paper_primitives.scss
├── snippets.scss
├── website.scss
├── website_slides.scss
├── curriculum.scss
└── foundation_v2.scss
```

If adding files, each must have a clear responsibility.

Rules:

- no page-specific 50 KB stylesheet;
- avoid duplicated token declarations;
- avoid broad unscoped Bootstrap overrides;
- maintain theme scoping under `.facodi-site` where current architecture requires it;
- use CSS custom properties for reusable runtime styling where appropriate.

## 12. QWeb architecture

Maintain:

- one stable XML template per reusable snippet;
- a small snippet registry;
- page compositions made with `t-snippet-call`;
- native Odoo dynamic snippets for course content;
- standard Website and Portal building blocks.

Do not:

- put business queries in presentation templates;
- use inline Tailwind classes as the new architecture;
- duplicate the whole homepage markup across pages;
- create JavaScript translation stores;
- introduce React/Vue for the public theme.

## 13. Internationalization

English remains canonical QWeb source language.

Required languages:

- English;
- Portuguese (Portugal);
- Spanish;
- French.

Every new user-facing string must:

1. be extractable by Odoo;
2. be represented in `theme_facodi.pot`;
3. receive translations in the three supported PO catalogues;
4. preserve current Website translation behavior.

Avoid text embedded inside decorative raster images.

## 14. Accessibility

The redesign must improve or preserve:

- semantic headings;
- landmark structure;
- keyboard navigation;
- visible `:focus-visible`;
- minimum interactive target sizes;
- contrast;
- readable body sizes;
- meaningful CTA labels;
- alt/aria treatment for meaningful illustrations;
- decorative icons marked appropriately;
- `prefers-reduced-motion`.

Grid textures, marker strokes and tape must never reduce text readability.

## 15. Responsive design

Required breakpoints:

- mobile;
- tablet;
- desktop;
- large desktop.

Acceptance principles:

- no horizontal overflow;
- hero becomes a vertical composition on small screens;
- visual notebook objects simplify rather than shrink illegibly;
- cards retain touch targets;
- header keeps standard mobile behavior;
- footer groups remain readable;
- course catalogue does not force narrow multi-column layouts.

## 16. Motion

Motion is secondary.

Allowed:

- small card lift;
- marker/highlight reveal;
- short paper-sheet entrance;
- subtle hover state.

Avoid:

- parallax-heavy sections;
- large scroll animations;
- continuous floating elements;
- motion required to understand content.

Respect `prefers-reduced-motion`.

## 17. Content rules

Homepage copy should be concise, direct and human.

Preferred tone:

- “Há conhecimento por todo o lado. Encontra o teu próximo passo.”
- “Aprender em público.”
- “Da curiosidade ao próximo clique.”
- “Uma boa descoberta merece companhia.”
- “Ainda estamos a construir. Podes fazer parte.”

Avoid:

- exaggerated edtech claims;
- “AI-powered” marketing language unless the feature is directly relevant and visible;
- invented success statistics;
- dense institutional language above the fold.

## 18. Compatibility constraints

The refactor must preserve:

- Odoo 19 Community compatibility;
- `theme_common`;
- `website_slides`;
- Website Builder;
- existing routes;
- portal authentication;
- existing page content where possible;
- existing Website menus;
- active translated content;
- current dynamic course showcase data flow.

Existing stable XML IDs should not be renamed without a migration reason.

## 19. Migration strategy

The refactor must be additive and staged.

### Phase 1 — design tokens and primitives

- add/normalize Campus Paper tokens;
- add shared paper/card/highlight primitives;
- no homepage composition change yet.

### Phase 2 — reusable snippets

- refactor hero;
- refactor learning entry cards;
- refactor journey;
- refactor course-card presentation;
- preserve XML IDs where feasible.

### Phase 3 — homepage v3

- compose the new homepage from the updated snippets;
- preserve Website Builder editability;
- no hard-coded course data.

### Phase 4 — global FACODI surfaces

- header/footer polish;
- eLearning catalogue;
- course pages;
- Roadmaps;
- Curricular Units;
- editorial pages.

### Phase 5 — deployment pin

Only after `facodi-theme` verification is green:

- update `addons/facodi-theme` gitlink in `facodi-deploy`;
- run deployment repository validation;
- run disposable Coolify acceptance/preview;
- merge deployment pin only after the canonical checks pass.

Production must not be used as the experimentation surface.

## 20. Testing strategy

Implementation must follow TDD.

### 20.1 Contract tests

Add or evolve tests that verify:

- expected design-token declarations;
- stable snippet IDs;
- Website Builder registration;
- homepage composition uses reusable snippets;
- dynamic course showcase remains standard;
- no QWeb `request.env` / `sudo()` business-data access;
- no external remote font import;
- routes remain valid.

### 20.2 Odoo tests

Verify:

- clean module installation;
- module upgrade;
- QWeb render;
- asset compilation;
- homepage HTTP 200;
- catalogue HTTP 200;
- course detail HTTP 200.

### 20.3 i18n tests

Verify:

- new source strings are in POT;
- PT/ES/FR catalogues contain them;
- source references remain valid;
- public routes render in default and Portuguese Website language contexts.

### 20.4 Visual acceptance

Capture/inspect at minimum:

- homepage desktop;
- homepage tablet;
- homepage mobile;
- course catalogue desktop/mobile;
- one course detail;
- one curriculum/UC page;
- header/footer mobile.

Check:

- overflow;
- clipping;
- hierarchy;
- contrast;
- focus states;
- grid/background readability;
- large-text wrapping.

### 20.5 Deployment acceptance

After pinning in `facodi-deploy`:

- repository contract;
- Compose validation;
- migration test;
- fresh and idempotent runtime acceptance;
- public Website smoke tests;
- disposable preview before production promotion.

## 21. Acceptance criteria

This project phase is complete only when:

1. the FACODI identity clearly matches the Campus Paper direction;
2. the homepage is rebuilt as a reusable composition, not static one-off markup;
3. Website Builder remains usable;
4. dynamic course data still comes from standard Odoo mechanisms;
5. Courses, Roadmaps and Curricular Units share a coherent visual language;
6. all supported locales remain functional;
7. mobile layouts have no horizontal overflow;
8. accessibility basics remain intact;
9. theme tests and Odoo install/upgrade checks pass;
10. the tested theme commit is pinned in `facodi-deploy`;
11. disposable deployment acceptance passes before production promotion.

## 22. Non-goals

This refactor does not:

- redesign FACODI business architecture;
- replace Supabase processing or ingestion logic;
- introduce a SPA frontend;
- replace Odoo Website Builder;
- replace Odoo eLearning;
- create new academic-recognition claims;
- redesign the Odoo backend/admin UI;
- migrate content into a parallel CMS;
- deploy directly to production as part of the design-spec stage.

## 23. Repository ownership

### `facodi-theme`

Owns:

- visual identity;
- tokens;
- reusable visual primitives;
- Website Builder snippets;
- homepage composition;
- header/footer presentation;
- eLearning presentation;
- translations;
- visual regression/contract tests.

### `facodi-learning`

Owns:

- learning-domain data;
- curriculum;
- mappings;
- reviewed coverage;
- discovery / learning functionality;
- public learning routes.

### `facodi-deploy`

Owns:

- exact source pins;
- Docker/Coolify runtime;
- migration gate;
- deployment acceptance.

No theme markup or SCSS should be duplicated into `facodi-deploy`.

## 24. Implementation handoff

After this specification is reviewed and approved:

1. invoke the Superpowers `writing-plans` workflow;
2. produce a detailed TDD implementation plan;
3. execute work in an isolated implementation branch/worktree;
4. implement the theme first;
5. verify the theme independently;
6. request code review;
7. only then advance the deployment gitlink;
8. verify disposable deployment before any production promotion.
