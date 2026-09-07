# FACODI Website Foundation v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the FACODI Odoo 19 Community theme with reusable standard-first Website/eLearning blocks, complete native translations and stronger Website Builder compatibility.

**Architecture:** `theme_facodi` remains presentation-only. Reusable QWeb snippets and page compositions use native Website Builder contracts; course data remains owned by `website_slides`, dynamic course cards use `website.snippet.filter`, and translations use Odoo PO catalogues with English source strings.

**Tech Stack:** Odoo 19 Community, Website, Website Builder, `website_slides`, QWeb/XML, SCSS, native Odoo i18n, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-07-facodi-website-foundation-v2-design.md`

## Global Constraints

- Target Odoo 19 Community.
- Prefer standard Odoo Website/eLearning mechanisms over custom controllers or parallel models.
- `theme_facodi` owns presentation only.
- English remains the QWeb source language; `pt_PT`, `es_ES` and `fr_FR` use native PO catalogues.
- Do not import arbitrary `website.page` records.
- Do not use `request.env` or `sudo()` in theme QWeb.
- Preserve Website Builder/COW compatibility on existing databases.
- Every increment must pass clean install and upgrade tests.

---

### Task 1: Dynamic-snippet Builder compatibility

**Files:**
- Modify: `tests/test_homepage_dashboard_contract.sh`
- Modify: `theme_facodi/views/snippets/s_facodi_course_showcase.xml`

**Interfaces:**
- Consumes: Odoo `DynamicSnippetOptionPlugin` structural contract.
- Produces: `.s_dynamic_snippet_container`, `.s_dynamic_snippet_content`, `.dynamic_snippet_template` inside `s_facodi_course_showcase`.

- [x] **Step 1: Add failing contract checks for the two mandatory Builder wrapper classes.**
- [x] **Step 2: Verify the contract fails against the previous implementation.**
- [x] **Step 3: Add the standard wrapper classes and template metadata without querying business data from QWeb.**
- [x] **Step 4: Run the full Odoo 19 theme CI and verify install + upgrade pass.**

### Task 2: Academic areas reusable snippet

**Files:**
- Create: `theme_facodi/views/snippets/s_facodi_academic_areas.xml`
- Modify: `theme_facodi/views/snippets/snippets.xml`
- Modify: `theme_facodi/views/page_templates.xml`
- Modify: `theme_facodi/__manifest__.py`
- Modify: `theme_facodi/static/src/scss/snippets.scss`
- Modify: `tests/test_module_contract.sh`
- Create/Modify: `tests/test_foundation_v2_contract.sh`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Produces: stable snippet XML ID `theme_facodi.s_facodi_academic_areas` and Builder entry.
- Links only to standard `/slides` and `/website/search` routes; it does not duplicate course records.

- [ ] **Step 1: Add failing foundation contract asserting the snippet source, manifest entry, Builder registry entry, page-composition use and standard routes.**
- [ ] **Step 2: Run CI and verify the foundation contract fails because the snippet is absent.**
- [ ] **Step 3: Implement a four-card academic-area block for Computing & Technology, Mathematics & Data, Business & Society, and Languages & Culture.**
- [ ] **Step 4: Add responsive FACODI styling scoped under `.facodi-site`.**
- [ ] **Step 5: Add the block to Home and Pathways page compositions.**
- [ ] **Step 6: Run CI and verify the new contract passes.**

### Task 3: Community ecosystem / partners reusable snippet

**Files:**
- Create: `theme_facodi/views/snippets/s_facodi_ecosystem.xml`
- Modify: `theme_facodi/views/snippets/snippets.xml`
- Modify: `theme_facodi/views/page_templates.xml`
- Modify: `theme_facodi/__manifest__.py`
- Modify: `theme_facodi/static/src/scss/snippets.scss`
- Modify: `tests/test_foundation_v2_contract.sh`

**Interfaces:**
- Produces: stable snippet XML ID `theme_facodi.s_facodi_ecosystem`.
- Presents FACODI as an open community/SEA-EU-compatible educational ecosystem without adding partner business models.

- [ ] **Step 1: Extend the failing contract for ecosystem source, registry, manifest and compositions.**
- [ ] **Step 2: Implement a reusable editorial ecosystem block with Community, Open resources and University network cards plus contact/contribution CTA.**
- [ ] **Step 3: Add it to Home, Partners and Community compositions.**
- [ ] **Step 4: Run the contract and full CI.**

### Task 4: Complete native translations for Foundation v2

**Files:**
- Modify: `theme_facodi/i18n/theme_facodi.pot`
- Modify: `theme_facodi/i18n/pt.po`
- Modify: `theme_facodi/i18n/es.po`
- Modify: `theme_facodi/i18n/fr.po`
- Modify: `tests/test_i18n_contract.sh`

**Interfaces:**
- Consumes: English source strings from all Foundation v2 snippets.
- Produces: native `pt_PT`, `es_ES`, `fr_FR` translations using `model_terms:theme.ir.ui.view,arch:theme_facodi.*` references.

- [ ] **Step 1: Add failing i18n anchors for course-showcase, academic-area and ecosystem copy.**
- [ ] **Step 2: Add POT entries and exact PT/ES/FR translations.**
- [ ] **Step 3: Verify no alternate language branches exist in QWeb.**
- [ ] **Step 4: Run native i18n contract and Odoo runtime tests.**

### Task 5: Expand standard Odoo visual personalization

**Files:**
- Modify: `theme_facodi/static/src/scss/components.scss`
- Modify: `theme_facodi/static/src/scss/website.scss`
- Modify: `theme_facodi/static/src/scss/website_slides.scss`
- Modify: `theme_facodi/tests/test_website.py`
- Modify: `tests/test_foundation_v2_contract.sh`

**Interfaces:**
- Consumes: standard Website/Portal/eLearning DOM classes.
- Produces: FACODI-styled native cards, badges, forms, alerts, pagination, course surfaces and focus states without replacing functional Odoo templates.

- [ ] **Step 1: Add failing assertions for scoped native component/eLearning selectors.**
- [ ] **Step 2: Add FACODI visual treatment under `.facodi-site` / `body.o_wslides_body .facodi-site`.**
- [ ] **Step 3: Preserve Website Builder color-combination ownership and reduced-motion behavior.**
- [ ] **Step 4: Run asset compilation, theme tests and upgrade regression.**

### Task 6: Final integration and deployment pin

**Files:**
- Theme: merge verified PR into `marcelo-m7/facodi-theme:main`.
- Deploy: update `marcelo-m7/facodi-deploy/addons/facodi-theme` gitlink and README pin.

**Interfaces:**
- Produces: exact theme revision baked into canonical FACODI Coolify runtime.

- [ ] **Step 1: Require exact-head theme CI green.**
- [ ] **Step 2: Review diff for presentation/business-layer boundary violations.**
- [ ] **Step 3: Merge theme PR.**
- [ ] **Step 4: Create deployment-pin branch and PR in `facodi-deploy`.**
- [ ] **Step 5: Require repository contract, Compose validation and full fresh/idempotent migration + HTTP acceptance green.**
- [ ] **Step 6: Merge deployment PR only after the exact-head deployment CI passes.**
