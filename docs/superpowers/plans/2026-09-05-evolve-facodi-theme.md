# FACODI Theme Evolution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evolve `marcelo-m7/facodi-theme` from the initial `website_facodi` styling addon into a proper Odoo 19 `theme_facodi` theme that preserves the current FACODI purple/blue identity, uses Odoo Website Builder and `website_slides` as the authoritative Website/LMS surfaces, and integrates reproducibly with `facodi-monorepo`.

**Architecture:** `theme_facodi` remains presentation-only. It follows `odoo/design-themes` conventions for primary variables, primary snippet template generation, theme configurator metadata, asset registration and narrowly scoped QWeb inheritance. `facodi-monorepo` pins `odoo/design-themes` separately and bakes only `theme_common` into the runtime image together with the FACODI addons. Existing Website content remains standard Odoo data and is preserved across the technical-module rename.

**Tech Stack:** Odoo 19 Community, `theme_common`, `website_slides`, QWeb/XML, SCSS/Bootstrap, Python `odoo.tests.HttpCase`, Bash contract tests, PostgreSQL 16, Docker, GitHub Actions, Git submodules.

**Spec:** `docs/superpowers/specs/2026-09-05-facodi-theme-evolution-design.md`

## Global Constraints

- Target Odoo version: **Odoo 19 Community**.
- Target technical addon name: **`theme_facodi`**.
- Repository name remains **`facodi-theme`**.
- Baseline addon dependencies are exactly `theme_common` and `website_slides`; do not add FACODI business-addon dependencies.
- `theme_common` must come from a pinned Odoo 19-compatible `odoo/design-themes` checkout; never vendor/copy its source into this repository.
- Pin `odoo/design-themes` commit **`a1818df4ade65406c0cacae8b1ea676e6f70095f`** for this implementation cycle.
- Visual priority is the current `https://edu-open2.odoo.com`; purple/blue is the implementation baseline and the Open2 lime/black proposal must not replace it.
- Website Builder remains authoritative for pages, menus, snippets, colors, logo, favicon, header/footer configuration and editor-created content.
- `website_slides` remains authoritative for courses, lessons, membership, progress and learner-facing routes.
- Do not place ad-hoc `request.env`, `sudo()` or ORM searches in theme QWeb.
- Do not copy complete Odoo Website/eLearning templates. Use theme values, stable CSS hooks and narrow inheritance.
- Do not hard-code a theme favicon or take ownership of the standard Website logo.
- No custom JavaScript unless a concrete editor/presentation requirement cannot be achieved with standard Odoo/Bootstrap behavior.
- Preserve editor-created Website content through the module-name migration.
- Use TDD for behavior changes and make focused commits after each task.

---

## Target File Map

### `marcelo-m7/facodi-theme`

```text
.github/workflows/ci.yml                         clean Odoo 19 install/test with pinned design-themes
README.md                                        install/use/architecture summary
docs/architecture.md                             technical boundary and lifecycle
tests/test_module_contract.sh                    fast repository/module-structure regression test

theme_facodi/
├── __init__.py                                  package marker only
├── __manifest__.py                              theme metadata, dependencies, data and configurator
├── data/
│   ├── generate_primary_template.xml            standard primary snippet generation hook
│   └── ir_asset.xml                             primary-variable asset registration
├── views/
│   ├── customizations.xml                       narrow Website layout/theme metadata inheritance
│   ├── snippets.xml                             FACODI snippet group + focused custom snippets
│   └── website_slides.xml                       intentionally narrow eLearning inheritance file
├── static/
│   ├── description/
│   │   └── theme_facodi.svg                     theme/snippet thumbnail
│   └── src/
│       ├── img/
│       │   ├── logo.svg                         optional project-owned asset
│       │   └── favicon.svg                      optional project-owned asset, never forced
│       └── scss/
│           ├── primary_variables.scss           Odoo palette/theme values only
│           ├── bootstrap_overridden.scss        semantic Bootstrap overrides
│           ├── components.scss                  reusable FACODI UI primitives
│           ├── website.scss                     standard Website refinements
│           ├── snippets.scss                    FACODI snippet presentation
│           └── website_slides.scss              standard eLearning presentation
└── tests/
    ├── __init__.py
    └── test_website.py                          route/theme-standard preservation tests
```

The old `website_facodi/` directory is removed in the rename task. Do not keep two installable FACODI themes.

### `marcelo-m7/facodi-monorepo`

```text
.gitmodules                                      add upstream design-themes submodule
vendor/odoo-design-themes                        Gitlink pinned to approved 19.0 commit
docker/Dockerfile                                copy FACODI addons + theme_common explicitly
.env.example                                     runtime technical-module list
scripts/validate-repository.sh                    composition contract
scripts/deploy-image.sh                           module list + controlled rename hook
scripts/migrate-theme-module-name.sh              one-time DB metadata rename, idempotent
tests/test_repository_contract.sh                 composition/migration contract tests
README.md                                         module/dependency documentation
docs/architecture.md                              updated composition map
docs/ci-cd.md                                     pinned theme dependency/module name
docs/deployment.md                                migration/deploy steps
docs/gcp-staging.md                               staging module name
```

---

### Task 1: Rename the technical addon and establish the Odoo theme skeleton

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
- Delete after migration: `website_facodi/`

**Interfaces:**
- Consumes: Odoo 19 module discovery and `theme_common` theme lifecycle.
- Produces: one installable addon named `theme_facodi`, manifest dependency contract `['theme_common', 'website_slides']`, and asset key `theme_facodi.primary_variables_scss`.

- [ ] **Step 1: Write the failing repository contract test**

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

if grep -R -nE 'request\.env|sudo\(\)\.search|href="/theme_facodi/static/src/img/favicon\.svg"' theme_facodi --include='*.xml'; then
  fail "theme QWeb contains forbidden data query or forced favicon"
fi

echo "PASS: theme module contract"
```

- [ ] **Step 2: Run the contract test and confirm RED**

```bash
bash tests/test_module_contract.sh
```

Expected: `FAIL: theme_facodi manifest missing` because only `website_facodi` exists.

- [ ] **Step 3: Create the minimal `theme_facodi` skeleton**

Create an empty `theme_facodi/__init__.py`.

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

Create temporary valid XML files for `views/customizations.xml`, `views/snippets.xml`, and `views/website_slides.xml` containing only:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo/>
```

Use `git mv` for the two project-owned SVG assets. Do not create a favicon `<link>` in QWeb. Create `static/description/theme_facodi.svg` as a lightweight project-owned purple/blue preview using only SVG primitives; do not embed a font file or external image.

Remove `website_facodi/` only after reusable assets have been moved.

- [ ] **Step 4: Run the contract test and confirm GREEN**

```bash
bash tests/test_module_contract.sh
```

Expected: `PASS: theme module contract`.

- [ ] **Step 5: Commit**

```bash
git add tests theme_facodi
git add -u website_facodi
git commit -m "refactor: migrate FACODI addon to theme_facodi"
```

---

### Task 2: Make theme-repository CI install the real upstream `theme_common`

**Files:**
- Modify: `.github/workflows/ci.yml`
- Modify: `tests/test_module_contract.sh`

**Interfaces:**
- Consumes: `odoo/design-themes` commit `a1818df4ade65406c0cacae8b1ea676e6f70095f`, official `odoo:19.0`, and `postgres:16`.
- Produces: clean-install CI for `theme_facodi` with `/mnt/design-themes` and `/mnt/facodi-addons` on `addons_path`.

- [ ] **Step 1: Add failing CI-contract assertions**

Append to `tests/test_module_contract.sh`:

```bash
grep -Fq 'a1818df4ade65406c0cacae8b1ea676e6f70095f' .github/workflows/ci.yml || fail "CI must pin the approved design-themes commit"
grep -Fq '/mnt/design-themes' .github/workflows/ci.yml || fail "CI must mount design-themes"
grep -Fq -- '-i theme_facodi' .github/workflows/ci.yml || fail "CI must install theme_facodi"
grep -Fq -- '--test-tags /theme_facodi' .github/workflows/ci.yml || fail "CI must run theme_facodi tests"
```

- [ ] **Step 2: Run and confirm RED**

```bash
bash tests/test_module_contract.sh
```

Expected: CI contract failure because the workflow still installs `website_facodi` and has no pinned design-themes checkout.

- [ ] **Step 3: Update `.github/workflows/ci.yml`**

Add after `actions/checkout@v4`:

```yaml
      - name: Checkout pinned Odoo design themes
        run: |
          git clone --filter=blob:none https://github.com/odoo/design-themes.git "$RUNNER_TEMP/design-themes"
          git -C "$RUNNER_TEMP/design-themes" checkout a1818df4ade65406c0cacae8b1ea676e6f70095f
          test -f "$RUNNER_TEMP/design-themes/theme_common/__manifest__.py"
```

Rename the CI DB from `website_facodi_ci` to `theme_facodi_ci` in both PostgreSQL startup/readiness and the Odoo command. Replace the install/test step with:

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

- [ ] **Step 4: Run fast contract + workflow**

```bash
bash tests/test_module_contract.sh
```

Expected: PASS. Then observe the GitHub Actions job: `theme_common` resolves from the pinned checkout and Odoo reaches the test phase without missing-dependency/XML errors.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/ci.yml tests/test_module_contract.sh
git commit -m "ci: test theme against pinned Odoo design themes"
```

---

### Task 3: Implement FACODI palette, theme values and separated SCSS assets

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
- Consumes: Odoo `$o-color-palettes`, `$o-theme-color-palettes`, `$o-selected-color-palettes-names`, `$o-website-values-palettes`, Bootstrap variables.
- Produces: palette `facodi`; SCSS variables `$facodi-purple`, `$facodi-blue`, `$facodi-surface`, `$facodi-ink`, `$facodi-heading`; focused frontend bundles.

- [ ] **Step 1: Write failing palette/asset assertions**

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

Do **not** force `header-template` or `footer-template` in this release. Preserve the active standard configuration while styling standard chrome. If the staging/live comparison later proves a different standard header/footer template is required, change only the corresponding Odoo theme value in a follow-up commit.

- [ ] **Step 4: Add semantic Bootstrap overrides**

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

- [ ] **Step 5: Add reusable/global styles and keep focused empty files intentional**

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

Create `snippets.scss` containing `// FACODI Website Builder snippets; populated in Task 4.` and `website_slides.scss` containing `// Standard website_slides refinements; populated in Task 5.`. These comments define an intentional task boundary rather than an unfinished production TODO.

- [ ] **Step 6: Register frontend SCSS in the manifest**

Add:

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

Primary variables remain registered through `ir.asset`; do not duplicate them in `web.assets_frontend`.

- [ ] **Step 7: Run contract + Odoo install tests**

```bash
bash tests/test_module_contract.sh
```

Then run/observe CI. Expected: contract PASS and no SCSS compilation error.

- [ ] **Step 8: Commit**

```bash
git add theme_facodi tests/test_module_contract.sh
git commit -m "feat: add FACODI Odoo theme palette and assets"
```

---

### Task 4: Add editable FACODI Website Builder snippets without replacing the homepage

**Files:**
- Modify: `theme_facodi/views/snippets.xml`
- Modify: `theme_facodi/static/src/scss/snippets.scss`
- Create: `theme_facodi/tests/__init__.py`
- Create: `theme_facodi/tests/test_website.py`

**Interfaces:**
- Consumes: standard `website.snippets`, Website Builder editable structure, Bootstrap grid/utilities.
- Produces: snippet group `facodi`; view keys `theme_facodi.s_facodi_hero`, `theme_facodi.s_facodi_learning_journey`, `theme_facodi.s_facodi_institutional`.

- [ ] **Step 1: Create the failing Odoo snippet test**

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
        views = self.env["ir.ui.view"].search([
            ("key", "in", [
                "theme_facodi.s_facodi_hero",
                "theme_facodi.s_facodi_learning_journey",
                "theme_facodi.s_facodi_institutional",
            ])
        ])
        self.assertEqual(len(views), 3)
```

- [ ] **Step 2: Run the Odoo test and confirm RED**

Run the Task 2 CI-equivalent Odoo command with `--test-tags /theme_facodi`.

Expected: the three snippet keys are absent because `views/snippets.xml` is empty.

- [ ] **Step 3: Register one group and three focused snippets**

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
                            <p class="mb-0">Use este bloco para apresentar o enquadramento institucional, parceiros e iniciativas da FACODI através do editor do Website.</p>
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

The institutional snippet deliberately contains editable neutral copy; it does not encode a funding/business rule.

- [ ] **Step 4: Add snippet-specific SCSS**

Replace the intentional comment in `snippets.scss` with:

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

- [ ] **Step 5: Run tests and confirm GREEN**

Run `bash tests/test_module_contract.sh` and the Odoo test suite. Expected: the three snippet keys load, XML parses, assets compile.

- [ ] **Step 6: Manually verify Website Builder insertion**

On a test instance, open Website -> Edit -> Blocks. Confirm group `FACODI` appears and each block can be inserted, text-edited, moved and deleted with standard Website Builder controls.

- [ ] **Step 7: Commit**

```bash
git add theme_facodi
git commit -m "feat: add editable FACODI website snippets"
```

---

### Task 5: Preserve standard layout/logo/favicon and refine `website_slides` presentation

**Files:**
- Modify: `theme_facodi/views/customizations.xml`
- Modify: `theme_facodi/views/website_slides.xml`
- Modify: `theme_facodi/static/src/scss/website_slides.scss`
- Modify: `theme_facodi/tests/test_website.py`

**Interfaces:**
- Consumes: `website.layout`, standard Odoo favicon/logo behavior, and stable `website_slides` routes/markup.
- Produces: styling hook `facodi-site`, theme-color metadata, standard `/` and `/slides` behavior.

- [ ] **Step 1: Add failing route/standard-preservation tests**

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

Add a repository-level assertion to `tests/test_module_contract.sh`:

```bash
[[ ! -d theme_facodi/controllers ]] || fail "presentation theme must not add parallel learning routes/controllers"
```

- [ ] **Step 2: Run and confirm RED**

Expected: homepage class test fails because `customizations.xml` is still empty.

- [ ] **Step 3: Implement narrow `website.layout` inheritance**

Replace `views/customizations.xml` with:

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

Do not add a favicon `<link>`, hard-coded logo, replacement header or replacement footer.

- [ ] **Step 4: Keep `website_slides.xml` intentionally structure-free**

Replace it with:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- The first evolved release needs no structural website_slides override. -->
</odoo>
```

This is a deliberate standard-first decision. Add QWeb inheritance only in a later change if a concrete requirement cannot be met through supported theme variables or verified standard selectors.

- [ ] **Step 5: Implement eLearning SCSS only against selectors verified in Odoo 19**

Start with these candidate rules in `website_slides.scss`:

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

Before committing, inspect the actual Odoo 19 `/slides`, course, and lesson markup. Remove any selector not present in Odoo 19 rather than creating replacement markup merely to satisfy the CSS. Keep only verified selectors.

- [ ] **Step 6: Run Odoo tests and asset compilation**

Expected: all tests PASS; `/` and `/slides` return 200; no forced favicon URL; assets compile.

- [ ] **Step 7: Manual responsive/accessibility smoke test**

Verify widths 375px, 768px, 1440px: standard navigation works; keyboard focus is visible; hero buttons are keyboard reachable; `/slides` cards/navigation work; no information depends only on hover; reduced-motion disables custom card transition.

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
- Consumes: implemented contracts from Tasks 1-5.
- Produces: current contributor/operator docs naming `theme_facodi`, `theme_common`, and standard Odoo ownership boundaries.

- [ ] **Step 1: Add stale-name/documentation checks**

Append:

```bash
if grep -R -n 'website_facodi' README.md docs/architecture.md; then
  fail "current docs still describe website_facodi as the active addon"
fi

grep -Fq 'theme_common' README.md || fail "README must document theme_common dependency"
grep -Fq 'odoo/design-themes' docs/architecture.md || fail "architecture must document upstream design themes"
```

- [ ] **Step 2: Run and confirm RED**

Expected: existing README/architecture still name `website_facodi`.

- [ ] **Step 3: Rewrite README around the evolved contract**

It must explicitly state:

```text
repository: facodi-theme
technical module: theme_facodi
runtime dependencies: theme_common + website_slides
visual authority: current edu-open2 identity
Website Builder: authoritative for editable pages and branding
eLearning: standard website_slides
no dependency on facodi_learning
no forced favicon/logo
```

Installation example:

```bash
odoo -d facodi \
  --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/opt/odoo-design-themes,/path/to/facodi-theme \
  -i theme_facodi \
  --stop-after-init
```

- [ ] **Step 4: Rewrite `docs/architecture.md`**

Use this diagram and explain the standard-first decision rule:

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

Explicitly prohibit QWeb business-data searches and full standard-template copies.

- [ ] **Step 5: Run contract and commit**

```bash
bash tests/test_module_contract.sh
git add README.md docs/architecture.md tests/test_module_contract.sh
git commit -m "docs: document evolved FACODI Odoo theme"
```

---

### Task 7: Add a controlled one-time `website_facodi` -> `theme_facodi` registry migration in `facodi-monorepo`

**Repository:** `marcelo-m7/facodi-monorepo`

**Files:**
- Create: `scripts/migrate-theme-module-name.sh`
- Modify: `tests/test_repository_contract.sh`

**Interfaces:**
- Consumes: existing monorepo `.env`, `infrastructure/docker-compose.yml`, PostgreSQL service `db`, Docker/Compose availability.
- Produces: idempotent metadata migration where `ir_module_module.name` and `ir_model_data.module` ownership move from `website_facodi` to `theme_facodi` before the first new-theme upgrade.

- [ ] **Step 1: Add failing script contract checks**

Append to `tests/test_repository_contract.sh`:

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

- [ ] **Step 3: Implement the idempotent Compose-based migration**

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

This changes only Odoo module metadata/XML-ID ownership. It must not delete Website pages, menus, views, attachments or other editorial data.

- [ ] **Step 4: Verify idempotence on a disposable copy/database**

Using the existing Compose PostgreSQL service or a disposable stack, verify three cases:

1. only `website_facodi` exists -> script exits 0 and renames module + XML-ID ownership;
2. rerun after rename -> exits 0 with `No legacy website_facodi module record`;
3. both module records exist -> exits 1 before mutation.

For case 1, verify:

```sql
SELECT name, state FROM ir_module_module WHERE name IN ('website_facodi', 'theme_facodi');
SELECT module, name FROM ir_model_data WHERE name='website_layout';
```

Expected module name/ownership: `theme_facodi` only.

- [ ] **Step 5: Run contract and commit**

```bash
bash tests/test_repository_contract.sh
git add scripts/migrate-theme-module-name.sh tests/test_repository_contract.sh
git commit -m "feat: add FACODI theme module rename migration"
```

---

### Task 8: Pin `odoo/design-themes`, bake only `theme_common`, and switch runtime to `theme_facodi`

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
- Consumes: upstream `odoo/design-themes` pinned at `a1818df4ade65406c0cacae8b1ea676e6f70095f`, green `facodi-theme` commit from Tasks 1-6, migration script from Task 7.
- Produces: runtime modules `facodi_learning,theme_facodi`; image modules `theme_common`, `facodi_learning`, `theme_facodi`; controlled migration before install/update state resolution.

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

Replace existing `website_facodi` manifest/default assertions with `theme_facodi`.

- [ ] **Step 2: Run and confirm RED**

```bash
bash tests/test_repository_contract.sh
```

Expected: vendor submodule/new manifest/runtime module checks fail.

- [ ] **Step 3: Add/pin the upstream theme source**

```bash
git submodule add -b 19.0 https://github.com/odoo/design-themes.git vendor/odoo-design-themes
git -C vendor/odoo-design-themes checkout a1818df4ade65406c0cacae8b1ea676e6f70095f
git add .gitmodules vendor/odoo-design-themes
```

The Gitlink SHA is the reproducibility boundary; `branch = 19.0` only documents upstream lineage.

- [ ] **Step 4: Update Dockerfile to copy only `theme_common` from upstream**

Retain the FACODI addon discovery loop for `addons/`, then explicitly copy `theme_common`:

```dockerfile
COPY addons/ /opt/facodi-addon-sources/
COPY vendor/odoo-design-themes/theme_common/ /opt/odoo-theme-common/
RUN set -eux; \
    mkdir -p /mnt/extra-addons; \
    found=0; \
    for manifest in /opt/facodi-addon-sources/*/*/__manifest__.py; do \
        [ -e "$manifest" ] || continue; \
        module_dir="$(dirname "$manifest")"; \
        module_name="$(basename "$module_dir")"; \
        [ ! -e "/mnt/extra-addons/$module_name" ] || { echo "duplicate Odoo module: $module_name" >&2; exit 1; }; \
        cp -a "$module_dir" "/mnt/extra-addons/$module_name"; \
        found=1; \
    done; \
    [ "$found" -eq 1 ] || { echo "no FACODI addons found in submodule sources" >&2; exit 1; }; \
    test -f /opt/odoo-theme-common/__manifest__.py; \
    cp -a /opt/odoo-theme-common /mnt/extra-addons/theme_common; \
    chown -R odoo:odoo /mnt/extra-addons
```

Do not copy `vendor/odoo-design-themes/` wholesale.

- [ ] **Step 5: Update repository validator**

Require the three Gitlinks/manifests:

```bash
git ls-files --stage addons/facodi-learning | grep -Eq '^160000 ' || fail "addons/facodi-learning is not a Gitlink"
git ls-files --stage addons/facodi-theme | grep -Eq '^160000 ' || fail "addons/facodi-theme is not a Gitlink"
git ls-files --stage vendor/odoo-design-themes | grep -Eq '^160000 ' || fail "vendor/odoo-design-themes is not a Gitlink"

[[ -f addons/facodi-learning/facodi_learning/__manifest__.py ]] || fail "facodi_learning manifest is missing"
[[ -f addons/facodi-theme/theme_facodi/__manifest__.py ]] || fail "theme_facodi manifest is missing"
[[ -f vendor/odoo-design-themes/theme_common/__manifest__.py ]] || fail "theme_common manifest is missing"
```

Also reject accidental full-upstream baking:

```bash
if grep -Eq 'COPY[[:space:]]+vendor/odoo-design-themes/[[:space:]]' docker/Dockerfile; then
  fail "Dockerfile must copy only theme_common, not all official design themes"
fi
```

- [ ] **Step 6: Switch runtime module names and invoke migration before state resolution**

Set `.env.example`:

```dotenv
FACODI_MODULES=facodi_learning,theme_facodi
```

Change `scripts/deploy-image.sh` default:

```bash
: "${FACODI_MODULES:=facodi_learning,theme_facodi}"
```

Immediately after `"${COMPOSE[@]}" up -d db` and before building `install_modules` / `update_modules`, call:

```bash
bash "$ROOT_DIR/scripts/migrate-theme-module-name.sh"
```

Because the helper uses the same `.env` and Compose file, no separate DB credentials/path contract is needed. `set -euo pipefail` must abort deployment if migration detects ambiguous/conflicting state.

- [ ] **Step 7: Update current docs**

Replace active technical-module references `website_facodi` -> `theme_facodi` in README/current architecture/deployment/CI/staging docs. Historical specs/plans that explicitly describe previous state may retain the old name.

Document the first rename deployment exactly:

```text
1. create/verify the normal database + filestore backup;
2. start the DB;
3. migrate website_facodi registry/XML-ID ownership to theme_facodi when required;
4. resolve install/update state for facodi_learning and theme_facodi;
5. run Odoo module install/upgrade;
6. start Odoo and healthcheck;
7. subsequent deploys skip the rename because website_facodi no longer exists.
```

- [ ] **Step 8: Run contract, validation and image build**

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

### Task 9: Advance the theme submodule and perform full staging validation

**Repositories:**
- `marcelo-m7/facodi-theme`
- `marcelo-m7/facodi-monorepo`

**Files:**
- Monorepo Gitlink: `addons/facodi-theme`
- No new production code unless validation exposes a concrete defect

**Interfaces:**
- Consumes: green theme feature branch and monorepo integration from Tasks 7-8.
- Produces: one immutable image containing `facodi_learning`, `theme_facodi`, `theme_common`, validated on fresh and migrated databases.

- [ ] **Step 1: Verify complete theme repository before integration**

```bash
bash tests/test_module_contract.sh
```

Run the exact CI and require:

```text
theme_facodi clean install: PASS
/theme_facodi tests: PASS
frontend SCSS compilation: PASS
/ route: HTTP 200
/slides route: HTTP 200
```

Do not advance the monorepo Gitlink until this commit is green.

- [ ] **Step 2: Advance `addons/facodi-theme` to the verified SHA**

At execution time, substitute the literal green theme commit SHA:

```bash
git -C addons/facodi-theme fetch origin
git -C addons/facodi-theme checkout <verified-theme-commit>
git add addons/facodi-theme
```

Record the literal SHA in the resulting monorepo commit body so reviewers can trace the exact theme release.

- [ ] **Step 3: Run full monorepo validation**

```bash
bash tests/test_repository_contract.sh
bash scripts/validate-repository.sh
docker build -f docker/Dockerfile -t facodi-odoo:theme-evolution .
```

Start the existing Compose stack with:

```dotenv
FACODI_IMAGE=facodi-odoo:theme-evolution
FACODI_MODULES=facodi_learning,theme_facodi
```

- [ ] **Step 4: Validate a fresh database**

Expected:

```text
facodi_learning installed
theme_common installed as dependency
theme_facodi installed
website_facodi absent
/ returns 200
/slides returns 200
```

- [ ] **Step 5: Validate upgrade path on a disposable copy of an existing database**

Before deployment, record the count of `website.page` rows and confirm `website_facodi` is installed. Run the new migration/deployment. Verify:

```sql
SELECT name, state
FROM ir_module_module
WHERE name IN ('website_facodi', 'theme_facodi');
```

Expected only:

```text
theme_facodi | installed
```

Recheck `website.page` count; it must be unchanged. Open the existing homepage and confirm editor-created content remains present.

- [ ] **Step 6: Perform visual acceptance against `edu-open2`**

Compare staging to `https://edu-open2.odoo.com` at desktop and mobile widths. Acceptance is identity/recognizable UX, not pixel-for-pixel copying.

Required checks:

```text
purple/blue FACODI identity remains dominant
navigation remains Odoo-standard and editable
homepage snippets remain movable/editable Website Builder blocks
no lime/black identity takeover
course catalog remains standard website_slides
course/lesson navigation still works
logo/favicon remain configurable through Odoo
keyboard focus remains visible
```

If a color token differs materially from the live reference, change only the demonstrably different theme token and rerun Task 3/5 tests. Do not redesign unrelated components during acceptance.

- [ ] **Step 7: Commit monorepo Gitlink advancement**

```bash
git add addons/facodi-theme
git commit -m "chore: advance FACODI theme evolution"
```

---

## Final Verification Matrix

Before requesting merge/review, every row must be green:

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
image contains theme_common/theme_facodi               PASS
image does not copy all official design themes         PASS
fresh DB deployment                                   PASS
legacy website_facodi DB migration                    PASS
existing website.page content preserved               PASS
staging visual comparison with edu-open2               PASS
```

## Rollback Boundary

The first deployment that renames the installed module must be preceded by the normal database + filestore backup. Image rollback alone is not a complete rollback boundary because module registry/XML-ID ownership changes from `website_facodi` to `theme_facodi`. If validation fails after that migration, restore the pre-deployment database/filestore backup together with the prior image rather than trying to recreate the old module state ad hoc.

## Implementation Order

Execute Tasks 1-6 in the `facodi-theme` feature branch first. Only after the theme repository is green, execute Tasks 7-8 in `facodi-monorepo`. Task 9 is the integration gate and must not start with an unverified theme commit.
