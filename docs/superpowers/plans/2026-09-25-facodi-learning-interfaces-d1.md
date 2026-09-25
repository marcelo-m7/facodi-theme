# FACODI D1 Learning Interfaces Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (\`- [ ]\`) syntax for tracking.

**Goal:** Refactor the real FACODI learning surfaces into one Campus Paper / academic filing-cabinet experience across Odoo courses, Roadmaps, Curricular Units and modules, using only real model-backed data.

**Architecture:** D1 is implemented across two owner repositories. \`facodi-theme\` supplies reusable learning-interface primitives plus native \`website_slides\` inheritance; \`facodi-learning\` adds semantic QWeb structure to the dynamic Roadmap/UC/module pages it already owns. A final integration branch in \`facodi-deploy\` pins the exact green SHAs for disposable cross-addon runtime/browser verification without merging production.

**Tech Stack:** Odoo 19 Community, QWeb, Website Builder, website_slides, SCSS/CSS custom properties, Python/Odoo tests, Bash static contracts, native PO/POT i18n, Git submodules, Docker Compose, Playwright browser acceptance through the deployment repository.

**Spec:** \`docs/superpowers/specs/2026-09-25-facodi-learning-interfaces-d1-design.md\`

## Global Constraints

- D1 covers \`/slides\`, native course detail, \`/roadmaps\`, Roadmap detail, \`/unidades-curriculares\`, Curricular Unit detail and \`/modulos/<id>\`.
- Campus Paper remains the base visual system; do not create a second theme system.
- \`theme_facodi\` owns presentation and native \`website_slides\` inheritance only.
- \`facodi_learning\` owns Roadmap/UC/module QWeb structure, projections, provenance and coverage semantics.
- \`slide.channel\` and \`slide.slide\` remain authoritative for courses and lessons.
- Do not add controllers, authentication, new learning-domain models, ORM searches in theme QWeb, or parallel progress logic.
- Do not implement private notes, class discussion/forum, bibliography database, terminal, invented workload hours, invented instructors, fictional enrolment counts or fabricated progress.
- Custom/editor-selected Odoo course covers must remain untouched.
- English remains canonical QWeb source; PT/ES/FR stay native PO/POT catalogues.
- Do not add Google Fonts, remote fonts, Tailwind runtime, Material Symbols or Stitch JavaScript.
- Mobile hard gate: no page-level horizontal overflow at 320 px.
- Coverage/progress state must retain textual semantics; colour never becomes the only signal.
- \`facodi-deploy/main\` remains untouched until both owner repositories are green and the cross-repo disposable integration gate passes.
- Planned release versions: \`theme_facodi 19.0.8.0.0\`, \`facodi_learning 19.0.1.22.0\`.

## File Structure

### facodi-theme

- Create: \`theme_facodi/static/src/scss/learning_interfaces.scss\` — D1 reusable learning-specific primitives: hero, index tabs, filter sheet, record card, study progress, module stack, reference rail, open callout.
- Modify: \`theme_facodi/__manifest__.py\` — load D1 stylesheet and release \`19.0.8.0.0\`.
- Modify: \`theme_facodi/views/website_slides.xml\` — catalogue/course-detail semantic hooks only; preserve native Odoo behavior.
- Modify: \`theme_facodi/static/src/scss/website_slides.scss\` — course catalogue/detail presentation.
- Modify: \`theme_facodi/static/src/scss/curriculum.scss\` — consume D1 semantic hooks emitted by facodi-learning.
- Create: \`tests/test_learning_interfaces_contract.sh\` — D1 design-system and no-fake-feature contract.
- Modify: \`tests/test_elearning_catalog_style_contract.sh\` — native Odoo course contract.
- Modify: \`tests/test_mobile_interaction_contract.sh\` — 320 px shrink/wrap behavior.
- Modify: \`tests/test_module_contract.sh\` — release/asset guard.
- Modify: \`theme_facodi/tests/test_website.py\` — rendered/compiled asset assertions.
- Modify i18n files only if this implementation introduces new user-facing theme strings.

### facodi-learning

- Modify: \`facodi_learning/views/website_curriculum.xml\` — semantic D1 wrappers/classes and layout grouping for Roadmap catalogue/detail, UC catalogue/detail and module detail.
- Modify: \`facodi_learning/views/website_slides.xml\` only for curriculum-alignment/contribution blocks rendered on native course pages.
- Modify: \`facodi_learning/__manifest__.py\` — release \`19.0.1.22.0\`.
- Create: \`facodi_learning/tests/test_learning_interfaces_contract.py\` — static/QWeb D1 structure contract.
- Modify: \`facodi_learning/tests/test_curriculum_ui.py\` — public QWeb integration assertions.
- Modify: \`facodi_learning/tests/test_curriculum_public_units.py\` — UC detail/gap/provenance semantic structure.
- Modify: \`facodi_learning/tests/test_curriculum_module.py\` — module projection/UI contract without changing model semantics.
- Modify: \`facodi_learning/tests/test_website_i18n_contract.py\` — i18n/no-unsupported-feature checks.
- Modify PO/POT only if source strings change.

### facodi-deploy integration branch only

- Modify gitlinks: \`addons/facodi-theme\`, \`addons/facodi-learning\` to exact green D1 SHAs.
- Extend existing disposable browser/runtime acceptance to assert D1 page hooks and 320 px overflow behavior.
- Do not merge this integration branch to production as part of D1 implementation.

## Review Focus

1. **Published course with a custom editor-selected cover** — D1 may restyle card/header chrome but must not overwrite the image/cover; Task 2 pins the existing exact-default-gradient-only override.
2. **Curricular Unit with missing optional metadata such as ECTS/group/classification** — detail/index layouts must collapse cleanly without empty fake labels; Task 4 pins conditional rendering and absence of fabricated fields.
3. **Authenticated user has progress but public user does not** — progress/current/next emphasis must render only from the existing projection/native Odoo state, never inferred from item order; Tasks 2 and 4 pin both states.
4. **Very long translated course/UC/Roadmap/module title at 320 px** — nested flex/grid children must shrink/wrap without page-level overflow; Tasks 1, 2 and 4 pin \`min-width: 0\`, \`overflow-wrap\` and the integrated browser gate.
5. **Roadmap/UC page has no covered/published courses** — truthful gap/empty state and contribution CTA remain; no sample course or “completed/current” decoration appears; Task 4 pins the existing gap contract.

---

### Task 1: Build reusable D1 learning-interface primitives in facodi-theme

**Repository:** \`marcelo-m7/facodi-theme\`

**Files:**
- Create: \`theme_facodi/static/src/scss/learning_interfaces.scss\`
- Create: \`tests/test_learning_interfaces_contract.sh\`
- Modify: \`theme_facodi/__manifest__.py\`
- Modify: \`tests/test_module_contract.sh\`
- Modify: \`tests/test_mobile_interaction_contract.sh\`

**Interfaces:**
- Consumes: Phase A/B Campus Paper tokens and primitives.
- Produces classes: \`.facodi-learning-hero\`, \`.facodi-index-tabs\`, \`.facodi-filter-sheet\`, \`.facodi-record-card\`, \`.facodi-study-progress\`, \`.facodi-module-stack\`, \`.facodi-reference-rail\`, \`.facodi-open-callout\`.

- [ ] **Step 1: Write the failing D1 primitive contract**

Create \`tests/test_learning_interfaces_contract.sh\` asserting that \`learning_interfaces.scss\` exists and contains every produced class plus:
- \`min-width: 0\`;
- \`overflow-wrap: anywhere\`;
- \`@media (max-width: 767.98px)\`;
- \`grid-template-columns: minmax(0, 1fr)\`;
- \`:focus-visible\`;
- \`prefers-reduced-motion\`.

Also fail if the theme contains user-facing strings matching unsupported Stitch concepts:
- \`My Notebook\`;
- \`Class Questions\`;
- \`Open Bibliography\`;
- \`verified answer\`;
- hard-coded fictional student counts.

- [ ] **Step 2: Run RED**

~~~bash
bash tests/test_learning_interfaces_contract.sh
~~~

Expected: FAIL because \`learning_interfaces.scss\` does not exist.

- [ ] **Step 3: Implement the reusable SCSS interfaces**

Create \`learning_interfaces.scss\` with one focused rule group per produced class.

Pinned behavior:
- hero and cards use existing \`--facodi-border\`, \`--facodi-shadow\`, \`--facodi-radius\`;
- active tab uses \`--facodi-sun\`;
- affirmative/completed visual modifier uses \`--facodi-mint\`;
- informational modifier uses \`--facodi-cyan\`;
- reference rail uses 4-column desktop concept only through parent grid; it must become normal flow on mobile;
- every grid/flex child likely to hold record titles gets \`min-width: 0\`;
- labels/titles use \`overflow-wrap: anywhere\`.

Do not add any domain data or QWeb here.

- [ ] **Step 4: Load the D1 stylesheet and bump theme release**

In \`theme_facodi/__manifest__.py\`:
- set version to \`19.0.8.0.0\`;
- load \`learning_interfaces.scss\` after \`paper_primitives.scss\` and before page-specific \`website_slides.scss\` / \`curriculum.scss\`.

Update \`tests/test_module_contract.sh\` to require the stylesheet and version.

- [ ] **Step 5: Pin mobile source contracts**

Extend \`tests/test_mobile_interaction_contract.sh\` to require the D1 stylesheet's 320-friendly single-column behavior and overflow wrapping.

- [ ] **Step 6: Run GREEN**

~~~bash
bash tests/test_learning_interfaces_contract.sh
bash tests/test_module_contract.sh
bash tests/test_mobile_interaction_contract.sh
~~~

Expected: PASS.

- [ ] **Step 7: Commit**

~~~bash
git add theme_facodi/static/src/scss/learning_interfaces.scss \
  theme_facodi/__manifest__.py tests/test_learning_interfaces_contract.sh \
  tests/test_module_contract.sh tests/test_mobile_interaction_contract.sh
git commit -m "feat(theme): add D1 learning interface primitives"
~~~

---

### Task 2: Refactor the real Odoo course catalogue and course detail in facodi-theme

**Repository:** \`marcelo-m7/facodi-theme\`

**Files:**
- Modify: \`theme_facodi/views/website_slides.xml\`
- Modify: \`theme_facodi/static/src/scss/website_slides.scss\`
- Modify: \`tests/test_elearning_catalog_style_contract.sh\`
- Modify: \`theme_facodi/tests/test_website.py\`

**Interfaces:**
- Consumes: Task 1 D1 primitives and native Odoo \`website_slides\` templates.
- Produces semantic hooks: \`.facodi-learning-catalogue-hero\`, \`.facodi-index-tabs--courses\`, \`.facodi-course-record-card\`, \`.facodi-course-study-shell\`.

- [ ] **Step 1: Write failing native course assertions**

Extend \`tests/test_elearning_catalog_style_contract.sh\` to require:
- D1 catalogue hero/index-tab selectors;
- \`.facodi-course-record-card\`;
- \`.facodi-course-study-shell\`;
- native \`.o_wslides_course_card\`, join/done links, lesson links and course nav still present;
- the exact default-cover selector remains the only forced \`background-image: ... !important\` override for \`slide.channel\`.

Add a guard that \`website_slides.xml\` does not contain fabricated static course codes, instructor names, enrolment counts or progress percentages.

- [ ] **Step 2: Run RED**

~~~bash
bash tests/test_elearning_catalog_style_contract.sh
~~~

Expected: FAIL on the new D1 hooks.

- [ ] **Step 3: Add catalogue semantic hooks through QWeb inheritance**

In \`theme_facodi/views/website_slides.xml\`:
- preserve existing \`courses_home\`, \`courses_search_results\` and \`course_card\` inheritance;
- add the D1 hero/index navigation around the catalogue using real links \`/slides\`, \`/roadmaps\`, \`/unidades-curriculares\`;
- add \`facodi-course-record-card\` to the native course-card wrapper rather than replacing the card's model-backed content;
- preserve native search/filter widgets.

Any new source copy must be English and must be added to POT/PT/ES/FR in the same task.

- [ ] **Step 4: Add course-detail semantic shell hooks**

Through existing native course template inheritance:
- add \`facodi-course-study-shell\` to the course-detail content area;
- style native course metadata, nav, progress, category headers and lesson rows using Task 1 primitives;
- keep native join/enrolment/progress/lesson links intact.

Do not compute progress or module state in QWeb.

- [ ] **Step 5: Preserve custom-cover safety**

Keep the existing exact default-gradient override. Add a static contract that fails if a generic selector such as:

~~~scss
.o_record_cover_container[data-res-model="slide.channel"] {
    background-image: ... !important;
}
~~~

appears.

- [ ] **Step 6: Add rendered/compiled assertions**

In \`theme_facodi/tests/test_website.py\`:
- assert \`/slides\` returns 200;
- compiled CSS contains all four D1 course selectors;
- dynamic catalogue continues to contain no invented course data;
- existing custom-cover/default-cover tests remain green.

- [ ] **Step 7: Run GREEN**

~~~bash
bash tests/test_elearning_catalog_style_contract.sh
bash tests/test_learning_interfaces_contract.sh
bash tests/test_mobile_interaction_contract.sh
bash tests/test_i18n_contract.sh
~~~

Then require exact-head \`Odoo 19 Theme CI\` success.

- [ ] **Step 8: Commit**

~~~bash
git add theme_facodi/views/website_slides.xml \
  theme_facodi/static/src/scss/website_slides.scss \
  theme_facodi/tests/test_website.py tests/test_elearning_catalog_style_contract.sh
git commit -m "feat(elearning): redesign FACODI course surfaces for D1"
~~~

---

### Task 3: Restructure Roadmap and Curricular Unit catalogues in facodi-learning

**Repository:** \`marcelo-m7/facodi-learning\`

**Files:**
- Create: \`facodi_learning/tests/test_learning_interfaces_contract.py\`
- Modify: \`facodi_learning/views/website_curriculum.xml\`
- Modify: \`facodi_learning/tests/test_curriculum_ui.py\`
- Modify: \`facodi_learning/tests/test_website_i18n_contract.py\`

**Interfaces:**
- Produces semantic hooks consumed by theme Task 6:
  - \`.facodi-learning-hero\`;
  - \`.facodi-index-tabs\`;
  - \`.facodi-filter-sheet\`;
  - \`.facodi-record-card\`;
  - modifiers \`--roadmap\` and \`--unit\`.
- Preserves all controller query parameters and record projections.

- [ ] **Step 1: Write failing catalogue QWeb tests**

Create \`test_learning_interfaces_contract.py\` using plain file/XML assertions plus Odoo view assertions.

Pin:
- \`curriculum_public_index\` includes \`facodi-learning-hero\`, \`facodi-index-tabs\`, \`facodi-record-card--roadmap\`;
- \`curriculum_public_unit_index\` includes \`facodi-learning-hero\`, \`facodi-index-tabs\`, \`facodi-filter-sheet\`, \`facodi-record-card--unit\`;
- existing filter names \`reference_id\`, \`curricular_year\`, \`period\`, \`credits\` remain;
- existing real values \`published_course_count\`, \`coverage_status\`, \`unit_url\` remain;
- unsupported Stitch strings are absent.

- [ ] **Step 2: Run RED**

Run the standalone contract first:

~~~bash
python facodi_learning/tests/test_learning_interfaces_contract.py
~~~

Expected: FAIL on missing D1 classes.

- [ ] **Step 3: Refactor Roadmap catalogue markup only**

In \`curriculum_public_index\`:
- wrap existing real heading/lead/reference records in the D1 hero + index tabs;
- transform each existing Roadmap card into \`facodi-record-card facodi-record-card--roadmap\`;
- retain institution/programme/academic-year/programme-code values already emitted;
- retain existing Roadmap URL and public visibility conditions;
- do not add static counts.

- [ ] **Step 4: Refactor UC catalogue markup only**

In \`curriculum_public_unit_index\`:
- add D1 hero/index tabs;
- apply \`facodi-filter-sheet\` to the existing form without renaming fields;
- change each existing unit result to \`facodi-record-card facodi-record-card--unit\`;
- preserve real code/year/ECTS/coverage/published-course-count/detail/contribution data;
- omit optional metadata when false rather than rendering empty placeholders.

- [ ] **Step 5: Extend Odoo UI contract**

In \`test_curriculum_ui.py\`, assert the loaded QWeb views contain the D1 hooks and still contain:
- \`website.layout\`;
- \`/unidades-curriculares\`;
- \`reference_id\`;
- \`period\`;
- no direct \`slide.slide\` or coverage-model ORM reference.

- [ ] **Step 6: Keep source copy and i18n stable**

If no source copy changes, extend \`test_website_i18n_contract.py\` only with unsupported-feature absence checks.

If source copy changes, update \`facodi_learning.pot\`, \`pt.po\`, \`es.po\`, \`fr.po\` and add exact assertions before continuing.

- [ ] **Step 7: Run GREEN**

~~~bash
python facodi_learning/tests/test_learning_interfaces_contract.py
python facodi_learning/tests/test_website_i18n_contract.py
~~~

Then require the relevant Odoo test classes through the repository CI.

- [ ] **Step 8: Commit**

~~~bash
git add facodi_learning/views/website_curriculum.xml \
  facodi_learning/tests/test_learning_interfaces_contract.py \
  facodi_learning/tests/test_curriculum_ui.py \
  facodi_learning/tests/test_website_i18n_contract.py
git commit -m "feat(curriculum): redesign D1 learning catalogues"
~~~

---

### Task 4: Refactor Roadmap detail, Curricular Unit detail and module detail in facodi-learning

**Repository:** \`marcelo-m7/facodi-learning\`

**Files:**
- Modify: \`facodi_learning/views/website_curriculum.xml\`
- Modify: \`facodi_learning/tests/test_learning_interfaces_contract.py\`
- Modify: \`facodi_learning/tests/test_curriculum_public_units.py\`
- Modify: \`facodi_learning/tests/test_curriculum_module.py\`
- Modify: \`facodi_learning/tests/test_curriculum_ui.py\`

**Interfaces:**
- Consumes existing controller projections: \`unit_matrix_groups\`, \`coverage_rows\`, \`learning['modules']\`, \`learning['progress_percent']\`, \`learning['next_item']\`, module public projection.
- Produces hooks:
  - \`.facodi-roadmap-study-path\`;
  - \`.facodi-unit-layout\`;
  - \`.facodi-unit-main\`;
  - \`.facodi-reference-rail\`;
  - \`.facodi-module-stack\`;
  - \`.facodi-module-detail\`;
  - \`.facodi-open-callout\`.

- [ ] **Step 1: Add failing detail-view contract**

Extend \`test_learning_interfaces_contract.py\` to require:
- Roadmap detail: \`facodi-roadmap-study-path\` and existing \`unit_matrix_groups\`;
- UC detail: \`facodi-unit-layout\`, \`facodi-unit-main\`, \`facodi-reference-rail\`, \`facodi-module-stack\`, \`facodi-open-callout\`;
- module detail: \`facodi-module-detail\`;
- no unsupported notes/forum/bibliography strings.

- [ ] **Step 2: Pin missing optional metadata behavior**

Add assertions to \`test_curriculum_public_units.py\` that the unit template uses QWeb conditionals for optional:
- \`unit.credits\`;
- \`unit.option_group\`;
- \`unit.classification\`.

The test must not require these values to exist.

- [ ] **Step 3: Pin public vs authenticated progress semantics**

In \`test_curriculum_module.py\`, retain existing projection tests and add UI-facing assertions that:
- public projection does not invent completion/current state;
- progress/next-item rendering remains guarded by existing authenticated \`show_learning_progress\`/projection values;
- neutral module rows remain available when progress is absent.

Do not change model methods unless a failing existing behavior proves a real bug.

- [ ] **Step 4: Refactor Roadmap detail**

In \`curriculum_public_detail\`:
- preserve source/provenance header;
- render existing year/period grouping as \`facodi-roadmap-study-path\`;
- give each real unit row a D1 record/study-row wrapper;
- keep coverage rows, modules, unit URLs and official source values intact;
- do not draw prerequisite semantics not present in the projection.

- [ ] **Step 5: Refactor UC detail into the 8/4 semantic composition**

In \`curriculum_public_unit\`:
- outer \`facodi-unit-layout\`;
- main column \`facodi-unit-main\`;
- side \`facodi-reference-rail\`;
- move only already-rendered data into those regions.

Main column order:
1. learning pathway/modules;
2. real progress/next item when present;
3. reviewed course coverage;
4. truthful gap state with contribution CTA.

Rail content:
- source/provenance;
- ECTS/year/period/classification/group only when available;
- coverage status and real related published-course count;
- contribution CTA.

Do not add coordinator, cohort size, workload hours, notebook, forum or bibliography.

- [ ] **Step 6: Refactor module detail**

In \`curriculum_public_module\`:
- apply \`facodi-module-detail\`;
- retain breadcrumb/title/description/progress/next-item/item list;
- render empty module as a neutral paper note;
- do not infer sequence/completion beyond the existing public projection.

- [ ] **Step 7: Run GREEN**

~~~bash
python facodi_learning/tests/test_learning_interfaces_contract.py
python facodi_learning/tests/test_website_i18n_contract.py
~~~

Then run repository CI including:
- \`TestCurriculumPublicUnits\`;
- \`TestCurriculumModule\`;
- \`TestCurriculumUI\`.

If the current CI tag list does not execute these classes, extend the CI test-tag list in this task so D1 cannot merge without them.

- [ ] **Step 8: Commit**

~~~bash
git add facodi_learning/views/website_curriculum.xml \
  facodi_learning/tests/test_learning_interfaces_contract.py \
  facodi_learning/tests/test_curriculum_public_units.py \
  facodi_learning/tests/test_curriculum_module.py \
  facodi_learning/tests/test_curriculum_ui.py .github/workflows/ci.yml
git commit -m "feat(curriculum): redesign D1 Roadmap unit and module detail"
~~~

---

### Task 5: Refactor curriculum alignment on native course pages in facodi-learning

**Repository:** \`marcelo-m7/facodi-learning\`

**Files:**
- Modify: \`facodi_learning/views/website_slides.xml\`
- Modify: \`facodi_learning/tests/test_learning_interfaces_contract.py\`
- Modify: \`facodi_learning/tests/test_website_i18n_contract.py\`

**Interfaces:**
- Produces \`.facodi-course-alignment-sheet\` and \`.facodi-open-callout\` hooks for Task 6 theme styling.
- Preserves \`approved_course_curriculum_links\` model-backed values and existing contribution routes.

- [ ] **Step 1: Add failing alignment contract**

Require \`website_slides.xml\` to include:
- \`facodi-course-alignment-sheet\`;
- \`facodi-open-callout\`;
- existing unit URL/course mapping values;
- existing “Content correspondence - not academic equivalence” boundary wording;
- existing \`/contribuir/recurso\` routes.

- [ ] **Step 2: Run RED**

~~~bash
python facodi_learning/tests/test_learning_interfaces_contract.py
~~~

Expected: FAIL on alignment hooks.

- [ ] **Step 3: Add semantic wrappers only**

Refactor the existing curriculum-alignment block:
- paper reference sheet around reviewed curriculum relations;
- each related unit keeps name/programme/year/relation badge/link;
- contribution CTA becomes \`facodi-open-callout\`;
- no new query/model field.

- [ ] **Step 4: Run i18n/boundary checks**

~~~bash
python facodi_learning/tests/test_website_i18n_contract.py
~~~

Expected: PASS. If source copy changed, update all four catalogues first.

- [ ] **Step 5: Commit**

~~~bash
git add facodi_learning/views/website_slides.xml \
  facodi_learning/tests/test_learning_interfaces_contract.py \
  facodi_learning/tests/test_website_i18n_contract.py
git commit -m "feat(elearning): align course curriculum panels with D1"
~~~

---

### Task 6: Style facodi-learning D1 hooks and finish theme release

**Repository:** \`marcelo-m7/facodi-theme\`

**Files:**
- Modify: \`theme_facodi/static/src/scss/curriculum.scss\`
- Modify: \`theme_facodi/static/src/scss/website_slides.scss\`
- Modify: \`tests/test_learning_interfaces_contract.sh\`
- Modify: \`tests/test_curriculum_style_contract.sh\`
- Modify: \`theme_facodi/tests/test_website.py\`
- Modify: \`.github/workflows/ci.yml\`
- Modify: \`README.md\`
- Modify: \`docs/validation.md\`

**Interfaces:**
- Consumes every semantic hook produced by Tasks 3–5.
- Produces final D1 responsive presentation in \`theme_facodi 19.0.8.0.0\`.

- [ ] **Step 1: Add failing style coverage for all learning hooks**

Extend theme contracts to require selectors for:
- Roadmap/UC catalogue hooks;
- \`facodi-roadmap-study-path\`;
- \`facodi-unit-layout\` with desktop \`minmax(0, 8fr) minmax(18rem, 4fr)\`-equivalent ratio;
- \`facodi-reference-rail\`;
- \`facodi-module-stack\`;
- \`facodi-module-detail\`;
- \`facodi-course-alignment-sheet\`;
- \`facodi-open-callout\`.

Require mobile collapse to one column at \`767.98px\`.

- [ ] **Step 2: Run RED**

~~~bash
bash tests/test_learning_interfaces_contract.sh
bash tests/test_curriculum_style_contract.sh
~~~

Expected: FAIL on new selectors/layout.

- [ ] **Step 3: Implement catalogue/card/filter presentation**

In \`curriculum.scss\`, style:
- learning hero;
- index tabs;
- filter sheet;
- record cards;
- coverage badges;
- result grids.

Use only shared semantic tokens and Task 1 primitives.

- [ ] **Step 4: Implement Roadmap/UC/module detail layout**

Pinned responsive behavior:
- desktop UC detail uses two columns approximating 8/4;
- <= 1023px may collapse rail below main if content becomes cramped;
- <= 767.98px is one column;
- all nested title containers \`min-width: 0\`;
- tables scroll internally;
- tabs may horizontally scroll inside their own contained element but never widen the page.

- [ ] **Step 5: Implement semantic state styling**

- completed/affirmative modifier = mint;
- active/next = yellow;
- informational/reference = cyan;
- attention/review only where corresponding real semantic class exists.

Do not derive state in CSS from DOM position.

- [ ] **Step 6: Update compiled asset/runtime tests and documentation**

In \`test_website.py\`, require compiled CSS to contain every final D1 selector.

Update README and \`docs/validation.md\` with:
- D1 route families;
- no-fake-feature policy;
- custom-cover guarantee;
- 320 px hard gate;
- cross-repo integration requirement.

Ensure \`.github/workflows/ci.yml\` still validates version \`19.0.8.0.0\`.

- [ ] **Step 7: Run complete theme gate**

~~~bash
bash tests/test_module_contract.sh
bash tests/test_campus_paper_contract.sh
bash tests/test_global_shell_contract.sh
bash tests/test_homepage_dashboard_contract.sh
bash tests/test_foundation_v2_contract.sh
bash tests/test_curriculum_style_contract.sh
bash tests/test_learning_interfaces_contract.sh
bash tests/test_i18n_contract.sh
bash tests/test_elearning_catalog_style_contract.sh
bash tests/test_mobile_interaction_contract.sh
~~~

Require exact-head \`Odoo 19 Theme CI\` success.

- [ ] **Step 8: Commit**

~~~bash
git add theme_facodi/static/src/scss/curriculum.scss \
  theme_facodi/static/src/scss/website_slides.scss \
  theme_facodi/tests/test_website.py tests \
  .github/workflows/ci.yml README.md docs/validation.md
git commit -m "feat(theme): complete D1 learning interface presentation"
~~~

---

### Task 7: Finish facodi-learning release, i18n and upgrade gates

**Repository:** \`marcelo-m7/facodi-learning\`

**Files:**
- Modify: \`facodi_learning/__manifest__.py\`
- Modify: \`facodi_learning/tests/test_learning_interfaces_contract.py\`
- Modify: \`facodi_learning/tests/test_website_i18n_contract.py\`
- Modify PO/POT files only if source copy changed
- Modify: \`.github/workflows/ci.yml\`
- Modify: \`README.md\` or release documentation if the repository has a current-release section

**Interfaces:**
- Produces exact green \`facodi_learning 19.0.1.22.0\` SHA for integration Task 8.

- [ ] **Step 1: Add failing release assertion**

Require manifest version \`19.0.1.22.0\` in the D1 contract or CI.

- [ ] **Step 2: Run RED**

~~~bash
python facodi_learning/tests/test_learning_interfaces_contract.py
~~~

Expected: FAIL on release version until bumped.

- [ ] **Step 3: Bump manifest and ensure D1 test classes run in CI**

Set:

~~~python
"version": "19.0.1.22.0",
~~~

Ensure CI's Odoo test tags execute:
- \`TestCurriculumUI\`;
- \`TestCurriculumPublicUnits\`;
- \`TestCurriculumModule\`;
plus existing governance/security suites.

- [ ] **Step 4: Verify translations**

~~~bash
python facodi_learning/tests/test_website_i18n_contract.py
~~~

All PT/ES/FR source strings must be present when copy changed; otherwise catalogues should remain untouched.

- [ ] **Step 5: Require complete exact-head CI**

Require:
- provider-neutral policy;
- curriculum fixture validation;
- website/i18n contract;
- pre-M3.4 upgrade fixture;
- D1 Odoo test classes;
- existing security/publication suites.

- [ ] **Step 6: Commit**

~~~bash
git add facodi_learning/__manifest__.py facodi_learning/tests \
  .github/workflows/ci.yml facodi_learning/i18n
git commit -m "test(learning): release D1 learning interfaces"
~~~

Do not add unchanged i18n files to the commit.

---

### Task 8: Prove cross-repo D1 integration without promoting production

**Repository:** \`marcelo-m7/facodi-deploy\` on branch \`test/facodi-learning-interfaces-d1-integration\`

**Files:**
- Modify gitlink: \`addons/facodi-theme\` → exact green Task 6 SHA.
- Modify gitlink: \`addons/facodi-learning\` → exact green Task 7 SHA.
- Extend existing browser/runtime acceptance only if the D1 selectors/routes are not already covered.
- Do not merge this branch to \`main\`.

**Interfaces:**
- Consumes exact green owner-repository SHAs.
- Produces integrated D1 acceptance evidence; no production promotion.

- [ ] **Step 1: Create integration branch from current facodi-deploy main**

Do not reuse the pending production Phase C branch if its pins no longer match D1.

- [ ] **Step 2: Pin exactly two gitlinks**

Change only:
- \`addons/facodi-theme\`;
- \`addons/facodi-learning\`.

Assert via \`git diff --submodule=log\` that no other gitlink changed.

- [ ] **Step 3: Extend browser assertions for D1 if needed**

Required runtime hooks:
- \`/slides\`: D1 catalogue hero/index tabs/course record cards;
- real course: D1 course study shell + curriculum alignment;
- \`/roadmaps\`: D1 hero/record cards;
- Roadmap detail: D1 study path;
- \`/unidades-curriculares\`: D1 filter sheet/unit cards;
- UC detail: D1 8/4 layout/reference rail/module stack;
- module detail: D1 module detail.

Required widths:
- 1440;
- 1024 where relevant;
- 390;
- 320.

Fail on \`document.documentElement.scrollWidth > window.innerWidth + 1\`.

- [ ] **Step 4: Run disposable integration gate**

~~~bash
git submodule update --init --recursive
bash scripts/validate-repository.sh
docker compose --env-file .env.ci -f deploy/coolify/docker-compose.yml config --quiet
python3 -m unittest tests/test_repository_contract.py tests/test_migration_contract.py -v
bash tests/test_coolify_runtime.sh
~~~

GitHub Actions must run browser acceptance on the exact integration head and upload screenshots.

- [ ] **Step 5: Review screenshot evidence and exact pins**

Record:
- theme SHA/version;
- learning SHA/version;
- CI run;
- screenshot artifact;
- route/viewports checked;
- no page-level 320 px overflow.

- [ ] **Step 6: Stop before deployment promotion**

D1 is complete at this point.

Do not merge \`facodi-deploy/main\`. A separate deployment-promotion decision updates/rebases the Phase C plan using the exact D1 green SHAs.

## Final D1 Verification

### facodi-theme

~~~bash
bash tests/test_module_contract.sh
bash tests/test_campus_paper_contract.sh
bash tests/test_global_shell_contract.sh
bash tests/test_homepage_dashboard_contract.sh
bash tests/test_foundation_v2_contract.sh
bash tests/test_curriculum_style_contract.sh
bash tests/test_learning_interfaces_contract.sh
bash tests/test_i18n_contract.sh
bash tests/test_elearning_catalog_style_contract.sh
bash tests/test_mobile_interaction_contract.sh
~~~

Require exact-head Odoo 19 Theme CI green.

### facodi-learning

~~~bash
python facodi_learning/tests/test_learning_interfaces_contract.py
python facodi_learning/tests/test_website_i18n_contract.py
python scripts/validate_curriculum_fixture.py
~~~

Require exact-head Odoo 19 CI green, including the D1 public curriculum classes.

### integrated disposable runtime

Require the exact two green addon SHAs to pass the facodi-deploy repository/Compose/migration/runtime/browser gates with the 320 px overflow check.

## D1 Completion Boundary

D1 is complete when:

- \`theme_facodi 19.0.8.0.0\` implements the reusable learning-interface system and native Odoo course surfaces;
- \`facodi_learning 19.0.1.22.0\` emits the approved semantic QWeb structure without changing business/security/provenance behavior;
- catalogue, course, Roadmap, UC and module surfaces use one coherent Stitch-informed Campus Paper/fichário vocabulary;
- unsupported Stitch features remain absent;
- custom Odoo course covers remain intact;
- PT/ES/FR remain native and green;
- authenticated progress/current/next state remains model/projection-backed;
- no learning page has page-level horizontal overflow at 320 px in the integrated runtime;
- both owner repositories and the disposable cross-repo integration branch are green;
- no production deployment has been triggered.
