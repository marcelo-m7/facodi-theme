# FACODI Live Odoo Theme Source Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the incorrect purple theme with a portable Odoo 19 Community implementation of the active `edu-open2.odoo.com` FACODI visual identity.

**Architecture:** Keep Website, Website Builder, Portal and `website_slides` authoritative. Package the verified database palette, layout and CSS as focused theme assets and inherited QWeb views, while excluding database ids, editorial pages and behavioral scripts.

**Tech Stack:** Odoo 19 Community, QWeb/XML, SCSS, Bash contract tests, Odoo `HttpCase`, Docker/PostgreSQL 16 CI.

**Spec:** `docs/superpowers/specs/2026-09-05-live-odoo-theme-source-design.md`

## Global Constraints

- Target Odoo 19 Community only.
- Depend only on `theme_common` and `website_slides`.
- Treat `edu-open2` website id 2 as read-only visual evidence, never as a runtime dependency.
- Do not add controllers, models, page records, ORM queries in QWeb or Enterprise dependencies.
- Do not force Website logo or favicon records.
- Preserve standard menu, authentication, Portal and eLearning behavior.

---

### Task 1: Visual-source regression contract

**Files:**
- Modify: `tests/test_module_contract.sh`

**Interfaces:**
- Consumes: exact source tokens and layout decisions from the design spec.
- Produces: a repository-level contract that fails against the superseded purple theme.

- [ ] **Step 1: Write the failing source-of-truth assertions**

Add checks requiring all six live colors, `facodi-header`, `facodi-footer`, the
dynamic Odoo menu expression and live eLearning selectors. Add a recursive
check rejecting `#6a4bff`, `#5dc7ff`, `#f7f6ff`, `/web/content/431`,
`request.env` and forced favicon markup.

```bash
for color in '#142846' '#37BED2' '#3979C8' '#A7E8BE' '#EFFF00' '#F9FAFB'; do
  grep -Riq "$color" theme_facodi || fail "live FACODI color missing: $color"
done
grep -Fq 'facodi-header' theme_facodi/views/customizations.xml || fail "live header missing"
grep -Fq 'website.menu_id.child_id' theme_facodi/views/customizations.xml || fail "dynamic menu missing"
```

- [ ] **Step 2: Run the contract and verify RED**

Run: `bash tests/test_module_contract.sh`

Expected: FAIL because `#142846` is absent or because a superseded purple token
is still present.

- [ ] **Step 3: Commit the failing regression contract**

```bash
git add tests/test_module_contract.sh
git commit -m "test: require live FACODI visual identity"
```

### Task 2: Live palette and optional assets

**Files:**
- Modify: `theme_facodi/static/src/scss/primary_variables.scss`
- Modify: `theme_facodi/static/src/scss/bootstrap_overridden.scss`
- Modify: `theme_facodi/static/description/theme_facodi.svg`
- Modify: `theme_facodi/static/src/img/logo.svg`
- Modify: `theme_facodi/static/src/img/favicon.svg`
- Modify: `theme_facodi/views/customizations.xml`

**Interfaces:**
- Consumes: exact FACODI colors from Task 1.
- Produces: Odoo palette name `facodi`, semantic Bootstrap values and matching optional artwork.

- [ ] **Step 1: Map the live color system into Odoo theme variables**

Set the source constants to the verified values and map Builder primary and
secondary colors to live ink and sun. Preserve readable white/paper
combinations and use `#142846` for `<meta name="theme-color">`.

```scss
$facodi-ink: #142846;
$facodi-cyan: #37BED2;
$facodi-blue: #3979C8;
$facodi-mint: #A7E8BE;
$facodi-sun: #EFFF00;
$facodi-paper: #F9FAFB;
```

- [ ] **Step 2: Redraw optional SVG assets using the same tokens**

Use paper backgrounds, ink borders/text, blue/cyan/mint panels and sun calls to
action. Keep the assets optional; no XML view may force their use.

- [ ] **Step 3: Run the contract**

Run: `bash tests/test_module_contract.sh`

Expected: still FAIL on the missing live header/footer or eLearning selectors,
proving the contract covers more than colors.

- [ ] **Step 4: Commit the palette unit**

```bash
git add theme_facodi/static/src/scss/primary_variables.scss theme_facodi/static/src/scss/bootstrap_overridden.scss theme_facodi/static/description/theme_facodi.svg theme_facodi/static/src/img/logo.svg theme_facodi/static/src/img/favicon.svg theme_facodi/views/customizations.xml
git commit -m "fix: restore live FACODI palette"
```

### Task 3: Dynamic live header, footer and primitives

**Files:**
- Modify: `theme_facodi/views/customizations.xml`
- Modify: `theme_facodi/static/src/scss/components.scss`
- Modify: `theme_facodi/static/src/scss/website.scss`
- Modify: `theme_facodi/tests/test_website.py`

**Interfaces:**
- Consumes: CSS custom properties derived from Task 2 and standard Odoo templates `website.layout`, `portal.placeholder_user_sign_in` and `portal.user_dropdown`.
- Produces: `.facodi-header`, `.facodi-footer`, `.facodi-wordmark`, `.facodi-button` and `.facodi-card` on clean theme activation.

- [ ] **Step 1: Add failing HttpCase expectations**

Require the public homepage response to contain the live theme color,
`facodi-header`, `FACODI<span`, `website.menu_id`-driven rendered links and
`facodi-footer`. Continue asserting that the standard Website favicon remains.

```python
self.assertIn('<meta name="theme-color" content="#142846"', response.text)
self.assertIn('class="o_header_standard facodi-header"', response.text)
self.assertIn('class="facodi-footer"', response.text)
```

- [ ] **Step 2: Replace the layout hooks with the portable live structure**

Implement the live wordmark, responsive navbar, dynamic child-menu iteration,
Portal sign-in/dropdown and footer links. Use standard routes only and no
database record ids.

- [ ] **Step 3: Implement reusable live primitives and responsive shell styles**

Move the live CSS into focused SCSS: CSS variables and header/footer in
`website.scss`; wordmark, geometric buttons and bordered/shadowed cards in
`components.scss`. Scope frontend rules under `.facodi-site` and include
focus-visible, reduced-motion and dark-scheme behavior.

- [ ] **Step 4: Run contract and Odoo tests**

Run: `bash tests/test_module_contract.sh`

Run the repository's Docker Odoo command from `.github/workflows/ci.yml` against
a fresh PostgreSQL 16 database.

Expected: source contract passes and HttpCase reports zero failures.

- [ ] **Step 5: Commit the layout unit**

```bash
git add theme_facodi/views/customizations.xml theme_facodi/static/src/scss/components.scss theme_facodi/static/src/scss/website.scss theme_facodi/tests/test_website.py
git commit -m "fix: reproduce live FACODI website shell"
```

### Task 4: Editable snippets and standard eLearning presentation

**Files:**
- Modify: `theme_facodi/views/snippets.xml`
- Modify: `theme_facodi/static/src/scss/snippets.scss`
- Modify: `theme_facodi/static/src/scss/website_slides.scss`
- Modify: `theme_facodi/tests/test_website.py`

**Interfaces:**
- Consumes: primitives from Task 3 and standard `/slides`/`/contactus` routes.
- Produces: three editable source-matched snippets and FACODI styling on standard `website_slides` markup.

- [ ] **Step 1: Extend failing source and HttpCase tests**

Require the registered snippets to expose the live classes
`facodi-hero`, `facodi-hero-board`, `facodi-stat-card` and
`facodi-open-section`. Require eLearning SCSS to target the standard
`o_wslides_body` cover, join and done controls without defining routes.

- [ ] **Step 2: Rebuild the three editable snippets**

Implement the live hero/learning-board, a three-card
Descubra–Aprenda–Contribua journey and the cyan institutional callout. Keep all
text editable and all links on `/slides` or `/contactus`.

- [ ] **Step 3: Port the live eLearning selectors**

Style the standard course cover with ink, translucent navigation, white header
text and blue/cyan primary actions. Keep all rules presentation-only and scoped
under `.facodi-site`.

- [ ] **Step 4: Run contract and Odoo tests**

Run: `bash tests/test_module_contract.sh`

Run the fresh-database Odoo `HttpCase` suite.

Expected: all tests pass with zero failures.

- [ ] **Step 5: Commit the snippet/eLearning unit**

```bash
git add theme_facodi/views/snippets.xml theme_facodi/static/src/scss/snippets.scss theme_facodi/static/src/scss/website_slides.scss theme_facodi/tests/test_website.py
git commit -m "fix: align FACODI snippets and eLearning"
```

### Task 5: Version and operational documentation

**Files:**
- Modify: `theme_facodi/__manifest__.py`
- Modify: `README.md`
- Modify: `docs/architecture.md`

**Interfaces:**
- Consumes: completed behavior from Tasks 1–4.
- Produces: release `19.0.3.0.0` and accurate source/ownership documentation.

- [ ] **Step 1: Add failing documentation assertions to the contract**

Require the README to name `edu-open2.odoo.com`, list the live ink/sun palette
and explain that pages are not imported. Require architecture documentation to
describe the database-artifact-to-source transition.

- [ ] **Step 2: Update manifest and documentation**

Bump the module to `19.0.3.0.0`. Document the verified source records,
standard-first boundary, file ownership, installation, validation and the fact
that `/web/content/431` is not a runtime dependency.

- [ ] **Step 3: Run the complete local suite**

Run: `bash tests/test_module_contract.sh`

Run: fresh PostgreSQL 16 plus Odoo 19 install and `--test-tags /theme_facodi`.

Expected: both commands exit 0 with no test failures.

- [ ] **Step 4: Commit documentation and release metadata**

```bash
git add theme_facodi/__manifest__.py README.md docs/architecture.md tests/test_module_contract.sh docs/superpowers/specs/2026-09-05-live-odoo-theme-source-design.md docs/superpowers/plans/2026-09-05-live-odoo-theme-source.md
git commit -m "docs: record live Odoo theme source"
```

### Task 6: Final verification and delivery

**Files:**
- Verify only; no planned production changes.

**Interfaces:**
- Consumes: all prior tasks.
- Produces: reviewable branch with fresh verification evidence.

- [ ] **Step 1: Review the complete diff against the design spec**

Run: `git diff --check origin/main...HEAD`

Run: `git diff --stat origin/main...HEAD`

Confirm every acceptance criterion maps to code or a passing test.

- [ ] **Step 2: Run final tests from a clean tree**

Run: `bash tests/test_module_contract.sh`

Run the full Docker Odoo 19/PostgreSQL 16 CI command.

Expected: zero failures and exit code 0.

- [ ] **Step 3: Push the branch and create a PR when the integration option is selected**

```bash
git push -u origin fix/live-odoo-theme
```

Target `main`; summarize the live-source evidence, standard-first boundary and
test output in the PR body.

