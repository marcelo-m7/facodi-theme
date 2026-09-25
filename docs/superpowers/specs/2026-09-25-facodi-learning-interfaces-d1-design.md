# FACODI D1 — Learning Interfaces Redesign

**Status:** approved conversational design; written specification for review  
**Date:** 2026-09-25  
**Primary repositories:** `marcelo-m7/facodi-theme`, `marcelo-m7/facodi-learning`  
**Design owner:** `theme_facodi`  
**Domain owner:** `facodi_learning` and native Odoo `website_slides`

## 1. Purpose

D1 extends the approved FACODI Campus Paper system from the homepage/global shell into the learning interfaces that users spend the most time in:

- `/slides` — course catalogue;
- native Odoo course detail pages;
- `/roadmaps` — Roadmap catalogue;
- `/roadmaps/<id>` — Roadmap detail;
- `/unidades-curriculares` — Curricular Unit catalogue;
- Curricular Unit detail;
- `/modulos/<id>` — learning module detail.

The intended result is a coherent “digital academic filing cabinet / study notebook” experience: content should feel structured like study sheets, dividers, index cards and highlighted notes while remaining clearly digital, accessible and native to Odoo.

This phase is a visual/information-architecture refactor. It does not create new learning-domain models, new accreditation semantics, a parallel catalogue, a private notes subsystem, a forum, or a bibliography product.

## 2. Source hierarchy

D1 is grounded in the supplied Google AI Stitch export, with these references carrying the most weight:

1. `digital_highlighter_campus/DESIGN.md` — system-level visual rules.
2. `facodi_cat_logo_geral_de_cursos_fich_rio/code.html` and `screen.png` — catalogue/fichário reference.
3. `facodi_unidade_curricular_algoritmos_menu_cantos_arredondados/code.html` and `screen.png` — curricular-unit detail reference.
4. `facodi_redesign_escolar_marcadores_de_texto/code.html` and `screen.png` — homepage language already translated into Campus Paper.
5. `extracted_text_from_https_facodi.com_pt.md` — current public information architecture and real route/copy baseline.

The Stitch HTML is a design reference, not a data source. Static counts, fictional course codes, fictional teachers, fictional progress values, fabricated module sequences, forum messages, bibliographies and live-status claims must not be copied into Odoo unless the live FACODI models actually provide equivalent data.

## 3. Design principles

### 3.1 Campus Paper remains the base system

D1 does not create a second visual system. It evolves the existing Campus Paper release in `theme_facodi 19.0.7.0.0`.

The Stitch `Digital Highlighter Campus` source sharpens the system around:

- dark fountain-pen ink;
- off-white paper canvases;
- 24px graph-paper rhythm;
- fluorescent highlighter accents;
- crisp borders;
- hard offset shadows rather than blurred elevation;
- index tabs and file-folder metaphors;
- mono metadata labels;
- dense but legible academic information.

### 3.2 Highlighter semantics

The supplied reference defines:

- yellow `#E8FD36` — primary emphasis, active study state, important CTA;
- mint `#72F6B8` — completion/affirmative state;
- cyan `#34B6CE` — navigation/information;
- pink `#FF70A6` — priority/attention;
- orange `#FFAE33` — review/warning/task state.

D1 may harmonize the existing Campus Paper token values toward these references where safe, but all changes must remain semantic and backwards-compatible with the homepage/global surfaces.

Highlighter colours are surfaces or markers behind dark text. They are not used as small body-text colours where contrast would degrade.

### 3.3 Typography

The Stitch references use Space Grotesk, Plus Jakarta Sans and JetBrains Mono. The Odoo implementation keeps the existing no-remote-font rule:

- headings use the current local/system geometric stack that approximates Space Grotesk;
- body uses the existing system/body stack;
- metadata uses the current local monospace stack.

No Google Fonts, remote font CDN or Tailwind runtime is added.

### 3.4 Radius and depth

The new learning interfaces use smaller, trimmed-paper corners than the early homepage mockups:

- standard sheet/card: 4–8px semantic radius;
- index tabs: rounded top corners, square/attached lower edge where appropriate;
- true pill shapes reserved for compact state badges;
- standard hard shadow: shared `--facodi-shadow`;
- smaller controls: shared `--facodi-shadow-hover`;
- highlighted/current study object may use a heavier semantic shadow, introduced as a reusable token only if necessary.

## 4. Architecture boundaries

### 4.1 `facodi-theme` owns presentation

`theme_facodi` owns:

- Campus Paper tokens/primitives;
- catalogue and course-page inheritance for native `website_slides`;
- SCSS for all learning-interface presentation;
- reusable visual components/selectors;
- responsive/accessibility behavior;
- builder-safe decorative styling.

It must not add:

- learning-domain controllers;
- authentication;
- ORM searches in QWeb;
- parallel course/unit/module records;
- progress calculations;
- fake activity data.

### 4.2 `facodi-learning` owns curriculum-page structure

`facodi_learning` owns the dynamic QWeb pages and data projections for:

- Roadmaps;
- Curricular Units;
- modules;
- curriculum-to-course alignment;
- contribution context.

D1 may change QWeb structure/classes in `facodi_learning/views/website_curriculum.xml` when required to express the approved layout, but these changes must remain presentation-semantic:

- add wrappers;
- add stable CSS classes;
- move already-rendered values into clearer layout groups;
- preserve route/controller/model behavior;
- preserve provenance and academic-limit copy;
- preserve all existing conditionals and record-source rules.

No new model field or controller query is justified merely for visual parity with Stitch.

### 4.3 Native Odoo remains authoritative for courses

For `/slides` and course detail:

- `slide.channel` remains the course model;
- `slide.slide` remains lesson/content;
- Odoo controls enrolment, completion, access and progress;
- native search/filter/navigation behavior remains;
- existing editor-selected course covers remain untouched;
- FACODI only changes layout and presentation.

## 5. Reusable component vocabulary

D1 introduces a learning-specific layer on top of existing Campus Paper primitives. Components should be independently understandable and reusable.

### 5.1 `.facodi-learning-hero`

Purpose: shared top sheet for catalogue, Roadmap and UC index/detail contexts.

Contains:
- kicker / record type;
- page title;
- explanatory lead;
- optional metadata strip;
- optional actions;
- optional compact status/progress.

Uses graph-paper or white paper surface with dark ink border and hard shadow.

### 5.2 `.facodi-index-tabs`

Purpose: cross-navigation between the three core learning entry points:

- Courses;
- Roadmaps;
- Curricular Units.

The active destination uses yellow highlighter; alternate destinations use paper/mint/cyan treatments.

These are real links, not JS-only tabs.

### 5.3 `.facodi-filter-sheet`

Purpose: wraps native search/filter controls as a filing/search sheet.

Rules:
- preserve form semantics;
- no custom filter state outside native query parameters;
- controls wrap/stack on mobile;
- clear/apply actions remain keyboard accessible.

### 5.4 `.facodi-record-card`

Generic academic record card for courses, Roadmaps and units.

Sub-elements:
- `__tab` — category/type/index label;
- `__meta` — code/year/ECTS/lesson count where real;
- `__title`;
- `__summary`;
- `__tags` — only real tags/data;
- `__footer` — real CTA/state.

A record card must never fabricate course codes, faculty, hours or tags.

### 5.5 `.facodi-study-progress`

Purpose: presentation wrapper around progress already provided by Odoo/FACODI.

Allowed:
- percentage already available;
- next item already available;
- completion state already available.

Not allowed:
- invented “week 05 of 12”;
- invented module completion;
- fake cohort statistics.

### 5.6 `.facodi-module-stack`

Purpose: visually separate completed/current/next content when the underlying projection supports that distinction.

Variants:
- `--complete` mint;
- `--current` yellow emphasis;
- `--next` paper/cyan.

When a page does not expose trustworthy completion/current/next semantics, render a neutral ordered module/item list instead.

### 5.7 `.facodi-reference-rail`

Purpose: right-hand desktop rail that replaces the unsupported Stitch notes/forum/bibliography column with real FACODI context.

Eligible content:
- provenance/source;
- institutional/programme metadata;
- ECTS/year/period/classification;
- coverage status;
- related-course count;
- contribution CTA;
- public-source link;
- real authenticated progress where already available.

At mobile widths the rail becomes normal-flow blocks below the primary content.

### 5.8 `.facodi-open-callout`

Purpose: community/open-source contribution panel inspired by the Stitch “found an error?” block.

Uses only real FACODI routes:
- suggest resource;
- contact/collaboration;
- source/repository link only when a real canonical destination exists.

## 6. Page design — Course catalogue `/slides`

### 6.1 Intent

Translate the Stitch “Catálogo & Fichário de Cursos Livres” into the real Odoo course catalogue without copying fictional statistics or fabricated course metadata.

### 6.2 Composition

1. **Learning hero**
   - label: FACODI learning catalogue;
   - H1 centred on courses/open learning;
   - real explanatory copy;
   - index tabs: Courses active, Roadmaps, Curricular Units;
   - native search stays functional and visually integrated.

2. **Search/filter sheet**
   - native Odoo search and category/tag controls remain authoritative;
   - style as file/index controls;
   - no custom JS filter system unless Odoo already provides the interaction.

3. **Course record grid**
   - current `facodi-course-media` cover strategy retained;
   - hard paper border/shadow;
   - real title/description;
   - real lesson/content count when Odoo exposes it;
   - real tags only;
   - CTA uses native course URL;
   - no invented UC code unless a real curriculum mapping code is explicitly available for that card.

4. **How FACODI learning works**
   - static explanatory section may visually borrow the Stitch three-step structure;
   - wording must describe actual FACODI behavior;
   - must not claim local-browser notebook cloning, GitHub peer review, or private note synchronization unless separately implemented.

5. **Community CTA**
   - use real contribution/contact routes.

### 6.3 Empty state

When no courses are published:
- retain standard truthful empty state;
- do not render sample cards;
- keep Roadmap/UC navigation and contribution CTA available.

## 7. Page design — Native Odoo course detail

### 7.1 Intent

Make course detail feel like an open study dossier while preserving all `website_slides` mechanics.

### 7.2 Header

The native course cover/header remains the functional base.

Campus Paper presentation should expose:
- title;
- real tags;
- real course description;
- enrolment/join state;
- real progress for authenticated learners;
- native course action buttons.

Custom cover images remain untouched.

### 7.3 Lesson/module content

Native lesson/category lists become paper stacks:

- category header = file-divider/tab;
- lesson row = study-line/card;
- content-type cue remains;
- completed state may use mint only where Odoo exposes completion;
- current/selected lesson may use yellow only where a real active state exists.

No fictitious study schedule is generated.

### 7.4 Curriculum alignment

The existing `facodi_learning.approved_course_curriculum_links` block becomes a Campus Paper reference panel:
- curricular-unit name;
- programme/year;
- reviewed relation badge;
- direct real link to unit.

No claim that FACODI awards credit/equivalence.

## 8. Page design — Roadmap catalogue `/roadmaps`

### 8.1 Intent

Move from generic Bootstrap cards toward an academic filing-cabinet index.

### 8.2 Structure

- `facodi-learning-hero` with Roadmaps active in `facodi-index-tabs`;
- concise source/governance explanation;
- one `facodi-record-card` per validated/published curriculum reference;
- card metadata only from real reference fields:
  - institution;
  - programme;
  - academic year;
  - programme code where present;
- CTA to Roadmap detail;
- contribution CTA stays available.

No static “24 courses”/student statistics.

## 9. Page design — Roadmap detail `/roadmaps/<id>`

### 9.1 Intent

Replace the current administrative-table feel with a study-path document while retaining the same data and provenance.

### 9.2 Hero/reference header

Show:
- institution;
- academic year;
- programme title;
- programme code if present;
- validated-reference state;
- official-source link;
- FACODI limitations/provenance copy.

### 9.3 Study path

Use the existing `unit_matrix_groups` projection.

Desktop:
- year as a large paper divider;
- period as an index tab/section;
- each curricular unit as a structured row/card;
- unit metadata;
- modules;
- reviewed course coverage.

Mobile:
- table-like structures must become stacked cards or internally scrollable table sections;
- no page-level horizontal overflow.

A visual connector/sequence may be added with CSS only if it does not imply prerequisites or ordering beyond the actual grouped curriculum order.

## 10. Page design — Curricular Unit catalogue `/unidades-curriculares`

### 10.1 Intent

Translate the Stitch filing/search language into a functional academic index.

### 10.2 Structure

1. learning hero with Curricular Units active;
2. `facodi-filter-sheet` containing existing:
   - Roadmap;
   - year;
   - period;
   - ECTS;
   - apply/clear actions;
3. result count;
4. `facodi-record-card` grid.

Each unit card may show only real:
- institution/programme;
- unit name;
- external code;
- year;
- ECTS;
- coverage state;
- related published-course count;
- contribution CTA if coverage incomplete;
- detail CTA.

Coverage colors retain existing semantics and wording.

## 11. Page design — Curricular Unit detail

### 11.1 Intent

Use the supplied UC-101 Stitch reference as the strongest page-composition reference while replacing unsupported features with real FACODI information.

### 11.2 Desktop composition

12-column grid:

- main content: 8 columns;
- `facodi-reference-rail`: 4 columns.

At tablet/mobile this becomes one column.

### 11.3 Hero

The Stitch hero includes code, workload, level, licence, cohort and coordinator. D1 only renders fields actually available.

Guaranteed current FACODI data can include:
- institution;
- academic year;
- programme;
- unit code;
- unit title;
- ECTS;
- curricular year;
- period;
- classification;
- optional group where present;
- official source;
- coverage status.

No fake professor/coordinator, cohort size, workload hours or licence is introduced.

### 11.4 Main content

Order:

1. **Learning pathway**
   - existing published modules;
   - real item count;
   - real progress/next item only for authenticated users where already projected.

2. **Current/complete/next visual states**
   - use only data already present in the projection;
   - if the projection exposes merely a module list plus progress percentage, keep the module stack neutral and highlight only the actual next item;
   - do not derive completion heuristically from visual order.

3. **Published FACODI coverage**
   - reviewed course relations;
   - course title/description;
   - coverage type;
   - real course link.

4. **Editorial gap state**
   - retain current truthful wording;
   - contribution CTA;
   - course catalogue CTA.

### 11.5 Reference rail

Replace Stitch's unsupported blocks as follows:

- “Meu Caderno de Notas” → **not implemented**;
- “Bibliografia Aberta” → **not implemented unless real model-backed bibliography exists later**;
- “Dúvidas da Turma” → **not implemented**.

The right rail instead contains real panels:

1. **Source & provenance**
   - official source;
   - academic year;
   - programme;
   - validation/limits wording.

2. **Academic metadata**
   - ECTS;
   - year;
   - period;
   - classification;
   - optional group.

3. **Coverage**
   - covered/partial/gap;
   - count of real related published courses when already provided.

4. **Contribute**
   - suggest a learning resource for this unit.

This preserves the Stitch page balance without inventing product features.

## 12. Page design — Module detail `/modulos/<id>`

The existing module detail becomes a focused study sheet:

- breadcrumb;
- module title;
- real description;
- real progress when authenticated;
- real next item CTA where projected;
- item list as study rows;
- empty state as a neutral paper note.

No additional module sequencing is calculated in the theme.

## 13. State and semantic mapping

### 13.1 Completion

Mint is used only for actual completed/affirmative state exposed by Odoo/FACODI.

### 13.2 Current/next

Yellow is used for:
- active destination tab;
- real current/next study action;
- primary highlight.

It must not imply completion.

### 13.3 Informational/navigation

Cyan is used for:
- informational tabs;
- navigational accents;
- code/reference labels.

### 13.4 Attention

Pink/orange are reserved for real priority/warning/review states. D1 will not introduce them merely for decoration where the content has no such meaning.

## 14. Responsive behavior

Breakpoints follow the existing Odoo/Bootstrap environment and the Stitch design intent.

### Desktop >= 1024px

- 12-column compositions;
- UC detail 8/4 main/rail;
- course/roadmap/unit cards may use 2–3 columns depending on native container width;
- filters stay horizontal when space allows.

### Tablet 768–1023px

- 8-column feeling;
- rail may collapse below main content if the layout becomes cramped;
- cards use 2 columns where practical.

### Mobile < 768px

- one-column page flow;
- 1rem page gutters;
- `min-width: 0` on all nested grid/flex children;
- long titles/codes wrap;
- filter controls stack;
- large data tables scroll internally;
- no page-level horizontal scrollbar at 320px;
- tab navigation wraps or becomes a horizontally scrollable contained strip without widening the page;
- touch targets remain at least 44px.

## 15. Accessibility

- preserve semantic headings in logical order;
- preserve native form labels;
- maintain keyboard access to all links/forms/course actions;
- visible `:focus-visible`;
- no information conveyed by highlighter colour alone;
- coverage/progress states retain textual labels;
- respect `prefers-reduced-motion`;
- avoid hover-only disclosure;
- decorative marker/tape/graph effects remain aria-neutral;
- external links retain appropriate `rel` behavior.

## 16. Internationalization

English remains canonical QWeb source.

If D1 changes source copy:
- update `theme_facodi.pot` and/or `facodi_learning.pot`;
- update PT/ES/FR catalogues in the owning addon;
- add explicit translation tests for new strings.

Do not add language-specific QWeb branches.

Route localization remains Odoo's responsibility.

## 17. Testing strategy

### 17.1 `facodi-theme`

Add/extend contracts for:
- learning hero;
- index tabs;
- filter sheet;
- record card;
- study progress/module stack;
- course catalogue/course detail native-hook preservation;
- custom course-cover preservation;
- 320px overflow-related CSS contracts;
- reduced motion/focus;
- PT/ES/FR.

Odoo tests must prove:
- `/slides` still renders;
- course detail still uses native `website_slides`;
- no fake static course data;
- compiled frontend assets contain D1 selectors.

### 17.2 `facodi-learning`

Tests must prove:
- existing public routes unchanged;
- existing record visibility/security unchanged;
- Roadmap index/detail values are sourced from the same records;
- UC filters preserve current query behavior;
- UC detail preserves provenance/limits copy;
- module detail preserves projection/progress behavior;
- new semantic wrappers/classes exist;
- no unsupported notes/forum/bibliography content is rendered.

### 17.3 Integrated runtime

The previously designed Phase C browser gate is extended to inspect D1 layouts on:
- `/slides`;
- one real course;
- `/roadmaps`;
- one Roadmap;
- `/unidades-curriculares`;
- one UC;
- one module.

Required widths:
- 1440;
- 1024 where useful;
- 390;
- 320.

The integrated gate must fail on page-level horizontal overflow.

## 18. Release strategy

D1 is implemented before production pinning.

Expected ownership sequence:

1. `facodi-theme` — reusable D1 components and native eLearning presentation.
2. `facodi-learning` — semantic QWeb restructuring for Roadmaps/UCs/modules.
3. integrated test against both exact green SHAs.
4. only then update `facodi-deploy`.

No push to `facodi-deploy/main` occurs while D1 is still being iterated.

Version numbers are assigned in the implementation plan based on the current manifests:
- current `theme_facodi`: `19.0.7.0.0`;
- current `facodi_learning`: `19.0.1.21.0`.

## 19. Out of scope

D1 explicitly excludes:

- private/persistent student notes;
- browser-local note synchronization;
- class discussion/forum;
- verified-answer system;
- bibliography/reference database;
- downloadable Markdown study notebook generation;
- embedded coding terminal;
- invented workload hours;
- invented teacher/coordinator profiles;
- fictional enrolment/student counts;
- fictional semesters/live status;
- new accreditation/equivalence semantics;
- changing course/curriculum business models solely for layout parity;
- copying Tailwind, Material Symbols, Google Fonts or Stitch JS into Odoo.

These can become separate functional projects if later requested.

## 20. Acceptance criteria

D1 is complete when:

1. all seven learning surface families share one recognizable Campus Paper/fichário visual language;
2. catalogue and UC detail clearly reflect the supplied Stitch references without copying unsupported data/features;
3. Odoo course search/enrolment/progress/content behavior remains native;
4. Roadmap/UC/module business behavior remains owned by `facodi_learning`;
5. no fictional statistics, educators, course codes or study states are introduced;
6. UC detail uses a real-data 8/4 desktop composition and one-column mobile layout;
7. `/slides`, Roadmaps, UCs and modules have no page-level horizontal overflow at 320px;
8. native PT/ES/FR translations remain green;
9. custom course covers remain intact;
10. clean install/upgrade tests pass in both owning repositories;
11. integrated exact-SHA browser acceptance passes before any deployment promotion.
