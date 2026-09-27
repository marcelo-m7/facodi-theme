# FACODI Study Player Shell Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a FACODI Campus Paper / Digital Highlighter study shell around the native Odoo 19 `website_slides` lesson experience without replacing Odoo progress, access, media, quiz or navigation behavior.

**Architecture:** `theme_facodi` remains presentation-only. The implementation adds focused QWeb inheritance, a dedicated player SCSS file and progressive-enhancement JavaScript; native `slide.channel`, `slide.slide`, controllers and completion logic stay authoritative. Supabase and `facodi-deploy` are read-only dependencies for this phase: no schema/function/deployment changes are part of the feature.

**Tech Stack:** Odoo 19 Community, QWeb/XML, SCSS, browser JavaScript, Odoo HttpCase/lxml tests, Bash static contract tests.

**Spec:** `docs/superpowers/specs/2026-09-27-facodi-study-player-shell-design.md`

## Global Constraints

- Preserve native Odoo enrolment, access, lesson completion, course completion, progress, media rendering, quiz behavior, lesson routing and course navigation.
- Do not add new `slide.channel` or `slide.slide` fields, controllers, RPC endpoints or ORM searches in player QWeb.
- Do not introduce Supabase calls, AI generation or private notes persistence in this release.
- Do not fabricate progress, duration, authors, resources or lesson metadata.
- JavaScript is presentation-only and the page must remain functional when it fails or is disabled.
- Reuse existing FACODI Campus Paper / Highlighter tokens and accessible focus/reduced-motion conventions.
- Do not modify `marcelo-m7/facodi-deploy` for this feature; it already consumes `addons/facodi-theme` as a submodule.
- Do not modify the Supabase FACODI project in this phase. Existing Edge Functions remain untouched and are only a future integration target.

## Review Focus

- Native Odoo lesson markup differs by content type (video/article/document/quiz): FACODI wrappers must not assume one media DOM shape.
- Anonymous vs authenticated users can receive different controls: the shell must not hide join/completion/access controls.
- A course may have no optional resources or no previous/next lesson: render honest empty/absent states rather than fake actions.
- Mobile drawer/tab enhancements may fail or be disabled: native links and lesson content must remain reachable without JavaScript.
- Localized routes such as `/pt/...` must preserve native links and not hard-code English-only navigation paths.

---

### Task 1: Lock the native player extension contract with failing rendering tests

**Files:**
- Create: `theme_facodi/tests/test_study_player_rendering.py`
- Reference: `theme_facodi/tests/test_elearning_catalog_rendering.py`
- Reference: `theme_facodi/views/website_slides.xml`

**Interfaces:**
- Consumes: native Odoo `slide.channel`, `slide.slide`, existing test helpers/patterns from `test_elearning_catalog_rendering.py`.
- Produces: a rendering contract requiring `.facodi-study-player`, native lesson links/content hooks, inert AI hooks, honest empty resource state and localized/authenticated preservation.

- [ ] **Step 1: Write failing HttpCase tests for the study-player shell**

Create `TestFacodiStudyPlayerRendering(HttpCase)` with helpers equivalent to the existing eLearning tests and assertions covering:
- a public training course with video/article/quiz content;
- lesson page contains a `facodi-study-player` root;
- native `o_wslides_js_slides_list_slide_link` lesson links remain present;
- native lesson content/player container remains present;
- AI controls expose `data-facodi-ai-action` and are disabled or marked inactive;
- resource panel renders an honest empty state when no native resource is available;
- authenticated rendering still exposes native completion/join behavior when applicable;
- Portuguese route preserves localized/native lesson links.

- [ ] **Step 2: Run the new test and verify it fails**

Run the Odoo test target used by this repository for `theme_facodi.tests.test_study_player_rendering`.

Expected: FAIL because `facodi-study-player` and utility panel hooks do not exist yet.

- [ ] **Step 3: Commit the failing test contract**

```bash
git add theme_facodi/tests/test_study_player_rendering.py
git commit -m "test: define FACODI study player rendering contract"
```

---

### Task 2: Add a minimal QWeb study shell while preserving native Odoo behavior

**Files:**
- Create: `theme_facodi/views/website_slides_player.xml`
- Modify: `theme_facodi/__manifest__.py`
- Test: `theme_facodi/tests/test_study_player_rendering.py`

**Interfaces:**
- Consumes: stable native `website_slides` templates/hooks discovered from Odoo 19 and current FACODI inheritance.
- Produces: semantic root/wrappers and utility-panel markup used by SCSS and JavaScript:
  - `.facodi-study-player`
  - `.facodi-study-player__content`
  - `.facodi-study-player__index`
  - `.facodi-study-tools`
  - `[data-facodi-study-panel]`
  - `[data-facodi-ai-action]`

- [ ] **Step 1: Inspect the exact native Odoo 19 lesson template names and extension points**

Use the vendored Odoo source / installed source already used by the project. Record the template ids and choose the narrowest stable XPaths; do not replace broad page sections.

- [ ] **Step 2: Register `views/website_slides_player.xml` in the manifest**

Place it immediately after `views/website_slides.xml` so existing course/catalog inheritance remains established first.

- [ ] **Step 3: Implement minimal QWeb wrappers and utility panels**

Add only presentation-semantic markup:
- study-player root around the native lesson surface;
- course-index wrapper around existing native lesson navigation;
- utility panel region for About, Resources, Notes and AI;
- Notes clearly marked unavailable/not persisted;
- AI actions disabled/inert with stable `data-facodi-ai-action` values;
- no ORM `.search(` calls;
- no fabricated resource list;
- no hard-coded previous/next URLs.

- [ ] **Step 4: Run the rendering tests**

Expected: Task 1 tests PASS for structure, native hooks, inactive AI and fallback states.

- [ ] **Step 5: Run existing eLearning rendering tests**

Expected: existing catalogue/training/documentation tests remain PASS.

- [ ] **Step 6: Commit QWeb shell**

```bash
git add theme_facodi/views/website_slides_player.xml theme_facodi/__manifest__.py theme_facodi/tests/test_study_player_rendering.py
git commit -m "feat: add native FACODI study player shell"
```

---

### Task 3: Add dedicated Campus Paper player styling and responsive behavior

**Files:**
- Create: `theme_facodi/static/src/scss/website_slides_player.scss`
- Modify: `theme_facodi/__manifest__.py`
- Create: `tests/test_study_player_style_contract.sh`
- Reference: `theme_facodi/static/src/scss/campus_paper_tokens.scss`
- Reference: `theme_facodi/static/src/scss/website_slides.scss`

**Interfaces:**
- Consumes: QWeb class hooks from Task 2 and existing FACODI CSS custom properties.
- Produces: desktop/tablet/mobile visual system with no behavioral dependency on JavaScript.

- [ ] **Step 1: Write the failing static style contract**

Assert:
- `website_slides_player.scss` exists and is registered in `web.assets_frontend`;
- required selectors for root/content/index/tools exist;
- shared FACODI tokens such as `var(--facodi-ink)`, `var(--facodi-sun)`, `var(--facodi-mint)`, `var(--facodi-shadow)` are used;
- mobile breakpoint behavior exists;
- `:focus-visible` exists;
- `prefers-reduced-motion` exists;
- no remote font/CDN URLs exist;
- no Supabase URL/client text exists.

- [ ] **Step 2: Run the style contract and verify it fails**

Run:

```bash
bash tests/test_study_player_style_contract.sh
```

Expected: FAIL because the stylesheet is not present.

- [ ] **Step 3: Implement player SCSS using existing FACODI tokens**

Style:
- paper/grid page treatment;
- prominent native lesson content/player sheet;
- bordered/hard-shadow course index;
- current/completed/native lesson states using existing upstream classes only;
- horizontally safe utility tabs;
- stacked mobile layout;
- touch-safe controls;
- no fixed layer over native fullscreen/video controls.

- [ ] **Step 4: Register the stylesheet after `website_slides.scss`**

This makes the player layer focused and intentionally later in cascade order.

- [ ] **Step 5: Run style and existing eLearning contracts**

Expected: PASS.

- [ ] **Step 6: Commit player styling**

```bash
git add theme_facodi/static/src/scss/website_slides_player.scss theme_facodi/__manifest__.py tests/test_study_player_style_contract.sh
git commit -m "style: add FACODI study player interface"
```

---

### Task 4: Add progressive-enhancement interactions without touching course state

**Files:**
- Create: `theme_facodi/static/src/js/facodi_study_player.js`
- Modify: `theme_facodi/__manifest__.py`
- Create: `tests/test_study_player_js_contract.py`
- Modify: `theme_facodi/views/website_slides_player.xml`

**Interfaces:**
- Consumes: Task 2 data hooks and native lesson links.
- Produces: presentation-only client behavior:
  - drawer toggle via `[data-facodi-index-toggle]`;
  - local panels via `[data-facodi-study-tab]` / `[data-facodi-study-panel]`;
  - active lesson scroll via native active/current selector plus FACODI wrapper.

- [ ] **Step 1: Write failing JS source-contract tests**

Assert the JS:
- initializes only under `.facodi-study-player`;
- uses no `rpc`, `fetch(`, Supabase client or completion endpoint;
- updates `aria-expanded` for the index toggle;
- supports keyboard/tab semantics;
- uses `scrollIntoView` only as progressive enhancement;
- stores at most non-sensitive presentation preference keys prefixed `facodi.study.`.

- [ ] **Step 2: Run the JS contract and verify it fails**

Run the repository Python test command for `tests/test_study_player_js_contract.py`.

Expected: FAIL because the JS file does not exist.

- [ ] **Step 3: Add QWeb interaction hooks**

Add the index toggle and tab controls with correct `aria-controls`, `aria-expanded`, roles and stable ids. Native links remain unchanged.

- [ ] **Step 4: Implement `facodi_study_player.js`**

Implement only:
- scoped initialization;
- mobile index open/close;
- local panel switching;
- focus management;
- active lesson `scrollIntoView({block: "nearest"})`;
- optional UI preference persistence.

Do not call Odoo RPC, Supabase, media APIs or completion actions.

- [ ] **Step 5: Register JS in `web.assets_frontend`**

Load it after the player SCSS entry.

- [ ] **Step 6: Run JS, rendering and style contracts**

Expected: PASS.

- [ ] **Step 7: Commit progressive interactions**

```bash
git add theme_facodi/static/src/js/facodi_study_player.js theme_facodi/views/website_slides_player.xml theme_facodi/__manifest__.py tests/test_study_player_js_contract.py
git commit -m "feat: enhance FACODI study player interactions"
```

---

### Task 5: Add safe contribution CTAs only where existing routes are proven

**Files:**
- Modify: `theme_facodi/views/website_slides_player.xml`
- Modify: `theme_facodi/tests/test_study_player_rendering.py`
- Reference/Search: current FACODI contribution/contact route definitions in `facodi-theme` and `facodi-learning`

**Interfaces:**
- Consumes: existing real public contribution/contact routes only.
- Produces: optional “Suggest improvement” and “Report a problem” lesson CTAs with context query parameters only if those routes already support them safely.

- [ ] **Step 1: Locate existing real contribution/contact routes**

Search current code for the routes backing the site's contribution and contact forms.

Expected: identify the canonical URL(s) and supported query parameters, or conclude no safe route exists.

- [ ] **Step 2: Add a failing rendering assertion for the proven route behavior**

If a real supported route exists, assert the CTA uses it and does not invent a new endpoint.

If none exists, assert the player contains no fake contribution endpoint and keep the CTA out of this release.

- [ ] **Step 3: Implement the minimal route-backed CTA behavior**

No controller/backend changes.

- [ ] **Step 4: Run rendering tests**

Expected: PASS.

- [ ] **Step 5: Commit contribution integration**

```bash
git add theme_facodi/views/website_slides_player.xml theme_facodi/tests/test_study_player_rendering.py
git commit -m "feat: connect study player contribution actions"
```

---

### Task 6: Full regression verification and branch handoff

**Files:**
- Modify if needed: `docs/validation.md`
- No changes: `marcelo-m7/facodi-deploy`
- No changes: Supabase project `bhfywztfyidvrlarebmg`

**Interfaces:**
- Consumes: completed Study Player implementation from Tasks 1–5.
- Produces: a branch ready for independent review/PR, with explicit evidence that deployment/Supabase scope stayed unchanged.

- [ ] **Step 1: Run all FACODI theme static contracts**

Include existing eLearning catalogue tests plus new player style/JS contracts.

Expected: PASS.

- [ ] **Step 2: Run Odoo `theme_facodi` rendering tests**

Include existing `test_elearning_catalog_rendering.py` and new `test_study_player_rendering.py`.

Expected: PASS.

- [ ] **Step 3: Validate JavaScript-disabled baseline**

Render/access the lesson page without relying on FACODI JS and confirm:
- native lesson links work;
- lesson content renders;
- native completion/access controls remain available;
- utility panels degrade to visible/stacked content.

- [ ] **Step 4: Validate representative viewport/content matrix**

Check at least:
- desktop video lesson;
- mobile video lesson;
- article/document lesson;
- quiz lesson;
- anonymous route;
- authenticated route;
- Portuguese localized route.

Expected: no clipping, no blocked native player controls, no broken navigation.

- [ ] **Step 5: Verify no Supabase or deployment mutation is required**

Confirm:
- no Supabase migration/function deployment was made;
- existing Supabase functions `v3_analyze_learning_resource` and `v3_discover_resource_metadata` remain untouched;
- `facodi-deploy` requires only a future submodule pointer bump after the theme PR is merged, not a feature-code change.

- [ ] **Step 6: Update validation documentation with exact commands/results**

Document only verified results.

- [ ] **Step 7: Commit validation evidence**

```bash
git add docs/validation.md
git commit -m "docs: validate FACODI study player shell"
```

- [ ] **Step 8: Open a pull request from `feat/facodi-study-player-shell` to `main`**

PR body should summarize:
- standard-first architecture;
- native behavior preserved;
- visual/UX changes;
- tests run;
- Supabase intentionally not integrated yet;
- `facodi-deploy` intentionally unchanged.

