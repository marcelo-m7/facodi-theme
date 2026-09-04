# FACODI Odoo 19 Website Theme Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standard Odoo 19 Website/eLearning theme package that applies FACODI branding without duplicating Website or eLearning business logic.

**Architecture:** Follow Odoo 19 theme conventions: package the technical addon as `website_facodi`, use Website Builder color/font variables and standard asset bundles, inherit `website.layout`/`website_slides` templates through QWeb/XPath, and keep JavaScript optional. The repo remains independent from `facodi_learning`.

**Tech Stack:** Odoo 19 Community, Website/eLearning, QWeb/XML, SCSS/Bootstrap 5.3, Odoo HttpCase, GitHub Actions, PostgreSQL 16.

**Spec:** `docs/superpowers/specs/2026-09-04-facodi-theme-design.md` (updated during implementation to reflect Odoo 19 `website_` technical naming convention).

## Global Constraints

- Target Odoo 19 Community.
- Technical addon name is `website_facodi`, following Odoo 19 theme naming guidance.
- Use standard Website Builder variables, color palettes, assets and inherited views before custom CSS/markup.
- Reuse standard Odoo header/footer/navigation behavior; styling may extend it, business behavior may not be replaced.
- No dependency on `facodi_learning`.
- Use the existing FACODI visual identity as reference: primary `#6a4bff`, secondary `#5dc7ff`, dark text `#1f1e42`, heading `#111035`, light background `#f7f6ff`, with system-font fallback.
- No bundled proprietary font binaries.

---

### Task 1: Theme contract and failing clean-install test

**Files:** `.github/workflows/ci.yml`, `website_facodi/__init__.py`, `website_facodi/__manifest__.py`, `website_facodi/tests/__init__.py`, `website_facodi/tests/test_website.py`.

**Interfaces:** Repository exposes one installable theme addon directory named `website_facodi`; CI installs it with `website_slides` on a clean Odoo 19 database and runs `/website_facodi` tests.

- [ ] Write an HttpCase that verifies `/` and `/slides` render after installation and that the FACODI site class is present on the website layout.
- [ ] Push the test/CI harness and verify failure before the theme implementation exists.
- [ ] Add only minimum package/manifest discovery files.

### Task 2: Standard Odoo theme variables and assets

**Files:** `website_facodi/static/src/scss/primary_variables.scss`, `website_facodi/static/src/scss/theme.scss`, `website_facodi/static/src/scss/elearning.scss`, `website_facodi/static/src/img/logo.svg`, `website_facodi/static/src/img/favicon.svg`.

**Interfaces:** `primary_variables.scss` extends `$o-color-palettes`, `$o-selected-color-palettes-names` and `$o-website-values-palettes`; frontend styles load through `web.assets_frontend`.

- [ ] Define a `facodi` 5-color Odoo palette and select it through Website Builder variables.
- [ ] Prefer Odoo/Bootstrap classes and semantic variables; custom CSS is limited to FACODI surfaces, rounded navigation/cards and eLearning presentation.
- [ ] Add repository-owned SVG logo/favicon only; do not bundle font files.
- [ ] Verify assets compile during clean module install.

### Task 3: Layout and eLearning view inheritance

**Files:** `website_facodi/views/website_layout.xml`, `website_facodi/views/elearning_templates.xml`.

**Interfaces:** Inherit `website.layout` and stable `website_slides` templates; add FACODI classes/branding hooks without replacing standard route/controller/business logic.

- [ ] Add `facodi-site` to the standard `#wrapwrap` container and set theme-color/favicon metadata with inherited QWeb.
- [ ] Add lightweight FACODI classes to standard eLearning catalog/course structures only where stable selectors exist.
- [ ] Keep standard menus, authentication, course membership, completion and publishing behavior untouched.
- [ ] Verify `/` and `/slides` render in HttpCase.

### Task 4: Repository documentation and standard compliance

**Files:** `README.md`, `docs/architecture.md`, `.gitignore`, `LICENSE`, update design spec.

**Interfaces:** Document module name `website_facodi`, submodule path `addons/facodi-theme`, Odoo 19 theme conventions and local CI command.

- [ ] Update the approved design spec to explain why `website_facodi` replaces the earlier `facodi_theme` technical name.
- [ ] Document the distinction between repository name (`facodi-theme`) and Odoo module name (`website_facodi`).
- [ ] Document standard-first styling principles and explicitly state there is no dependency on `facodi_learning`.
- [ ] Run final CI and review branch diff for copied standard templates or unnecessary JavaScript; remove any such duplication.
