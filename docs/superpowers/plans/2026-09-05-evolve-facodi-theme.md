# FACODI Theme Evolution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evolve `marcelo-m7/facodi-theme` from the initial `website_facodi` styling addon into a proper Odoo 19 `theme_facodi` theme that preserves the current FACODI purple/blue identity, uses Odoo Website Builder and `website_slides` as the authoritative Website/LMS surfaces, and integrates reproducibly with `facodi-monorepo`.

**Architecture:** `theme_facodi` remains presentation-only. It follows `odoo/design-themes` conventions for theme naming, primary variables, primary snippet template generation, configurator metadata, asset registration, editable snippets and narrow QWeb inheritance. `facodi-monorepo` pins the Odoo 19 design-themes source separately and bakes only `theme_common` into the runtime image. Existing Website content remains standard Odoo data and survives the technical-module rename.

**Tech Stack:** Odoo 19 Community, `theme_common`, `website_slides`, QWeb/XML, SCSS/Bootstrap, Python `odoo.tests.HttpCase`, Bash contract tests, PostgreSQL 16, Docker, GitHub Actions, Git submodules.

**Spec:** `docs/superpowers/specs/2026-09-05-facodi-theme-evolution-design.md`

## Global Constraints

- Target Odoo version: **Odoo 19 Community**.
- Target technical addon name: **`theme_facodi`**.
- Repository name remains **`facodi-theme`**.
- Runtime addon dependencies are exactly `theme_common` and `website_slides`; do not add FACODI business-addon dependencies.
- `theme_common` comes from a pinned Odoo 19-compatible `odoo/design-themes` checkout; do not copy its source into this repository.
- Pin `odoo/design-themes` commit **`a1818df4ade65406c0cacae8b1ea676e6f70095f`** for this implementation cycle.
- Visual authority is the current `https://edu-open2.odoo.com`; the existing FACODI purple/blue palette is the implementation baseline.
- The Open2 lime/black proposal is a UX/content-composition reference only and must not replace the current identity.
- Website Builder remains authoritative for pages, menus, snippets, color combinations, logo, favicon, header/footer configuration and editor-created content.
- `website_slides` remains authoritative for courses, lessons, membership, progress and learner-facing routes.
- Theme QWeb must not contain ad-hoc `request.env`, `sudo()` or ORM searches.
- Do not copy complete Odoo Website/eLearning templates. Use theme variables, stable CSS hooks and narrow inheritance.
- Do not force a theme favicon or take ownership of the standard Website logo.
- No custom JavaScript unless a concrete theme/editor requirement cannot be implemented with standard Odoo/Bootstrap behavior.
- Preserve editor-created Website content through the module-name migration.
- Apply TDD: failing test/contract first, minimal implementation second, green verification third, focused commit fourth.

## Execution Branches

At execution time create:

```bash
# facodi-theme
git switch design/evolve-facodi-theme
git switch -c feat/evolve-odoo19-theme

# facodi-monorepo
git switch main
git pull --ff-only
git switch -c feat/evolve-theme-integration
```

Do not implement directly on `main` or on the design-only branch.

---

## Target File Map

### `marcelo-m7/facodi-theme`

```text
.github/workflows/ci.yml
tests/test_module_contract.sh
README.md
docs/architecture.md

theme_facodi/
├── __init__.py
├── __manifest__.py
├── data/
│   ├── generate_primary_template.xml
│   └── ir_asset.xml
├── views/
│   ├── customizations.xml
│   ├── snippets.xml
│   └── website_slides.xml
├── static/
│   ├── description/theme_facodi.svg
│   └── src/
│       ├── img/logo.svg
│       ├── img/favicon.svg
│       └── scss/
│           ├── primary_variables.scss
│           ├── bootstrap_overridden.scss
│           ├── components.scss
│           ├── website.scss
│           ├── snippets.scss
│           └── website_slides.scss
└── tests/
    ├── __init__.py
    └── test_website.py
```

The old `website_facodi/` directory is removed; the repository must expose one installable FACODI theme only.

### `marcelo-m7/facodi-monorepo`

```text
.gitmodules
vendor/odoo-design-themes                  # Gitlink
docker/Dockerfile
.env.example
scripts/validate-repository.sh
scripts/deploy-image.sh
scripts/migrate-theme-module-name.sh
tests/test_repository_contract.sh
README.md
docs/architecture.md
docs/ci-cd.md
docs/deployment.md
docs/gcp-staging.md
```

---

### Task 1: Rename the addon to `theme_facodi` and establish the theme skeleton

**Files:**
- Create: `tests/test_module_contract.sh`
- Create: `theme_facodi/__init__.py`
- Create: `theme_facodi/__manifest__.py`
- Create: `theme_facodi/data/generate_primary_template.xml`
- Create: `theme_facodi/data/ir_asset.xml`
- Create: `theme_facodi/views/customizations.xml`
- Create: `theme_facodi/views/snippets.xml`
- Create: `theme_facodi/views/website_slides.xml`
- Move: `website_facodi/static/src/img/logo.svg` -> `theme_facodi/static/src/img/logo.svg`
- Move: `website_facodi/static/src/img/favicon.svg` -> `theme_facodi/static/src/img/favicon.svg`
- Create: `theme_facodi/static/description/theme_facodi.svg`
- Delete: remaining `website_facodi/`

**Interfaces:**
- Consumes: Odoo module discovery and `theme_common` theme lifecycle.
- Produces: one addon named `theme_facodi`, dependency contract `theme_common + website_slides`, primary asset key `theme_facodi.primary_variables_scss`.

- [ ] **Step 1: Write the failing repository contract**

Create executable `tests/test_module_contract.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

[[ -f theme_facodi/__manifest__.py ]] || fail "theme_facodi manifest missing"
[[ ! -e website_facodi ]] || fail "legacy website_facodi addon must not remain installable"
[[ -f theme_facodi/data/generate_primary_template.xml ]] || fail "primary template generator missing"
[[ -f theme_facodi/data/ir_asset.xml ]] || fail "theme primary asset record missing"

grep -Fq '"theme_common"' theme_facodi/__manifest__.py || fail "theme_common dependency missing"
grep -Fq '"website_slides"' theme_facodi/__manifest__.py || fail "website_slides dependency missing"
grep -Fq 'Theme/Education' theme_facodi/__manifest__.py || fail "theme category must be Theme/Education"
grep -Fq 'theme_facodi.primary_variables_scss' theme_facodi/data/ir_asset.xml || fail "primary variables asset key missing"
grep -Fq 'web._assets_primary_variables' theme_facodi/data/ir_asset.xml || fail "primary variables bundle missing"

if grep -R -nE 'request\.env|sudo\(\)|href="/theme_facodi/static/src/img/favicon\.svg"' theme_facodi --include='*.xml'; then
  fail "theme QWeb contains business-data access or a forced favicon"
fi

echo "PASS: theme module contract"
```

- [ ] **Step 2: Run the contract and confirm RED**

```bash
bash tests/test_module_contract.sh
```

Expected: `FAIL: theme_facodi manifest missing`.

- [ ] **Step 3: Create the minimal Odoo theme manifest and standard lifecycle data**

Create empty `theme_facodi/__init__.py`.

Create `theme_facodi/__manifest__.py`:

```python
{
    "name": "FACODI Theme",
    "summary": "FACODI visual identity for Odoo Website and eLearning",
    "version": "19.0.2.0.0",
    "category": "Theme/Education",
    "sequence": 120,
    "author": "FACODI",
    "website": "https://facodi.pt",
    "license": "LGPL-3",
    "depends": ["theme_common", "website_slides"],
    "data": [
        "data/generate_primary_template.xml",
        "data/ir_asset.xml",
        "views/customizations.xml",
        "views/snippets.xml",
        "views/website_slides.xml",
    ],
    "images": ["static/description/theme_facodi.svg"],
    "images_preview_theme": {},
    "configurator_snippets": {
        "homepage": [
            "s_facodi_hero",
            "s_facodi_learning_journey",
            "s_facodi_institutional",
        ],
    },
    "installable": True,
    "application": False,
}
```

Create `theme_facodi/data/generate_primary_template.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <function model="ir.module.module" name="_generate_primary_snippet_templates">
        <value eval="[ref('base.module_theme_facodi')]"/>
    </function>
</odoo>
```

Create `theme_facodi/data/ir_asset.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <asset id="primary_variables_scss" name="FACODI primary variables SCSS">
        <field name="key">theme_facodi.primary_variables_scss</field>
        <field name="bundle">web._assets_primary_variables</field>
        <field name="path">theme_facodi/static/src/scss/primary_variables.scss</field>
    </asset>
</odoo>
```

Create the three view files as valid intentional empty Odoo data files for this task:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo/>
```

Move the existing project-owned logo/favicon SVGs with `git mv`. Create `theme_facodi/static/description/theme_facodi.svg` as a lightweight purple/blue SVG preview using SVG primitives only.

- [ ] **Step 4: Remove the legacy addon directory**

After moving reusable assets:

```bash
git rm -r website_facodi
```

If `git mv` already removed individual files from that tree, delete only what remains.

- [ ] **Step 5: Run the contract and confirm GREEN**

```bash
bash tests/test_module_contract.sh
```

Expected: `PASS: theme module contract`.

- [ ] **Step 6: Commit**

```bash
git add tests theme_facodi
git add -u
git commit -m "refactor: migrate FACODI addon to theme_facodi"
```

---

### Task 2: Make theme CI resolve pinned `theme_common`

**Files:**
- Modify: `.github/workflows/ci.yml`
- Modify: `tests/test_module_contract.sh`

**Interfaces:**
- Consumes: `odoo/design-themes@a1818df4ade65406c0cacae8b1ea676e6f70095f`, `odoo:19.0`, `postgres:16`.
- Produces: clean-install CI for `theme_facodi` with pinned `theme_common` available.

- [ ] **Step 1: Add failing CI assertions**

Append:

```bash
grep -Fq 'a1818df4ade65406c0cacae8b1ea676e6f70095f' .github/workflows/ci.yml || fail "CI must pin design-themes"
grep -Fq '/mnt/design-themes' .github/workflows/ci.yml || fail "CI must mount design-themes"
grep -Fq -- '-i theme_facodi' .github/workflows/ci.yml || fail "CI must install theme_facodi"
grep -Fq -- '--test-tags /theme_facodi' .github/workflows/ci.yml || fail "CI must run theme_facodi tests"
```

- [ ] **Step 2: Run and confirm RED**

```bash
bash tests/test_module_contract.sh
```

Expected: workflow contract failure.

- [ ] **Step 3: Checkout pinned design-themes in GitHub Actions**

Add after `actions/checkout@v4`:

```yaml
      - name: Checkout pinned Odoo design themes
        run: |
          git clone --filter=blob:none https://github.com/odoo/design-themes.git "$RUNNER_TEMP/design-themes"
          git -C "$RUNNER_TEMP/design-themes" checkout a1818df4ade65406c0cacae8b1ea676e6f70095f
          test -f "$RUNNER_TEMP/design-themes/theme_common/__manifest__.py"
```

Rename the CI database to `theme_facodi_ci` everywhere. Use this Odoo run:

```yaml
      - name: Install theme and run Odoo tests
        run: |
          docker run --rm \
            --network facodi-theme-ci \
            -e HOST=facodi-theme-db \
            -e PORT=5432 \
            -e USER=odoo \
            -e PASSWORD=odoo \
            -v "$GITHUB_WORKSPACE:/mnt/facodi-addons:ro" \
            -v "$RUNNER_TEMP/design-themes:/mnt/design-themes:ro" \
            odoo:19.0 \
            --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/design-themes,/mnt/facodi-addons \
            --workers=0 \
            --without-demo=True \
            -d theme_facodi_ci \
            -i theme_facodi \
            --test-tags /theme_facodi \
            --stop-after-init
```

Update the PostgreSQL start/readiness DB name from `website_facodi_ci` to `theme_facodi_ci`.

- [ ] **Step 4: Run contract + CI**

```bash
bash tests/test_module_contract.sh
```

Expected: fast contract PASS. GitHub Actions must resolve `theme_common` and complete the Odoo install without dependency/XML errors.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/ci.yml tests/test_module_contract.sh
git commit -m "ci: test theme against pinned Odoo design themes"
```

---

### Task 3: Implement the FACODI palette and separated theme assets

**Files:**
- Create: `theme_facodi/static/src/scss/primary_variables.scss`
- Create: `theme_facodi/static/src/scss/bootstrap_overridden.scss`
- Create: `theme_facodi/static/src/scss/components.scss`
- Create: `theme_facodi/static/src/scss/website.scss`
- Create: `theme_facodi/static/src/scss/snippets.scss`
- Create: `theme_facodi/static/src/scss/website_slides.scss`
- Modify: `theme_facodi/__manifest__.py`
- Modify: `tests/test_module_contract.sh`

**Interfaces:**
- Consumes: Odoo theme palette maps and Bootstrap variables.
- Produces: FACODI color combination `facodi` and focused frontend SCSS bundles.

- [ ] **Step 1: Add failing asset assertions**

Append:

```bash
for file in primary_variables bootstrap_overridden components website snippets website_slides; do
  [[ -f "theme_facodi/static/src/scss/${file}.scss" ]] || fail "missing ${file}.scss"
done

grep -Fq '#6a4bff' theme_facodi/static/src/scss/primary_variables.scss || fail "FACODI purple missing"
grep -Fq '#5dc7ff' theme_facodi/static/src/scss/primary_variables.scss || fail "FACODI blue missing"
grep -Fq "'facodi'" theme_facodi/static/src/scss/primary_variables.scss || fail "FACODI palette missing"
grep -Fq 'web.assets_frontend' theme_facodi/__manifest__.py || fail "frontend asset bundle missing"
```

- [ ] **Step 2: Run and confirm RED**

```bash
bash tests/test_module_contract.sh
```

Expected: missing SCSS files.

- [ ] **Step 3: Implement `primary_variables.scss`**

```scss
$facodi-purple: #6a4bff;
$facodi-blue: #5dc7ff;
$facodi-surface: #f7f6ff;
$facodi-white: #ffffff;
$facodi-ink: #1f1e42;
$facodi-heading: #111035;

$o-color-palettes: map-merge($o-color-palettes, (
    'facodi': (
        'o-color-1': $facodi-purple,
        'o-color-2': $facodi-blue,
        'o-color-3': $facodi-surface,
        'o-color-4': $facodi-white,
        'o-color-5': $facodi-ink,
        'o-cc1-bg': 'o-color-4',
        'o-cc1-text': 'o-color-5',
        'o-cc1-headings': 'o-color-5',
        'o-cc1-link': 'o-color-1',
        'o-cc1-btn-primary': 'o-color-1',
        'o-cc1-btn-primary-text': 'o-color-4',
        'o-cc2-bg': 'o-color-3',
        'o-cc2-text': 'o-color-5',
        'o-cc2-headings': 'o-color-5',
        'o-cc2-link': 'o-color-1',
        'o-cc3-bg': 'o-color-1',
        'o-cc3-text': 'o-color-4',
        'o-cc3-headings': 'o-color-4',
        'o-cc3-link': 'o-color-4',
        'o-cc4-bg': 'o-color-5',
        'o-cc4-text': 'o-color-4',
        'o-cc4-headings': 'o-color-4',
        'o-cc4-link': 'o-color-2',
        'menu': 1,
        'footer': 4,
        'copyright': 4,
    ),
));

$o-selected-color-palettes-names: append($o-selected-color-palettes-names, 'facodi');

$o-theme-color-palettes: map-merge($o-theme-color-palettes, (
    'facodi': (
        'alpha': $facodi-purple,
        'beta': $facodi-blue,
        'gamma': $facodi-surface,
        'delta': $facodi-white,
        'epsilon': $facodi-ink,
    ),
));

$o-website-values-palettes: append($o-website-values-palettes, (
    'color-palettes-name': 'facodi',
    'link-underline': 'never',
    'btn-border-radius': .75rem,
    'btn-border-radius-sm': .625rem,
    'btn-border-radius-lg': .875rem,
    'input-border-radius': .75rem,
    'logo-height': 2.25rem,
));

$o-color-palettes-compatibility-indexes: (1: 'facodi');
$o-theme-color-palettes-compatibility-indexes: (1: 'facodi');
```

Do not force `header-template` or `footer-template`. The first release preserves the site's active standard configuration and styles the standard chrome.

- [ ] **Step 4: Implement Bootstrap/reusable/global styles**

`bootstrap_overridden.scss`:

```scss
$primary: $facodi-purple !default;
$secondary: $facodi-blue !default;
$body-color: $facodi-ink !default;
$headings-color: $facodi-heading !default;
$body-bg: $facodi-white !default;
$border-radius: .75rem !default;
$border-radius-lg: .875rem !default;
$border-radius-sm: .625rem !default;
```

`components.scss`:

```scss
.facodi-kicker {
    color: $facodi-purple;
    font-size: .8125rem;
    font-weight: 700;
    letter-spacing: .08em;
    text-transform: uppercase;
}

.facodi-card {
    border: 1px solid rgba($facodi-ink, .12);
    border-radius: 1rem;
    background: $facodi-white;
    box-shadow: 0 .5rem 2rem rgba($facodi-ink, .06);
}
```

`website.scss`:

```scss
#wrapwrap {
    color: $facodi-ink;
}

#wrapwrap h1,
#wrapwrap h2,
#wrapwrap h3,
#wrapwrap h4,
#wrapwrap h5,
#wrapwrap h6 {
    color: $facodi-heading;
}

#wrapwrap .navbar .nav-link:focus-visible,
#wrapwrap .btn:focus-visible,
#wrapwrap a:focus-visible {
    outline: .1875rem solid rgba($facodi-blue, .65);
    outline-offset: .1875rem;
}
```

Create `snippets.scss` with the single comment `// FACODI Website Builder snippet styles.` and `website_slides.scss` with `// Standard website_slides presentation refinements.`. They are populated in Tasks 4 and 5.

- [ ] **Step 5: Register the frontend bundle**

Add to the manifest:

```python
"assets": {
    "web.assets_frontend": [
        "theme_facodi/static/src/scss/bootstrap_overridden.scss",
        "theme_facodi/static/src/scss/components.scss",
        "theme_facodi/static/src/scss/website.scss",
        "theme_facodi/static/src/scss/snippets.scss",
        "theme_facodi/static/src/scss/website_slides.scss",
    ],
},
```

Primary variables remain registered through `ir.asset` only.

- [ ] **Step 6: Verify GREEN and commit**

```bash
bash tests/test_module_contract.sh
```

Require green GitHub Actions asset compilation, then:

```bash
git add theme_facodi tests/test_module_contract.sh
git commit -m "feat: add FACODI Odoo theme palette and assets"
```

---

### Task 4: Add editable FACODI Website Builder snippets

**Files:**
- Modify: `theme_facodi/views/snippets.xml`
- Modify: `theme_facodi/static/src/scss/snippets.scss`
- Create: `theme_facodi/tests/__init__.py`
- Create: `theme_facodi/tests/test_website.py`

**Interfaces:**
- Consumes: `website.snippets`, standard Website Builder editing, Bootstrap grid/utilities.
- Produces: snippet group `facodi` and view keys `theme_facodi.s_facodi_hero`, `theme_facodi.s_facodi_learning_journey`, `theme_facodi.s_facodi_institutional`.

- [ ] **Step 1: Write failing snippet registration test**

`theme_facodi/tests/__init__.py`:

```python
from . import test_website
```

`theme_facodi/tests/test_website.py`:

```python
from odoo.tests import HttpCase, tagged


@tagged("-at_install", "post_install")
class TestFacodiTheme(HttpCase):
    def test_facodi_snippets_are_registered(self):
        keys = {
            "theme_facodi.s_facodi_hero",
            "theme_facodi.s_facodi_learning_journey",
            "theme_facodi.s_facodi_institutional",
        }
        views = self.env["ir.ui.view"].search([("key", "in", list(keys))])
        self.assertEqual(set(views.mapped("key")), keys)
```

- [ ] **Step 2: Run Odoo tests and confirm RED**

Use the CI-equivalent Odoo command with `--test-tags /theme_facodi`.

Expected: the snippet keys are absent.

- [ ] **Step 3: Register the FACODI snippet group and snippets**

Replace `views/snippets.xml` with:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="snippets" inherit_id="website.snippets" name="FACODI snippets">
        <xpath expr="//t[@id='installed_snippets_hook']" position="after">
            <t snippet-group="facodi"
               t-snippet="website.s_snippet_group"
               string="FACODI"
               t-thumbnail="/theme_facodi/static/description/theme_facodi.svg"/>
        </xpath>
        <xpath expr="//snippets[@id='snippet_structure']" position="inside">
            <t t-snippet="theme_facodi.s_facodi_hero" string="FACODI Hero" group="facodi"
               t-thumbnail="/theme_facodi/static/description/theme_facodi.svg"/>
            <t t-snippet="theme_facodi.s_facodi_learning_journey" string="Learning Journey" group="facodi"
               t-thumbnail="/theme_facodi/static/description/theme_facodi.svg"/>
            <t t-snippet="theme_facodi.s_facodi_institutional" string="Institutional" group="facodi"
               t-thumbnail="/theme_facodi/static/description/theme_facodi.svg"/>
        </xpath>
    </template>

    <template id="s_facodi_hero" name="FACODI Hero">
        <section class="s_facodi_hero o_cc o_cc1 pt96 pb96" data-snippet="s_facodi_hero" data-name="FACODI Hero">
            <div class="container">
                <div class="row align-items-center g-5">
                    <div class="col-lg-7">
                        <p class="facodi-kicker mb-3">Faculdade Comunitária Digital</p>
                        <h1 class="display-3 mb-4">Ensino superior acessível, aberto e comunitário.</h1>
                        <p class="lead mb-4">Explore percursos de aprendizagem organizados a partir de conteúdos educativos abertos e públicos.</p>
                        <div class="d-flex flex-wrap gap-3">
                            <a class="btn btn-primary btn-lg" href="/slides">Explorar percursos</a>
                            <a class="btn btn-outline-primary btn-lg" href="/sobre">Conhecer a FACODI</a>
                        </div>
                    </div>
                    <div class="col-lg-5">
                        <div class="facodi-card s_facodi_hero__journey p-4 p-lg-5">
                            <span class="facodi-kicker">A sua jornada</span>
                            <ol class="list-unstyled mt-4 mb-0">
                                <li><strong>01 · Descubra</strong><span>Encontre um percurso.</span></li>
                                <li><strong>02 · Aprenda</strong><span>Estude no seu ritmo.</span></li>
                                <li><strong>03 · Contribua</strong><span>Partilhe em comunidade.</span></li>
                            </ol>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </template>

    <template id="s_facodi_learning_journey" name="FACODI Learning Journey">
        <section class="s_facodi_learning_journey o_cc o_cc2 pt80 pb80" data-snippet="s_facodi_learning_journey" data-name="Learning Journey">
            <div class="container">
                <p class="facodi-kicker">Como funciona</p>
                <h2 class="mb-5">Descubra, aprenda e contribua.</h2>
                <div class="row g-4">
                    <div class="col-md-4"><article class="facodi-card h-100 p-4"><span class="facodi-kicker">01</span><h3>Descubra</h3><p>Explore currículos, cursos e recursos educativos.</p></article></div>
                    <div class="col-md-4"><article class="facodi-card h-100 p-4"><span class="facodi-kicker">02</span><h3>Aprenda</h3><p>Siga um percurso organizado usando os recursos disponíveis.</p></article></div>
                    <div class="col-md-4"><article class="facodi-card h-100 p-4"><span class="facodi-kicker">03</span><h3>Contribua</h3><p>Ajude a melhorar e ampliar a aprendizagem em comunidade.</p></article></div>
                </div>
            </div>
        </section>
    </template>

    <template id="s_facodi_institutional" name="FACODI Institutional">
        <section class="s_facodi_institutional o_cc o_cc1 pt64 pb64" data-snippet="s_facodi_institutional" data-name="FACODI Institutional">
            <div class="container">
                <div class="facodi-card p-4 p-lg-5">
                    <div class="row align-items-center g-4">
                        <div class="col-lg-8">
                            <p class="facodi-kicker">Projeto universitário e comunitário</p>
                            <h2>Aprendizagem digital aberta, organizada para circular.</h2>
                            <p class="mb-0">Apresente aqui o enquadramento institucional, parceiros e iniciativas da FACODI usando o editor do Website.</p>
                        </div>
                        <div class="col-lg-4 text-lg-end">
                            <a class="btn btn-primary" href="/sobre">Sobre a FACODI</a>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </template>
</odoo>
```

The institutional block is neutral editable website copy; it does not encode a funding/business rule.

- [ ] **Step 4: Implement snippet SCSS**

Replace `snippets.scss` with:

```scss
.s_facodi_hero {
    background:
        radial-gradient(circle at 85% 20%, rgba($facodi-blue, .28), transparent 32rem),
        linear-gradient(180deg, rgba($facodi-surface, .9), $facodi-white);
}

.s_facodi_hero__journey li {
    display: grid;
    gap: .25rem;
    padding: 1rem 0;
    border-bottom: 1px solid rgba($facodi-ink, .1);
}

.s_facodi_hero__journey li:last-child {
    border-bottom: 0;
}

.s_facodi_learning_journey .facodi-card {
    transition: transform .2s ease, box-shadow .2s ease;
}

@media (hover: hover) {
    .s_facodi_learning_journey .facodi-card:hover {
        transform: translateY(-.25rem);
        box-shadow: 0 .75rem 2.5rem rgba($facodi-ink, .1);
    }
}

@media (prefers-reduced-motion: reduce) {
    .s_facodi_learning_journey .facodi-card {
        transition: none;
    }
}
```

- [ ] **Step 5: Verify GREEN**

Run the fast contract and Odoo CI. Expected: the three snippet keys exist, XML parses and frontend assets compile.

- [ ] **Step 6: Website Builder smoke test**

On a test instance: Website -> Edit -> Blocks. Confirm group `FACODI` appears and each block can be inserted, text-edited, moved and deleted with standard controls.

- [ ] **Step 7: Commit**

```bash
git add theme_facodi
git commit -m "feat: add editable FACODI website snippets"
```

---

### Task 5: Preserve standard layout/logo/favicon and style `website_slides`

**Files:**
- Modify: `theme_facodi/views/customizations.xml`
- Modify: `theme_facodi/views/website_slides.xml`
- Modify: `theme_facodi/static/src/scss/website_slides.scss`
- Modify: `theme_facodi/tests/test_website.py`
- Modify: `tests/test_module_contract.sh`

**Interfaces:**
- Consumes: `website.layout`, standard Odoo favicon/logo, standard `website_slides` routes/markup.
- Produces: `facodi-site` layout class, theme-color metadata, visual-only eLearning adaptation.

- [ ] **Step 1: Add failing preservation/route tests**

Extend `test_website.py`:

```python
    def test_homepage_uses_facodi_layout_class(self):
        response = self.url_open("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("facodi-site", response.text)

    def test_standard_favicon_is_not_replaced(self):
        response = self.url_open("/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("/theme_facodi/static/src/img/favicon.svg", response.text)

    def test_elearning_catalog_renders(self):
        response = self.url_open("/slides")
        self.assertEqual(response.status_code, 200)
```

Append to `tests/test_module_contract.sh`:

```bash
[[ ! -d theme_facodi/controllers ]] || fail "presentation theme must not add parallel learning routes/controllers"
```

- [ ] **Step 2: Run and confirm RED**

Expected: homepage class test fails because `customizations.xml` is empty.

- [ ] **Step 3: Implement narrow layout inheritance**

`views/customizations.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="website_layout" inherit_id="website.layout" name="FACODI Website Layout">
        <xpath expr="//div[@id='wrapwrap']" position="attributes">
            <attribute name="t-attf-class" add="facodi-site" separator=" "/>
        </xpath>
        <xpath expr="//head" position="inside">
            <meta name="theme-color" content="#6a4bff"/>
        </xpath>
    </template>
</odoo>
```

No favicon `<link>`, hard-coded logo, complete header replacement or complete footer replacement.

- [ ] **Step 4: Make absence of eLearning structural overrides explicit**

`views/website_slides.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- First evolved release uses standard website_slides structure unchanged. -->
</odoo>
```

- [ ] **Step 5: Verify actual Odoo 19 selectors before styling**

Open rendered Odoo 19 `/slides`, a course and a lesson. For each selector below, confirm it exists in the current DOM/source before retaining the rule:

```text
.o_wslides_home_main
.o_wslides_course_main
.o_wslides_course_card
.o_wslides_slides_list_slide
.progress-bar
```

Remove nonexistent selectors from the implementation; do not create replacement markup just to satisfy CSS.

- [ ] **Step 6: Implement `website_slides.scss` with only verified selectors**

The expected implementation, when all listed selectors are present, is:

```scss
.facodi-site .o_wslides_home_main,
.facodi-site .o_wslides_course_main {
    color: $facodi-ink;
}

.facodi-site .o_wslides_course_card {
    overflow: hidden;
    border-radius: 1rem;
    border-color: rgba($facodi-ink, .1);
    box-shadow: 0 .375rem 1.5rem rgba($facodi-ink, .05);
}

.facodi-site .o_wslides_slides_list_slide:hover,
.facodi-site .o_wslides_slides_list_slide:focus-within {
    background-color: rgba($facodi-surface, .75);
}

.facodi-site .progress-bar {
    background-color: $facodi-purple;
}
```

- [ ] **Step 7: Verify tests, assets and responsive behavior**

Require Odoo CI PASS. At widths 375px, 768px and 1440px verify standard navigation, visible keyboard focus, working `/slides` navigation, no hover-only content, and reduced-motion behavior for the custom snippet transition.

- [ ] **Step 8: Commit**

```bash
git add theme_facodi tests/test_module_contract.sh
git commit -m "feat: style standard Website and eLearning surfaces"
```

---

### Task 6: Update theme documentation and remove stale active-module claims

**Files:**
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `tests/test_module_contract.sh`

**Interfaces:**
- Consumes: final theme contracts from Tasks 1-5.
- Produces: current operator/contributor documentation for `theme_facodi`.

- [ ] **Step 1: Add failing documentation assertions**

Append:

```bash
if grep -R -n 'website_facodi' README.md docs/architecture.md; then
  fail "current docs still describe website_facodi as the active addon"
fi

grep -Fq 'theme_common' README.md || fail "README must document theme_common"
grep -Fq 'odoo/design-themes' docs/architecture.md || fail "architecture must document upstream design-themes"
```

- [ ] **Step 2: Run and confirm RED**

Expected: README/architecture still name `website_facodi`.

- [ ] **Step 3: Rewrite README with the implemented contract**

State exactly:

```text
repository: facodi-theme
technical module: theme_facodi
dependencies: theme_common + website_slides
visual authority: current edu-open2 identity
Website Builder owns editable pages/branding
website_slides owns learner behavior
no facodi_learning dependency
no forced favicon/logo
```

Use this installation example:

```bash
odoo -d facodi \
  --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/opt/odoo-design-themes,/path/to/facodi-theme \
  -i theme_facodi \
  --stop-after-init
```

- [ ] **Step 4: Rewrite architecture doc**

Include:

```text
Odoo 19 Community
├── website / Website Builder
├── website_slides
└── theme_common (pinned from odoo/design-themes)
          │
          ▼
     theme_facodi
     ├── palette/theme values
     ├── editable FACODI snippets
     ├── narrow layout inheritance
     └── presentation-only website_slides styling
```

Document the standard-first decision rule and the prohibition on business-data queries in QWeb.

- [ ] **Step 5: Verify GREEN and commit**

```bash
bash tests/test_module_contract.sh
git add README.md docs/architecture.md tests/test_module_contract.sh
git commit -m "docs: document evolved FACODI Odoo theme"
```

---

### Task 7: Add the one-time `website_facodi` -> `theme_facodi` registry migration to `facodi-monorepo`

**Repository:** `marcelo-m7/facodi-monorepo`

**Files:**
- Create: `scripts/migrate-theme-module-name.sh`
- Modify: `tests/test_repository_contract.sh`

**Interfaces:**
- Consumes: monorepo `.env`, Docker Compose, PostgreSQL service `db`.
- Produces: idempotent rename of `ir_module_module.name` and `ir_model_data.module` before the first `theme_facodi` upgrade.

- [ ] **Step 1: Add failing migration-script contract tests**

Append:

```bash
[[ -x scripts/migrate-theme-module-name.sh ]] || fail "theme module rename migration must be executable"
grep -Fq 'ir_module_module' scripts/migrate-theme-module-name.sh || fail "migration must update ir_module_module"
grep -Fq 'ir_model_data' scripts/migrate-theme-module-name.sh || fail "migration must update ir_model_data ownership"
grep -Fq 'theme_facodi' scripts/migrate-theme-module-name.sh || fail "migration target missing"
```

- [ ] **Step 2: Run and confirm RED**

```bash
bash tests/test_repository_contract.sh
```

Expected: migration script missing.

- [ ] **Step 3: Implement Compose-based idempotent migration**

Create executable `scripts/migrate-theme-module-name.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

[[ -f .env ]] || { echo "missing $ROOT_DIR/.env" >&2; exit 66; }
set -a
# shellcheck disable=SC1091
source .env
set +a

: "${ODOO_DB:?ODOO_DB must be set in .env}"
: "${POSTGRES_USER:=odoo}"

if docker info >/dev/null 2>&1; then
  DOCKER=(docker)
elif sudo -n docker info >/dev/null 2>&1; then
  DOCKER=(sudo -n docker)
else
  echo "docker is unavailable" >&2
  exit 69
fi

COMPOSE=("${DOCKER[@]}" compose --env-file "$ROOT_DIR/.env" -f infrastructure/docker-compose.yml)
"${COMPOSE[@]}" up -d db

old_state="$("${COMPOSE[@]}" exec -T db psql -U "$POSTGRES_USER" -d "$ODOO_DB" -tAc \
  "SELECT state FROM ir_module_module WHERE name='website_facodi' LIMIT 1" 2>/dev/null || true)"
new_state="$("${COMPOSE[@]}" exec -T db psql -U "$POSTGRES_USER" -d "$ODOO_DB" -tAc \
  "SELECT state FROM ir_module_module WHERE name='theme_facodi' LIMIT 1" 2>/dev/null || true)"

if [[ -z "$old_state" ]]; then
  echo "No legacy website_facodi module record; no rename required."
  exit 0
fi

if [[ -n "$new_state" ]]; then
  echo "Both website_facodi and theme_facodi exist; refusing ambiguous migration." >&2
  exit 1
fi

conflicts="$("${COMPOSE[@]}" exec -T db psql -U "$POSTGRES_USER" -d "$ODOO_DB" -tAc "
SELECT count(*)
FROM ir_model_data old
JOIN ir_model_data new
  ON new.module='theme_facodi'
 AND new.name=old.name
WHERE old.module='website_facodi';
")"

if [[ "$conflicts" != "0" ]]; then
  echo "Conflicting theme_facodi XML IDs already exist; refusing migration." >&2
  exit 1
fi

"${COMPOSE[@]}" exec -T db psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$ODOO_DB" <<'SQL'
BEGIN;
UPDATE ir_module_module
SET name = 'theme_facodi'
WHERE name = 'website_facodi';

UPDATE ir_model_data
SET module = 'theme_facodi'
WHERE module = 'website_facodi';
COMMIT;
SQL

echo "Renamed website_facodi registry/XML-ID ownership to theme_facodi."
```

This script changes module metadata/XML-ID ownership only. It must not delete Website pages, menus, views or attachments.

- [ ] **Step 4: Test three migration cases on a disposable database/stack**

Verify:

```text
Case A: website_facodi exists, theme_facodi absent -> rename succeeds
Case B: run again after Case A -> no-op exit 0
Case C: both module records exist -> abort exit 1
```

For Case A verify:

```sql
SELECT name, state FROM ir_module_module WHERE name IN ('website_facodi', 'theme_facodi');
SELECT module, name FROM ir_model_data WHERE name='website_layout';
```

Expected ownership/module name: `theme_facodi` only.

- [ ] **Step 5: Verify contract and commit**

```bash
bash tests/test_repository_contract.sh
git add scripts/migrate-theme-module-name.sh tests/test_repository_contract.sh
git commit -m "feat: add FACODI theme module rename migration"
```

---

### Task 8: Pin `odoo/design-themes`, bake only `theme_common`, switch runtime to `theme_facodi`

**Repository:** `marcelo-m7/facodi-monorepo`

**Files:**
- Modify: `.gitmodules`
- Add Gitlink: `vendor/odoo-design-themes`
- Modify: `docker/Dockerfile`
- Modify: `.env.example`
- Modify: `scripts/validate-repository.sh`
- Modify: `scripts/deploy-image.sh`
- Modify: `tests/test_repository_contract.sh`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/ci-cd.md`
- Modify: `docs/deployment.md`
- Modify: `docs/gcp-staging.md`

**Interfaces:**
- Consumes: green `feat/evolve-odoo19-theme`, migration helper from Task 7, `odoo/design-themes@a1818df...`.
- Produces: image modules `theme_common`, `facodi_learning`, `theme_facodi`; runtime module list `facodi_learning,theme_facodi`.

- [ ] **Step 1: Add failing composition/runtime assertions**

Update `tests/test_repository_contract.sh`:

```bash
git ls-files --stage vendor/odoo-design-themes | grep -Eq '^160000 ' || fail "vendor/odoo-design-themes must be a Git submodule"
[[ -f vendor/odoo-design-themes/theme_common/__manifest__.py ]] || fail "pinned theme_common manifest missing"
[[ -f addons/facodi-theme/theme_facodi/__manifest__.py ]] || fail "theme_facodi manifest missing from theme submodule"

grep -Fq 'vendor/odoo-design-themes' .gitmodules || fail "design-themes submodule declaration missing"
grep -Fq 'theme_common' docker/Dockerfile || fail "Dockerfile must explicitly bake theme_common"
grep -Fq 'FACODI_MODULES=facodi_learning,theme_facodi' .env.example || fail "runtime module list must use theme_facodi"
grep -Fq 'migrate-theme-module-name.sh' scripts/deploy-image.sh || fail "deploy script must invoke theme module rename migration"
```

Replace existing current-state checks for `website_facodi` with `theme_facodi`.

- [ ] **Step 2: Run and confirm RED**

```bash
bash tests/test_repository_contract.sh
```

Expected: new upstream/theme/runtime assertions fail.

- [ ] **Step 3: Pin upstream design-themes**

```bash
git submodule add -b 19.0 https://github.com/odoo/design-themes.git vendor/odoo-design-themes
git -C vendor/odoo-design-themes checkout a1818df4ade65406c0cacae8b1ea676e6f70095f
git add .gitmodules vendor/odoo-design-themes
```

The Gitlink SHA is the actual reproducibility boundary.

- [ ] **Step 4: Bake only `theme_common` from upstream**

Update `docker/Dockerfile` so it keeps the existing FACODI-addon discovery loop and adds:

```dockerfile
COPY vendor/odoo-design-themes/theme_common/ /opt/odoo-theme-common/
```

Inside the existing `RUN` block, after FACODI addon copying:

```dockerfile
test -f /opt/odoo-theme-common/__manifest__.py; \
cp -a /opt/odoo-theme-common /mnt/extra-addons/theme_common; \
```

Do not copy `vendor/odoo-design-themes/` wholesale.

- [ ] **Step 5: Update repository validation**

Require:

```bash
git ls-files --stage addons/facodi-learning | grep -Eq '^160000 ' || fail "addons/facodi-learning is not a Gitlink"
git ls-files --stage addons/facodi-theme | grep -Eq '^160000 ' || fail "addons/facodi-theme is not a Gitlink"
git ls-files --stage vendor/odoo-design-themes | grep -Eq '^160000 ' || fail "vendor/odoo-design-themes is not a Gitlink"

[[ -f addons/facodi-learning/facodi_learning/__manifest__.py ]] || fail "facodi_learning manifest is missing"
[[ -f addons/facodi-theme/theme_facodi/__manifest__.py ]] || fail "theme_facodi manifest is missing"
[[ -f vendor/odoo-design-themes/theme_common/__manifest__.py ]] || fail "theme_common manifest is missing"
```

Also reject accidental full upstream copying:

```bash
if grep -Eq 'COPY[[:space:]]+vendor/odoo-design-themes/[[:space:]]' docker/Dockerfile; then
  fail "Dockerfile must copy only theme_common, not all design themes"
fi
```

- [ ] **Step 6: Switch runtime module list and invoke migration before state resolution**

`.env.example`:

```dotenv
FACODI_MODULES=facodi_learning,theme_facodi
```

`deploy-image.sh` default:

```bash
: "${FACODI_MODULES:=facodi_learning,theme_facodi}"
```

Immediately after:

```bash
"${COMPOSE[@]}" up -d db
```

call:

```bash
bash "$ROOT_DIR/scripts/migrate-theme-module-name.sh"
```

This must execute before the loop that decides install vs update state.

- [ ] **Step 7: Update current docs**

Replace active `website_facodi` technical-module references with `theme_facodi` in current README/deployment/architecture/CI/staging docs. Historical design/plan documents may retain the old name when describing prior state.

Document first rename deployment as:

```text
1. verify database + filestore backup;
2. start PostgreSQL;
3. rename legacy module registry/XML-ID ownership if required;
4. resolve install/update state for facodi_learning and theme_facodi;
5. run Odoo install/upgrade;
6. start Odoo and healthcheck;
7. later deployments no-op the rename because website_facodi is absent.
```

- [ ] **Step 8: Run contract/validator/image build**

```bash
bash tests/test_repository_contract.sh
bash scripts/validate-repository.sh
docker build -f docker/Dockerfile -t facodi-theme-evolution:test .
```

Inspect image:

```bash
docker run --rm --entrypoint bash facodi-theme-evolution:test -lc \
  'test -f /mnt/extra-addons/theme_common/__manifest__.py && \
   test -f /mnt/extra-addons/theme_facodi/__manifest__.py && \
   test -f /mnt/extra-addons/facodi_learning/__manifest__.py && \
   test ! -d /mnt/extra-addons/theme_bewise'
```

Expected: exit 0.

- [ ] **Step 9: Commit**

```bash
git add .gitmodules vendor/odoo-design-themes docker/Dockerfile .env.example scripts tests README.md docs
git commit -m "build: integrate theme_facodi and pinned theme_common"
```

---

### Task 9: Advance the theme submodule and perform fresh/migrated staging validation

**Repositories:**
- `marcelo-m7/facodi-theme`
- `marcelo-m7/facodi-monorepo`

**Files:**
- Update Gitlink: `facodi-monorepo/addons/facodi-theme`

**Interfaces:**
- Consumes: green remote branch `feat/evolve-odoo19-theme` and Task 8 monorepo integration.
- Produces: one immutable Odoo image validated on fresh and migrated databases.

- [ ] **Step 1: Verify theme branch is fully green**

In `facodi-theme`:

```bash
bash tests/test_module_contract.sh
git rev-parse HEAD
```

Require the GitHub Actions run for that exact HEAD to report success. Do not integrate a theme SHA whose CI is pending or failed.

- [ ] **Step 2: Resolve the exact green remote branch SHA without a placeholder**

In `facodi-monorepo`:

```bash
THEME_SHA="$(git ls-remote https://github.com/marcelo-m7/facodi-theme.git refs/heads/feat/evolve-odoo19-theme | awk '{print $1}')"
test -n "$THEME_SHA"
printf 'Integrating FACODI theme SHA: %s\n' "$THEME_SHA"
git -C addons/facodi-theme fetch origin "$THEME_SHA"
git -C addons/facodi-theme checkout "$THEME_SHA"
git add addons/facodi-theme
```

- [ ] **Step 3: Run complete monorepo validation**

```bash
bash tests/test_repository_contract.sh
bash scripts/validate-repository.sh
docker build -f docker/Dockerfile -t facodi-odoo:theme-evolution .
```

- [ ] **Step 4: Validate a fresh database**

Start the existing Compose stack with:

```dotenv
FACODI_IMAGE=facodi-odoo:theme-evolution
FACODI_MODULES=facodi_learning,theme_facodi
```

Expected:

```text
facodi_learning installed
theme_common installed as dependency
theme_facodi installed
website_facodi absent
/ returns HTTP 200
/slides returns HTTP 200
```

- [ ] **Step 5: Validate the rename on a disposable copy of an existing database**

Before deployment record:

```sql
SELECT count(*) FROM website_page;
SELECT name, state FROM ir_module_module WHERE name='website_facodi';
```

Run the new deploy flow. Afterward verify:

```sql
SELECT name, state
FROM ir_module_module
WHERE name IN ('website_facodi', 'theme_facodi');
SELECT count(*) FROM website_page;
```

Expected: `theme_facodi | installed`, no `website_facodi` row, and unchanged `website_page` count. Open the existing homepage and confirm editor-created content is still present.

- [ ] **Step 6: Perform visual acceptance against `edu-open2`**

Compare staging with `https://edu-open2.odoo.com` at desktop and mobile widths. Acceptance criteria:

```text
purple/blue FACODI identity remains dominant
standard Odoo navigation remains editable
FACODI snippets are editable/movable blocks
no lime/black identity takeover
/slides remains standard website_slides behavior
course/lesson navigation works
logo/favicon remain configurable through Odoo
keyboard focus remains visible
```

If a color token differs materially from the current website, change only the demonstrably different theme token and rerun the relevant theme tests/CI.

- [ ] **Step 7: Commit submodule advancement**

```bash
git add addons/facodi-theme
git commit -m "chore: advance FACODI theme evolution to ${THEME_SHA}"
```

---

## Final Verification Matrix

Before merge/review require every row green:

```text
facodi-theme/tests/test_module_contract.sh            PASS
facodi-theme GitHub Actions Odoo 19 CI                PASS
theme_facodi clean install with pinned theme_common   PASS
theme_facodi post_install HttpCase                    PASS
frontend asset compilation                            PASS
homepage /                                            HTTP 200
catalog /slides                                       HTTP 200
standard favicon not hard-coded                       PASS
FACODI custom snippets registered                     PASS
Website Builder insert/edit/move/delete               PASS
monorepo/tests/test_repository_contract.sh            PASS
monorepo/scripts/validate-repository.sh                PASS
monorepo Docker build                                 PASS
image contains theme_common/theme_facodi              PASS
image excludes unrelated official design themes       PASS
fresh DB deployment                                   PASS
legacy website_facodi DB migration                    PASS
existing website_page count/content preserved         PASS
staging visual comparison with edu-open2              PASS
```

## Rollback Boundary

The first deployment that renames the installed module must be preceded by the normal database + filestore backup. Image rollback alone is not a complete rollback boundary because the module registry/XML-ID ownership changes from `website_facodi` to `theme_facodi`. If validation fails after the migration, restore the pre-deployment database/filestore backup together with the previous image; do not reconstruct the old module metadata manually.

## Implementation Order

Execute Tasks 1-6 in `facodi-theme` first. Require a green exact theme commit before Tasks 7-8 change the monorepo. Task 9 is the integration/staging gate and must not start until both repositories' preceding tests are green.
