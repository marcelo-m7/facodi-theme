# FACODI eLearning Catalogue and Dynamic Thumbnails Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modernize `/slides` and lesson presentation while resolving course visuals non-destructively from existing Odoo `website_slides` data.

**Architecture:** Keep `website_slides` authoritative. Add a presentation-only `slide.channel` batch helper in `theme_facodi`, focused QWeb inheritance for standard catalogue/course templates, and responsive SCSS. Derived thumbnails are render-time fallbacks only; no provider HTTP calls, no per-card ORM searches, no parallel catalogue, no persisted derived covers.

**Tech Stack:** Odoo 19 Community, `website_slides`, QWeb/XML inheritance, Bootstrap 5/Odoo Website, SCSS, Odoo `HttpCase`, Bash repository contracts, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-07-elearning-catalog-thumbnails-design.md`

## Global Constraints

- `theme_facodi` remains presentation-oriented.
- `website_slides` owns courses, lessons, routes, filters, pager, membership and progress.
- No new catalogue model, controller, route, cron or external thumbnail service.
- No `sudo()` to reveal private/unpublished learning content to public visitors.
- No HTTP calls to YouTube, Vimeo or Google Drive during catalogue rendering.
- No per-card ORM searches from QWeb.
- No writes to `slide.channel.image_1920` or `slide.slide.image_1920` for derived presentation.
- Preserve Website Builder, native translations, Bootstrap/Odoo conventions and standard JS hook classes.
- Prefer focused XPath inheritance; do not copy whole upstream templates.
- Keep the existing homepage dynamic course showcase behavior independent from `/slides` catalogue loading behavior.

---

### Task 1: Batch visual resolver

**Files:**
- Create: `theme_facodi/models/slide_channel.py`
- Modify: `theme_facodi/models/__init__.py`
- Modify: `theme_facodi/tests/test_website.py`

**Interfaces:**
- Consumes: standard `slide.channel.image_1920`, `slide.slide.image_1920`, `slide.slide.youtube_id`, `slide.slide.website_published`, `slide.slide.is_category`, `sequence`, `id`.
- Produces: `slide.channel._facodi_catalog_visuals()` returning `{channel_id: {"kind": str, "slide": record|False, "url": str|False, "alt": str}}` for the complete recordset.
- Produces: `slide.channel._facodi_has_explicit_cover()` boolean helper for a single channel without evaluating image widget placeholders.

- [ ] **Step 1: Write failing resolver tests**

Add focused tests to `theme_facodi/tests/test_website.py` creating channels/slides for explicit channel cover, stored slide image, YouTube-only slide, no-image fallback and unpublished/private slide exclusion. Assert exact `kind`, selected slide and URL.

Representative assertion shape:

```python
visuals = channels._facodi_catalog_visuals()
self.assertEqual(visuals[with_cover.id]["kind"], "channel")
self.assertEqual(visuals[with_slide_image.id]["kind"], "slide")
self.assertEqual(visuals[with_youtube.id]["kind"], "youtube")
self.assertEqual(
    visuals[with_youtube.id]["url"],
    "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
)
self.assertEqual(visuals[without_visual.id]["kind"], "fallback")
self.assertNotEqual(visuals[private_only.id].get("slide"), private_slide)
```

- [ ] **Step 2: Run CI/runtime tests and verify RED**

Push the test-only commit and run the repository's existing Odoo 19 CI. Expected failure: missing `_facodi_catalog_visuals` / `_facodi_has_explicit_cover`, not fixture or XML errors.

- [ ] **Step 3: Implement minimal batch resolver**

Create `theme_facodi/models/slide_channel.py` with `_inherit = "slide.channel"`.

Implementation rules:

```python
def _facodi_catalog_visuals(self):
    visuals = {
        channel.id: {"kind": "fallback", "slide": False, "url": False, "alt": channel.name or ""}
        for channel in self
    }
    # mark explicit channel covers first
    # one search for eligible slides across self.ids, ordered channel_id, sequence, id
    # first stored image candidate wins per uncovered channel
    # otherwise first valid youtube_id candidate wins
    # never call requests or sudo
    return visuals
```

Use one `slide.slide.search()` for all channels with domain including `channel_id in self.ids`, `is_category = False`, and visibility/publication conditions appropriate to the current user context. Prefer candidates with stored `image_1920` over YouTube-only candidates while preserving natural sequence within each class. Derive YouTube URL only from standard `youtube_id` and require exactly 11 safe ID characters.

- [ ] **Step 4: Register model import**

Update `theme_facodi/models/__init__.py` to import `slide_channel` alongside existing model modules.

- [ ] **Step 5: Run resolver tests and full runtime suite**

Expected: new resolver tests pass and existing theme tests remain green.

- [ ] **Step 6: Commit**

Commit message: `feat: resolve course visuals from learning content`

---

### Task 2: `/slides` catalogue QWeb inheritance

**Files:**
- Create: `theme_facodi/views/website_slides.xml`
- Modify: `theme_facodi/__manifest__.py`
- Modify: `theme_facodi/tests/test_website.py`
- Modify: `tests/test_module_contract.sh`

**Interfaces:**
- Consumes: `_facodi_catalog_visuals()` from Task 1.
- Produces: FACODI classes `facodi-slides-catalog`, `facodi-slides-grid`, `facodi-course-media`, `facodi-course-fallback` while retaining standard `.o_wslides_course_card` and filter/pager components.

- [ ] **Step 1: Write failing rendered catalogue test**

Extend `test_elearning_catalog_renders` or add a dedicated test that creates visible courses, opens `/slides`, parses HTML, and asserts:

```python
self.assertTrue(tree.xpath("//*[contains(@class, 'facodi-slides-catalog')]") )
self.assertTrue(tree.xpath("//*[contains(@class, 'facodi-slides-grid')]") )
self.assertTrue(tree.xpath("//a[contains(@class, 'o_wslides_course_card')]") )
```

Assert explicit cover renders through `/web/image/slide.channel/...`, stored slide visual through `/web/image/slide.slide/...`, YouTube fallback uses `i.ytimg.com`, and no-image course renders `.facodi-course-fallback` without a broken `<img>`.

- [ ] **Step 2: Verify RED**

Run/push the test-only change. Expected failure: FACODI classes/media hierarchy absent.

- [ ] **Step 3: Add focused QWeb inheritance**

Create `theme_facodi/views/website_slides.xml`:

1. Inherit `website_slides.courses_home`; add `facodi-slides-catalog` to the main catalogue container only.
2. Inherit `website_slides.courses_search_results`; add `facodi-slides-grid` to the existing result row and neutralize only conflicting Bootstrap `row-cols-*` classes if necessary through attributes, without replacing search/pager logic.
3. Inherit `website_slides.course_card`; compute the shared visual map once at the search-results level and select `facodi_visual = facodi_catalog_visuals.get(channel.id)` per card. Replace only the media node currently rendering `channel.image_1920`.
4. For `kind == "channel"`, render the channel image widget using Odoo image derivatives.
5. For `kind == "slide"`, render the selected slide image widget.
6. For `kind == "youtube"`, render `<img loading="lazy" decoding="async">` using the deterministic URL.
7. For fallback, render semantic `.facodi-course-fallback` HTML with FACODI label, initials and a decorative icon.

Do not alter standard title, tags, progress, CTA, membership or pager templates.

- [ ] **Step 4: Register QWeb data file and bump module version**

Add `views/website_slides.xml` to manifest `data`. Bump the release from the current `19.0.5.0.x` to the next patch version. Update the version assertion in `tests/test_module_contract.sh`.

- [ ] **Step 5: Run catalogue rendering and repository contract tests**

Expected: all new `/slides` tests pass; no missing XPath/template errors; existing homepage dynamic snippet and builder migration tests remain green.

- [ ] **Step 6: Commit**

Commit message: `feat: integrate dynamic visuals into course catalogue`

---

### Task 3: Lesson cards and course content hierarchy

**Files:**
- Modify: `theme_facodi/views/website_slides.xml`
- Modify: `theme_facodi/tests/test_website.py`

**Interfaces:**
- Consumes: standard `slide.slide.slide_category`, `slide_type`, `slide_icon_class`, `image_1920`, `youtube_id`, progress/access variables already provided by upstream templates.
- Produces: visual/type classes on standard `website_slides.lesson_card` and `website_slides.course_slides_list_slide` without changing JS hooks.

- [ ] **Step 1: Write failing training/documentation tests**

Create one training channel and one documentation channel. Render both course pages and assert that standard hooks remain:

```python
self.assertTrue(tree.xpath("//*[contains(@class, 'o_wslides_slides_list_slide')]") )
self.assertTrue(tree.xpath("//*[contains(@class, 'o_wslides_js_slides_list_slide_link')]") )
self.assertTrue(tree.xpath("//*[contains(@class, 'o_wslides_lesson_card')]") )
```

Also assert new FACODI type classes/badges such as `facodi-content-type-video`, `facodi-content-type-document`, `facodi-content-type-quiz` where matching fixtures exist.

- [ ] **Step 2: Verify RED**

Expected failure: new FACODI content-type classes absent, while upstream hooks are present.

- [ ] **Step 3: Add localized QWeb class/media refinements**

Inherit `website_slides.lesson_card` and `website_slides.course_slides_list_slide` with XPath attribute additions only. Derive class names from existing `slide.slide_category`/`slide_type`; retain all standard access conditions, links, progress, votes, preview, publisher and drag/drop controls.

For lesson-card media, prefer stored `slide.image_1920`; for a YouTube slide without stored image use deterministic thumbnail URL from standard `youtube_id`; otherwise render a FACODI content fallback using the existing `slide_icon_class`. Do not search ORM from the lesson template.

- [ ] **Step 4: Run course-page regression tests**

Expected: both training and documentation pages render 200; new visual classes appear; Odoo JS hook classes and controls remain intact.

- [ ] **Step 5: Commit**

Commit message: `feat: refine course content presentation`

---

### Task 4: Responsive catalogue and accessibility SCSS

**Files:**
- Modify: `theme_facodi/static/src/scss/website_slides.scss`
- Modify: `theme_facodi/tests/test_website.py`
- Modify: `tests/test_module_contract.sh`

**Interfaces:**
- Consumes: classes from Tasks 2–3.
- Produces: wide catalogue frame, responsive CSS Grid, consistent 16:9 media, clamped text, focus-visible, content badges, fallback art and reduced-motion handling.

- [ ] **Step 1: Add failing CSS contract assertions**

Add assertions that compiled frontend CSS contains `.facodi-slides-catalog`, `.facodi-slides-grid`, `.facodi-course-media`, `.facodi-course-fallback`, `grid-template-columns`, `object-fit:cover`, and focus-visible/reduced-motion selectors.

- [ ] **Step 2: Verify RED**

Expected failure: new CSS classes absent from compiled bundle.

- [ ] **Step 3: Implement responsive SCSS**

Extend `website_slides.scss` with:

```scss
body.o_wslides_body .facodi-site {
    .facodi-slides-catalog {
        width: min(100% - 2rem, 1680px);
        max-width: none;
        margin-inline: auto;
    }

    .facodi-slides-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(min(100%, 15rem), 1fr));
        gap: clamp(1rem, 1.4vw, 1.5rem);
    }

    .facodi-course-media {
        aspect-ratio: 16 / 9;
        overflow: hidden;
    }

    .facodi-course-media img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
}
```

Tune min card width/breakpoints so actual behavior is 1 mobile, 2 tablet, roughly 3–4 normal desktop and up to 5 on wide desktop. Clamp titles/descriptions, avoid excessive card height, improve card footer/progress spacing, type badges, lesson-list hover/focus, and touch target sizing. Preserve existing FACODI reduced-motion behavior.

- [ ] **Step 4: Verify compiled assets and rendering**

Run full Odoo tests plus asset fetch/compile assertions. Ensure no Sass errors and no upstream selector breakage.

- [ ] **Step 5: Commit**

Commit message: `style: modernize eLearning catalogue layout`

---

### Task 5: Internationalization, documentation and full regression

**Files:**
- Modify: `theme_facodi/i18n/theme_facodi.pot` only if new translatable source strings were introduced.
- Modify: `theme_facodi/i18n/pt.po` only for new visible source strings required by the QWeb additions.
- Modify: `theme_facodi/i18n/es.po` / `fr.po` only when the same strings are user-visible and current repository policy requires complete native catalogues.
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/validation.md`

**Interfaces:**
- Produces: documented behavior/evidence matrix matching the implemented source.

- [ ] **Step 1: Audit visible strings**

Prefer existing upstream strings and iconography. If FACODI fallback/type labels introduce source text, add them to native Odoo PO/POT catalogues; do not add custom language branching.

- [ ] **Step 2: Add PT/EN runtime assertions**

Extend existing i18n/runtime tests to render `/slides` and at least one course under English and `/pt`, asserting 200 responses and the same FACODI structural classes without custom language-condition markup.

- [ ] **Step 3: Update docs**

Document:
- non-destructive visual priority;
- batch resolver/no external request guarantee;
- inherited upstream templates;
- responsive `/slides` behavior;
- accessibility/fallback behavior;
- known validation boundary for exact browser viewport geometry if CI has no browser-layout runner.

- [ ] **Step 4: Run complete repository and Odoo regression suite**

Run all shell contract tests and the GitHub Actions Odoo 19 clean-install/upgrade workflow. Confirm prior dynamic-snippet Website Builder regression is still green.

- [ ] **Step 5: Review full branch diff**

Compare branch to current base and verify:
- no controller/model duplication;
- no `requests`/external HTTP in new resolver;
- no QWeb `request.env` searches or `sudo()`;
- no writes of derived images;
- no whole upstream template copies;
- standard Odoo hook classes preserved.

- [ ] **Step 6: Commit documentation/i18n**

Commit message: `docs: document dynamic eLearning visuals`

---

### Task 6: Pull request and exact-head verification

**Files:** none unless CI exposes a real defect.

- [ ] **Step 1: Push branch and open PR**

PR title: `feat: modernize eLearning catalogue and dynamic thumbnails`

PR body must summarize visual priority, `/slides` responsive changes, inherited Odoo templates, performance constraints and tests.

- [ ] **Step 2: Inspect complete PR diff**

Use GitHub PR diff, not only individual commits. Correct any ownership, accessibility, XPath or performance issue found.

- [ ] **Step 3: Require exact-head CI green**

Fetch workflow runs for the exact PR head SHA. Inspect failed job logs if any; fix through TDD and repeat until the exact head is green.

- [ ] **Step 4: Record final evidence**

Record branch, commits, files changed, inherited templates, resolver behavior, CI run/job IDs, limitations and whether the PR is merged or only ready for merge.
