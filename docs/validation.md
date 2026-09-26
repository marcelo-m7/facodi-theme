# Validation — 2026-09-07

## Environment and scope

Validation uses disposable PostgreSQL 16 and the official Odoo 19.0 Community
container with `odoo/design-themes` pinned at
`a1818df4ade65406c0cacae8b1ea676e6f70095f`. The public FACODI sites are evidence
and deployment targets only; this repository's CI does not modify production.

Release under validation: `theme_facodi` `19.0.7.0.0`.

## Automated evidence required for release

The release gate is the repository's `Odoo 19 Theme CI` workflow. A revision is
eligible for merge only when the workflow succeeds on that exact PR head. After
merge, the workflow must succeed again on the exact `main` merge commit.

The workflow performs:

- repository, homepage, Foundation v2 and native-i18n contracts;
- responsive eLearning catalogue style contract;
- pinned official Odoo design-theme checkout;
- installation of the pinned legacy `19.0.5.0.1` theme on a clean PostgreSQL 16 database;
- real Odoo 19 addon tests and frontend/Website Builder asset compilation;
- seeding of persisted legacy course-showcase markup;
- upgrade to the current release with `-u theme_facodi`;
- verification that the legacy dynamic-snippet builder contract is repaired without losing editor content.

## Campus Paper homepage regression matrix

The `19.0.6.0.0` gate additionally verifies:

- semantic Campus Paper runtime tokens and reusable paper primitives;
- no remote font requests;
- editable hero, learning-entry, learning-step, community, institutional and
  closing-CTA snippets;
- standard dynamic-course empty state with no invented static course records;
- canonical public routes for Courses, Roadmaps and Curricular Units;
- PT/ES/FR Campus Paper source-copy translations;
- responsive single-column collapse for the hero, learning cards and community
  cards;
- visible focus and reduced-motion declarations;
- persisted legacy Website Builder content across module upgrade.

Visual geometry is still supporting evidence rather than a formal pixel-perfect
or WCAG certification. Required manual/disposable-browser viewports for this
release are 1440×1200, 1024×1366, 390×844 and 320×700 on the homepage, plus
1440×1200 and 390×844 on `/slides`. No screenshot evidence is claimed unless
those captures are actually produced and inspected.

## Campus Paper global surfaces regression matrix

Release `19.0.7.0.0` extends the Campus Paper gate to global Website,
eLearning, curriculum and editorial surfaces.

Automated source/runtime checks cover:

- the native FACODI desktop header, standard Odoo mobile header, Portal
  identity actions and an existing Website Builder header customization;
- Campus Paper footer hooks and standard public form focus/touch behavior;
- `website_slides` catalogue cards, exact default-cover replacement,
  editor-selected cover preservation, course actions, progress, lesson rows,
  navigation tabs, tags and profile/badge surfaces;
- Roadmap/Curricular Unit card, filter, pathway, coverage and table hooks
  exposed by `facodi-learning`, including shrinkable 320 px layouts and
  internal table scrolling;
- editorial intro, route and pathway snippets built from shared paper
  primitives without changing their user-facing source copy;
- native PT/ES/FR catalogues and the absence of language-specific QWeb
  branches;
- clean legacy install, upgrade to `19.0.7.0.0`, asset compilation and
  persisted Website Builder/dynamic-snippet markup.

Required browser acceptance before deployment promotion remains:

- header + homepage at 1440×1200, 1024×1366, 390×844 and 320×700;
- `/slides` at 1440×1200, 390×844 and 320×700;
- one real course detail at desktop/mobile widths;
- `/roadmaps`, one Roadmap detail, `/unidades-curriculares` and one
  curricular-unit detail with the integrated `facodi-learning` addon;
- one editorial page using intro/routes/pathway snippets;
- keyboard focus, reduced-motion behavior and custom course-cover retention.

The theme repository CI proves real Odoo rendering and asset compilation but
does not claim pixel-perfect browser inspection. The integrated Roadmap/UC and
viewport screenshot gate is therefore repeated in Phase C on the disposable
deployment runtime before any production promotion.

## D2 editorial/public regression matrix

Release `19.0.9.0.0` adds the Stitch-informed editorial layer without moving
editorial truth out of Odoo Website.

Theme-side evidence covers:

- eight reusable D2 Website Builder components and their native registry;
- About/How/Contribution/Manifesto/Partners page-picker compositions without
  fixed `website.page` imports;
- a persisted editor-owned D2 page surviving a second theme upgrade unchanged;
- native Blog index/article/card/prose hooks with sparse/rich post fixtures and
  custom cover preservation;
- native Contact rendering with exactly one `#contactus_form`, unchanged
  `/website/form/` action, native fields and submit control;
- policy long-form containment for URLs, code, tables and responsive media;
- complete POT/PT/ES/FR D2 view occurrences;
- phone single-column layouts, focus visibility and reduced-motion handling;
- clean legacy install, upgrade to `19.0.9.0.0`, frontend asset compilation
  and Odoo HttpCase regressions.

Disposable deployment acceptance must additionally exercise About,
Contribution, Blog index, rich/sparse articles, Contact and a policy fixture at
desktop/mobile widths, with the hard condition
`document.documentElement.scrollWidth <= window.innerWidth + 1` at 320 px.

Production Website recomposition is deliberately separate from module upgrade:
the current live page arch is read/backed up first, then meaningful existing
content is mapped into D2 components only after the new theme code is healthy.
Legal paragraphs, dates and obligations are never rewritten by the theme.

## D1 learning interfaces regression matrix

Release `19.0.8.0.0` adds the Stitch-informed academic filing-cabinet layer
across the learning surfaces while preserving native Odoo and
`facodi-learning` behavior.

Theme-side automated evidence covers:

- reusable learning hero, index tabs, filter sheet, record card, progress,
  module-stack, reference-rail and contribution-callout primitives;
- native `/slides` catalogue and course-detail hooks with no fabricated
  course metadata;
- exact-default-cover replacement plus Odoo-rendered proof that a custom
  editor-selected course cover keeps its own inline style;
- Roadmap/UC catalogue selectors, Roadmap study-path styling, the approved 8/4
  desktop UC detail layout, module detail and curriculum-alignment sheet;
- `min-width: 0`, long-text wrapping, tablet/mobile rail collapse, internal
  table scrolling, focus visibility and reduced-motion declarations;
- clean legacy install, upgrade to `19.0.8.0.0`, frontend asset compilation
  and Website Builder persistence.

Cross-repository acceptance remains mandatory because Roadmap, UC and module
markup belongs to `facodi-learning`. The disposable integrated runtime must
check one real route of each family at 1440/1024/390/320 widths and fail when
`document.documentElement.scrollWidth > window.innerWidth + 1`.

Unsupported Stitch-only features remain intentionally absent: private notebook,
class forum/questions, bibliography database, fictional instructors/student
counts, invented workload and fabricated study progress.

## eLearning regression matrix

The Odoo `HttpCase` and `TransactionCase` suite verifies the presentation added in
`19.0.6.0.0` against real `website_slides` records and routes:

- `/slides` keeps the standard `.o_wslides_course_card` hook;
- course cards render an explicit `slide.channel` cover first;
- a published stored `slide.slide` image is the next visual source;
- YouTube thumbnails are derived deterministically from Odoo's stored `youtube_id`;
- YouTube fixture creation is mocked so the test suite itself does not depend on provider HTTP;
- courses without usable media render the FACODI HTML/CSS fallback and no broken `<img>`;
- the visual resolver returns one entry per channel and excludes unpublished/category slides;
- training pages keep `.o_wslides_slides_list_slide` and `.o_wslides_js_slides_list_slide_link`;
- documentation pages keep `.o_wslides_lesson_card`;
- content-type cues are present for standard Odoo slide categories;
- documentation cards render stored images, deterministic YouTube media and icon fallbacks;
- Portuguese `/pt/slides` and authenticated `/slides` retain the standard catalogue hooks.

The static style contract additionally requires:

- FACODI catalogue, course-media, lesson-media, fallback and content-type selectors;
- CSS Grid column definitions at 576, 992, 1280 and 1600 px;
- predictable `object-fit: cover` media cropping;
- visible `:focus-visible` rules;
- `prefers-reduced-motion` handling.

## Runtime boundaries

The catalogue visual resolver is intentionally read-only. It does not write images,
make thumbnail-provider requests or introduce a custom course model/controller. The
QWeb layer consumes a batch visual map and preserves `website_slides` as the owner of
search, filtering, enrolment, lessons and progress.

The content-type labels come from Odoo's translated `slide_category` selection
metadata instead of a second FACODI translation vocabulary. English remains the
canonical theme source language and Website language routing remains native Odoo.

## Reproduction

With Odoo core, the pinned design-themes checkout and this repository available on
`addons_path`, the fast contracts are:

```sh
bash tests/test_module_contract.sh
bash tests/test_campus_paper_contract.sh
bash tests/test_global_shell_contract.sh
bash tests/test_homepage_dashboard_contract.sh
bash tests/test_foundation_v2_contract.sh
bash tests/test_curriculum_style_contract.sh
bash tests/test_learning_interfaces_contract.sh
bash tests/test_editorial_interfaces_contract.sh
bash tests/test_blog_contract.sh
bash tests/test_public_pages_contract.sh
bash tests/test_i18n_contract.sh
bash tests/test_elearning_catalog_style_contract.sh
bash tests/test_mobile_interaction_contract.sh
```

The CI workflow then runs the clean-install and upgrade commands against the same
disposable database using the official Odoo 19 container and `--test-tags
/theme_facodi`.

## Existing Website and Builder coverage

The broader regression suite continues to verify:

- native theme lifecycle and `_theme_facodi_post_copy()`;
- selectable FACODI desktop header plus standard Odoo mobile header;
- nested/external Website menu behavior and Portal identity controls;
- configured Website logo and favicon ownership;
- reusable FACODI snippets and New Page compositions;
- editor-owned page HTML across theme reload;
- `/`, `/contactus` and `/web/login`;
- native Portuguese, Spanish and French Website translations;
- compilation and HTTP retrieval of frontend assets without Sass errors.

The persisted legacy course-showcase test specifically protects the Odoo dynamic
snippet editor contract (`.s_dynamic_snippet_container` and
`.s_dynamic_snippet_content`) introduced by release `19.0.5.0.2`.

## Visual and deployment boundary

CI proves source contracts, real Odoo rendering, asset compilation, clean install and
upgrade behavior. It does not claim pixel-perfect browser geometry on every device or
an authenticated production Website Builder session. Browser screenshots and manual
keyboard inspection remain supporting evidence rather than a formal WCAG audit.

`marcelo-m7/facodi-deploy` must pin the exact merged `facodi-theme` commit separately.
Advancing that gitlink validates the deployment composition; it is not evidence that
Coolify production has already redeployed.