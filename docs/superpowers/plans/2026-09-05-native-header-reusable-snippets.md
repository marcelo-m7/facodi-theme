# FACODI Native Header and Reusable Snippets Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Follow TDD for every behavioral change and use `superpowers:verification-before-completion` before claiming the work is complete.

**Goal:** Preserve the approved FACODI Website navigation appearance while replacing the unconditional full-header override with Odoo 19's native selectable header-template mechanism, and split the nine existing FACODI Website Builder blocks into stable reusable source units without changing their public XML IDs, translations, page-composition contracts, or eLearning ownership.

**Architecture:** `theme_facodi` remains a presentation-only Odoo 19 Community theme. The header becomes a registered `theme.utils` header template exposed through `website.HeaderTemplateOption`; it replaces only the standard header `<nav>` in the same manner as Odoo's own `theme_test_custo`, while Odoo keeps ownership of the outer header, configured brand/logo, menus, Portal identity, mobile header and editor controls. The nine existing `s_facodi_*` templates keep their XML IDs but move from one monolithic QWeb file into one file per block, with a small registry file. `facodi-deploy` remains a composition repository and, only after the theme commit is green, advances its `addons/facodi-theme` gitlink and corresponding exact-pin test.

**Tech Stack:** Odoo 19 Community, `theme_common`, `website_slides`, `theme.utils`, Odoo Website Builder / `html_builder.assets`, QWeb/XML, SCSS/Bootstrap, Python `odoo.tests.HttpCase`, native Odoo i18n PO/POT catalogues, Bash contract tests, PostgreSQL 16, Docker, GitHub Actions, Git submodules, Coolify runtime validation.

**Spec:** `docs/superpowers/specs/2026-09-05-native-header-reusable-snippets-design.md`

## Global Constraints

- Target Odoo version is **Odoo 19 Community**.
- Work on `marcelo-m7/facodi-theme` branch `feat/native-header-reusable-snippets`; do not modify `main` directly.
- Preserve the approved FACODI visual contract: Ink `#142846`, Cyan `#37BED2`, Blue `#3979C8`, Mint `#A7E8BE`, Sun `#EFFF00`, Paper `#F9FAFB`, strong borders and offset-shadow interaction language.
- The public header must remain visually equivalent to the approved screenshot: configurable logo at left, right-aligned Website menu, lime Portal/user action, light background and dark bottom separator.
- Do not style Odoo's backend/editor chrome.
- Runtime dependencies remain exactly `theme_common` and `website_slides`; do not add FACODI business-addon dependencies.
- `website.menu`, `website.submenu`, `website.placeholder_header_brand`, `portal.placeholder_user_sign_in`, `portal.user_dropdown`, `website.template_header_mobile` and `website_slides` remain authoritative.
- Do not add a parallel menu/authentication/mobile-navigation implementation.
- Do not add ORM access, `request.env`, `sudo()`, controllers, course queries, Website-page data dumps or forced logo/favicon behavior.
- Do not reintroduce an unconditional `xpath expr="//header" position="replace"`.
- Keep all nine public snippet XML IDs unchanged so page compositions and translation keys stay stable.
- Preserve the ten existing New Page compositions and their `t-snippet-call` references.
- Preserve native Odoo i18n for English source plus `pt_PT`, `es_ES`, `fr_FR`.
- Keep the current Odoo design-themes pin `a1818df4ade65406c0cacae8b1ea676e6f70095f` for this change.
- `facodi-deploy` receives no theme QWeb/SCSS. It only advances the exact theme gitlink after the theme CI is green.
- Do not trigger production deployment as part of this plan.

---

## Task 1: Define the native-header and split-snippet contracts in RED

**Files:**
- Modify: `tests/test_module_contract.sh`
- Modify: `tests/test_i18n_contract.sh`
- Modify: `theme_facodi/tests/test_website.py`

**Interfaces:**
- Consumes: current `theme_facodi` source and Odoo 19 theme conventions.
- Produces: failing contracts for the new file boundaries and supported Odoo header mechanism before production code changes.

### Step 1: Replace the old full-header assumptions in the fast repository contract

In `tests/test_module_contract.sh`, remove assertions that require the header to live in `views/customizations.xml` and add these checks near the existing theme-layout checks:

```bash
for path in \
  theme_facodi/models/__init__.py \
  theme_facodi/models/theme_models.py \
  theme_facodi/views/header.xml \
  theme_facodi/static/src/builder/header.xml \
  theme_facodi/static/src/img/template_header_facodi.svg; do
  [[ -f "$path" ]] || fail "missing native FACODI header file: $path"
done

grep -Fq 'from . import models' theme_facodi/__init__.py \
  || fail "theme root must load theme.utils extension"
grep -Fq 'from . import theme_models' theme_facodi/models/__init__.py \
  || fail "theme models package must load theme_models"
grep -Fq "_inherit = 'theme.utils'" theme_facodi/models/theme_models.py \
  || grep -Fq '_inherit = "theme.utils"' theme_facodi/models/theme_models.py \
  || fail "theme.utils extension missing"
grep -Fq 'theme_facodi.template_header_facodi' theme_facodi/models/theme_models.py \
  || fail "FACODI header must be registered with theme.utils"
grep -Fq '_theme_facodi_post_copy' theme_facodi/models/theme_models.py \
  || fail "theme post-copy hook must enable the FACODI header"

grep -Fq 'views/header.xml' theme_facodi/__manifest__.py \
  || fail "native FACODI header view missing from manifest"
grep -Fq 'html_builder.assets' theme_facodi/__manifest__.py \
  || fail "Website Builder asset bundle missing"
grep -Fq 'theme_facodi/static/src/builder/**/*' theme_facodi/__manifest__.py \
  || fail "FACODI builder assets missing"

if grep -R -n '<xpath[^>]*expr="//header"[^>]*position="replace"' theme_facodi --include='*.xml'; then
  fail "theme must not replace the complete Odoo header"
fi

grep -Fq 'id="template_header_facodi"' theme_facodi/views/header.xml \
  || fail "selectable FACODI header template missing"
grep -Fq 'xpath expr="//header//nav" position="replace"' theme_facodi/views/header.xml \
  || fail "FACODI header must replace only the standard nav extension point"
grep -Fq 'website.placeholder_header_brand' theme_facodi/views/header.xml \
  || fail "header must retain standard configurable Website brand"
grep -Fq 'website.navbar_nav' theme_facodi/views/header.xml \
  || fail "header must use the standard navbar list wrapper"
grep -Fq 'website.menu_id.child_id' theme_facodi/views/header.xml \
  || fail "header must use standard dynamic Website menus"
grep -Fq 't-call="website.submenu"' theme_facodi/views/header.xml \
  || fail "header must use native submenu recursion"
grep -Fq 'portal.placeholder_user_sign_in' theme_facodi/views/header.xml \
  || fail "header must retain standard Portal sign-in"
grep -Fq 'portal.user_dropdown' theme_facodi/views/header.xml \
  || fail "header must retain standard Portal user dropdown"

grep -Fq 't-inherit="website.HeaderTemplateOption"' theme_facodi/static/src/builder/header.xml \
  || fail "FACODI header must extend the native header template picker"
grep -Fq "'header-template': 'facodi'" theme_facodi/static/src/builder/header.xml \
  || fail "FACODI header picker must set the facodi header-template variable"
grep -Fq "views: ['theme_facodi.template_header_facodi']" theme_facodi/static/src/builder/header.xml \
  || fail "FACODI picker must activate the FACODI header view"
```

Add exact split-snippet expectations:

```bash
SNIPPET_IDS=(
  s_facodi_hero
  s_facodi_learning_journey
  s_facodi_institutional
  s_facodi_intro
  s_facodi_features
  s_facodi_community
  s_facodi_roadmap
  s_facodi_faq
  s_facodi_course_cta
)

[[ -f theme_facodi/views/snippets/snippets.xml ]] \
  || fail "FACODI snippet registry missing"

for snippet_id in "${SNIPPET_IDS[@]}"; do
  path="theme_facodi/views/snippets/${snippet_id}.xml"
  [[ -f "$path" ]] || fail "missing reusable snippet source: $path"
  grep -Fq "id=\"${snippet_id}\"" "$path" \
    || fail "snippet source does not define ${snippet_id}"
  count="$(grep -R -h -o "id=\"${snippet_id}\"" theme_facodi/views/snippets --include='*.xml' | wc -l)"
  [[ "$count" -eq 1 ]] || fail "${snippet_id} must be defined exactly once"
  grep -Fq "t-snippet=\"theme_facodi.${snippet_id}\"" theme_facodi/views/snippets/snippets.xml \
    || fail "${snippet_id} is not registered in Website Builder"
done

[[ ! -f theme_facodi/views/snippets.xml ]] \
  || fail "legacy monolithic snippets.xml must be removed"
```

Replace the existing Python parser at the bottom of the contract so it discovers snippet IDs from all files in `theme_facodi/views/snippets/`:

```python
from pathlib import Path
from xml.etree import ElementTree as ET

snippet_dir = Path("theme_facodi/views/snippets")
blocks = set()
for path in snippet_dir.glob("s_facodi_*.xml"):
    root = ET.parse(path).getroot()
    for node in root.findall("template"):
        if node.get("id", "").startswith("s_facodi_"):
            blocks.add(node.get("id"))

expected = {
    "s_facodi_hero",
    "s_facodi_learning_journey",
    "s_facodi_institutional",
    "s_facodi_intro",
    "s_facodi_features",
    "s_facodi_community",
    "s_facodi_roadmap",
    "s_facodi_faq",
    "s_facodi_course_cta",
}
assert blocks == expected, (blocks, expected)

pages = ET.parse("theme_facodi/views/page_templates.xml").getroot()
compositions = [
    node for node in pages.findall("template")
    if node.get("id", "").startswith("new_page_template_sections_")
]
assert len(compositions) == 10
for page in compositions:
    for node in page.iter("t"):
        key = node.get("t-snippet-call")
        if key:
            assert key.startswith("theme_facodi.")
            assert key.split(".", 1)[1] in expected
```

### Step 2: Make the i18n source-location contract compatible with split snippets

In `tests/test_i18n_contract.sh`, replace:

```bash
grep -Fq 'Learn together with the community' "$VIEWS_DIR/snippets.xml" || fail "snippet source language must be English"
```

with:

```bash
grep -Fq 'Learn together with the community' "$VIEWS_DIR/snippets/s_facodi_hero.xml" \
  || fail "hero source language must remain English"
```

Keep the existing recursive check that forbids hard-coded Portuguese copy under `theme_facodi/views`.

### Step 3: Add runtime expectations before production code exists

In `theme_facodi/tests/test_website.py`:

- expand `test_facodi_snippets_are_registered` to all nine stable keys;
- add `test_facodi_header_is_registered_as_native_theme_template`:

```python
def test_facodi_header_is_registered_as_native_theme_template(self):
    theme_view = self.env["theme.ir.ui.view"].search(
        [("key", "=", "theme_facodi.template_header_facodi")], limit=1
    )
    self.assertTrue(theme_view)
    website_view = self.env["ir.ui.view"].search(
        [
            ("key", "=", "theme_facodi.template_header_facodi"),
            ("website_id", "!=", False),
        ],
        limit=1,
    )
    self.assertTrue(website_view)
    self.assertIn("website.placeholder_header_brand", website_view.arch_db)
    self.assertIn("website.navbar_nav", website_view.arch_db)
```

Keep the existing nested/external/active-menu and authenticated-account tests; those are regression coverage for preserving standard Odoo ownership.

### Step 4: Run the fast contract and confirm RED

```bash
bash tests/test_module_contract.sh
```

Expected first failure:

```text
FAIL: missing native FACODI header file: theme_facodi/models/__init__.py
```

The i18n contract is also expected to fail until the hero is moved:

```bash
bash tests/test_i18n_contract.sh
```

Expected:

```text
FAIL: hero source language must remain English
```

### Step 5: Commit the RED contracts

```bash
git add tests/test_module_contract.sh tests/test_i18n_contract.sh theme_facodi/tests/test_website.py
git commit -m "test: define native header and split snippet contracts"
```

---

## Task 2: Implement the Odoo-native selectable FACODI header

**Files:**
- Modify: `theme_facodi/__init__.py`
- Create: `theme_facodi/models/__init__.py`
- Create: `theme_facodi/models/theme_models.py`
- Create: `theme_facodi/views/header.xml`
- Modify: `theme_facodi/views/customizations.xml`
- Create: `theme_facodi/static/src/builder/header.xml`
- Create: `theme_facodi/static/src/img/template_header_facodi.svg`
- Modify: `theme_facodi/static/src/scss/website.scss`
- Modify: `theme_facodi/__manifest__.py`

**Interfaces:**
- Consumes: `theme.utils`, `website.layout`, `website.HeaderTemplateOption`, `website.navbar_nav`, `website.template_header_mobile`, Website menus and Portal identity templates.
- Produces: selectable header key `theme_facodi.template_header_facodi`, Website value `header-template=facodi`, FACODI desktop presentation, standard Odoo mobile navigation.

### Step 1: Load the theme-utils model extension

Replace the empty `theme_facodi/__init__.py` with:

```python
from . import models
```

Create `theme_facodi/models/__init__.py`:

```python
from . import theme_models
```

Create `theme_facodi/models/theme_models.py`, mirroring the official Odoo design-themes header registration pattern:

```python
from odoo import models


class ThemeUtils(models.AbstractModel):
    _inherit = "theme.utils"

    @property
    def _header_templates(self):
        return ["theme_facodi.template_header_facodi"] + super()._header_templates

    def _theme_facodi_post_copy(self, mod):
        self.enable_view("theme_facodi.template_header_facodi")
```

### Step 2: Create the selectable desktop header using only the supported nav replacement point

Create `theme_facodi/views/header.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="template_header_facodi"
              inherit_id="website.layout"
              name="FACODI Header Template"
              active="False">
        <xpath expr="//header" position="attributes">
            <attribute name="class" add="facodi-header" separator=" "/>
        </xpath>
        <xpath expr="//header//nav" position="replace">
            <nav data-name="Navbar"
                 aria-label="Primary navigation"
                 class="navbar navbar-expand-lg">
                <div id="o_main_nav" class="container-fluid facodi-nav-shell">
                    <t t-call="website.placeholder_header_brand"
                       _link_class.f="facodi-wordmark"/>
                    <t t-call="website.navbar_nav">
                        <t t-set="_nav_class" t-valuef="ms-auto align-items-lg-center gap-lg-1"/>
                        <t t-foreach="website.menu_id.child_id" t-as="submenu">
                            <t t-call="website.submenu"
                               item_class.f="nav-item"
                               link_class.f="nav-link"
                               dropdown_menu_classes.f="facodi-dropdown-menu"/>
                        </t>
                        <t t-call="portal.placeholder_user_sign_in"
                           _item_class.f="nav-item ms-lg-2"
                           _link_class.f="btn facodi-button facodi-button-primary"/>
                        <t t-call="portal.user_dropdown"
                           _user_name="True"
                           _item_class.f="nav-item dropdown ms-lg-2"
                           _link_class.f="btn facodi-button facodi-button-primary border-0"
                           _dropdown_menu_class.f="dropdown-menu-end"/>
                    </t>
                </div>
            </nav>
        </xpath>
    </template>
</odoo>
```

This follows Odoo 19's own `theme_test_custo`: only `//header//nav` is replaced. The outer header and the standard mobile header stay Odoo-owned.

### Step 3: Remove the unconditional header replacement from `customizations.xml`

Delete the entire existing `<template id="facodi_header" ...>` block from `theme_facodi/views/customizations.xml`.

Keep unchanged:

- the `website_layout` wrapper class `facodi-site`;
- `<meta name="theme-color" content="#142846"/>`;
- the existing FACODI footer.

### Step 4: Expose FACODI in the native Website Builder header picker

Create `theme_facodi/static/src/builder/header.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="theme_facodi.headerTemplateOption"
       t-inherit="website.HeaderTemplateOption"
       t-inherit-mode="extension">
        <xpath expr="//BuilderSelect[@action=&quot;'reloadComposite'&quot;]" position="inside">
            <BuilderSelectItem
                id="'header_facodi_opt'"
                title.translate="FACODI"
                actionParam="[
                    {
                        action: 'websiteConfig',
                        actionParam: {
                            views: ['theme_facodi.template_header_facodi'],
                            vars: {
                                'header-links-style': 'default',
                                'header-template': 'facodi',
                            },
                            checkVars: false,
                        },
                    },
                ]">
                <Img src="'/theme_facodi/static/src/img/template_header_facodi.svg'"
                     class="'theme_facodi_header'"/>
            </BuilderSelectItem>
        </xpath>
    </t>
</templates>
```

### Step 5: Add a local header-picker preview

Create `theme_facodi/static/src/img/template_header_facodi.svg` as a 234×60 SVG containing only local primitives:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="234" height="60" viewBox="0 0 234 60">
  <rect width="234" height="60" fill="#F9FAFB"/>
  <path d="M0 58h234" stroke="#142846" stroke-width="2"/>
  <rect x="12" y="21" width="48" height="12" rx="2" fill="#142846"/>
  <rect x="94" y="24" width="20" height="5" rx="2" fill="#142846"/>
  <rect x="121" y="24" width="20" height="5" rx="2" fill="#142846"/>
  <rect x="148" y="24" width="20" height="5" rx="2" fill="#142846"/>
  <rect x="180" y="16" width="40" height="22" rx="4" fill="#EFFF00" stroke="#142846" stroke-width="2"/>
</svg>
```

No remote image/font request is allowed.

### Step 6: Register the header view and builder asset, and bump the theme release

Update `theme_facodi/__manifest__.py`:

```python
"version": "19.0.5.0.0",
```

Change the data list to load the header before the generic customizations:

```python
"data": [
    "data/ir_asset.xml",
    "views/header.xml",
    "views/customizations.xml",
    "views/snippets.xml",
    "views/page_templates.xml",
],
```

Add the builder bundle alongside `web.assets_frontend`:

```python
"html_builder.assets": [
    "theme_facodi/static/src/builder/**/*",
],
```

The `views/snippets.xml` path remains temporarily in this task and is replaced in Task 3.

### Step 7: Adapt header SCSS while leaving mobile HTML native

In `theme_facodi/static/src/scss/website.scss` keep the desktop `.facodi-header` styling, but remove rules that depend on the old custom `.navbar-collapse` structure. Add explicit native mobile-header styling:

```scss
.facodi-site {
    .o_header_mobile {
        background: var(--facodi-paper);
        border-bottom: 2px solid var(--facodi-ink);

        .navbar-toggler,
        .o_header_mobile_buttons_wrap .btn {
            border-color: var(--facodi-ink);
            color: var(--facodi-ink);
        }
    }
}
```

Keep `.facodi-nav-shell`, `.facodi-dropdown-menu`, focus rules and Portal button primitives. Do not create a new mobile QWeb menu.

### Step 8: Run fast contracts

```bash
bash tests/test_module_contract.sh
```

Expected: the native-header assertions pass; the first remaining failure is the missing split-snippet directory from Task 1.

Do not weaken the split-snippet assertions to make this task green.

### Step 9: Commit the native-header implementation

```bash
git add theme_facodi/__init__.py \
  theme_facodi/models \
  theme_facodi/views/header.xml \
  theme_facodi/views/customizations.xml \
  theme_facodi/static/src/builder/header.xml \
  theme_facodi/static/src/img/template_header_facodi.svg \
  theme_facodi/static/src/scss/website.scss \
  theme_facodi/__manifest__.py
git commit -m "refactor: use native selectable FACODI header"
```

---

## Task 3: Split the nine FACODI snippets into stable reusable source units

**Files:**
- Create: `theme_facodi/views/snippets/snippets.xml`
- Create: `theme_facodi/views/snippets/s_facodi_hero.xml`
- Create: `theme_facodi/views/snippets/s_facodi_learning_journey.xml`
- Create: `theme_facodi/views/snippets/s_facodi_institutional.xml`
- Create: `theme_facodi/views/snippets/s_facodi_intro.xml`
- Create: `theme_facodi/views/snippets/s_facodi_features.xml`
- Create: `theme_facodi/views/snippets/s_facodi_community.xml`
- Create: `theme_facodi/views/snippets/s_facodi_roadmap.xml`
- Create: `theme_facodi/views/snippets/s_facodi_faq.xml`
- Create: `theme_facodi/views/snippets/s_facodi_course_cta.xml`
- Delete: `theme_facodi/views/snippets.xml`
- Modify: `theme_facodi/__manifest__.py`
- Keep unchanged: `theme_facodi/views/page_templates.xml`

**Interfaces:**
- Consumes: existing stable snippet IDs and page-composition references.
- Produces: nine independently maintainable Website Builder blocks with no change to XML IDs, `data-snippet`, public routes or editor behavior.

### Step 1: Move each existing template verbatim into its own Odoo XML data file

For each existing template, create a valid standalone file with the same template ID and exact current markup/content. Example `theme_facodi/views/snippets/s_facodi_hero.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="s_facodi_hero" name="FACODI Hero">
        <!-- move the existing s_facodi_hero section here verbatim -->
    </template>
</odoo>
```

The implementation operation is a literal move, not a redesign. Apply the same rule to:

```text
s_facodi_learning_journey
s_facodi_institutional
s_facodi_intro
s_facodi_features
s_facodi_community
s_facodi_roadmap
s_facodi_faq
s_facodi_course_cta
```

The following must not change during the move:

- template IDs;
- section `data-snippet` values;
- class names;
- English source strings;
- `/slides`, `/contactus`, `/web/login` links;
- `t-translation="off"` markers.

### Step 2: Reduce the registry to registration only

Create `theme_facodi/views/snippets/snippets.xml` containing only the `website.snippets` inheritance and the FACODI group/9 registrations currently at the top of the monolithic file:

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
            <t t-snippet="theme_facodi.s_facodi_hero" string="FACODI Hero" group="facodi" t-thumbnail="/theme_facodi/static/description/theme_facodi.svg"/>
            <t t-snippet="theme_facodi.s_facodi_learning_journey" string="Learning Journey" group="facodi" t-thumbnail="/theme_facodi/static/description/theme_facodi.svg"/>
            <t t-snippet="theme_facodi.s_facodi_institutional" string="Institutional" group="facodi" t-thumbnail="/theme_facodi/static/description/theme_facodi.svg"/>
            <t t-snippet="theme_facodi.s_facodi_intro" string="Editorial intro" group="facodi" t-thumbnail="/theme_facodi/static/description/theme_facodi.svg"/>
            <t t-snippet="theme_facodi.s_facodi_features" string="Learning principles" group="facodi" t-thumbnail="/theme_facodi/static/description/theme_facodi.svg"/>
            <t t-snippet="theme_facodi.s_facodi_community" string="Community and contribution" group="facodi" t-thumbnail="/theme_facodi/static/description/theme_facodi.svg"/>
            <t t-snippet="theme_facodi.s_facodi_roadmap" string="Roadmap" group="facodi" t-thumbnail="/theme_facodi/static/description/theme_facodi.svg"/>
            <t t-snippet="theme_facodi.s_facodi_faq" string="Frequently asked questions" group="facodi" t-thumbnail="/theme_facodi/static/description/theme_facodi.svg"/>
            <t t-snippet="theme_facodi.s_facodi_course_cta" string="Course catalogue CTA" group="facodi" t-thumbnail="/theme_facodi/static/description/theme_facodi.svg"/>
        </xpath>
    </template>
</odoo>
```

### Step 3: Load definitions before registry and page compositions

Replace `"views/snippets.xml"` in the manifest with this exact ordered list:

```python
"views/snippets/s_facodi_hero.xml",
"views/snippets/s_facodi_learning_journey.xml",
"views/snippets/s_facodi_institutional.xml",
"views/snippets/s_facodi_intro.xml",
"views/snippets/s_facodi_features.xml",
"views/snippets/s_facodi_community.xml",
"views/snippets/s_facodi_roadmap.xml",
"views/snippets/s_facodi_faq.xml",
"views/snippets/s_facodi_course_cta.xml",
"views/snippets/snippets.xml",
"views/page_templates.xml",
```

Delete `theme_facodi/views/snippets.xml` after all nine definitions and the registry exist.

### Step 4: Run both source contracts and confirm GREEN

```bash
bash tests/test_module_contract.sh
bash tests/test_i18n_contract.sh
```

Expected:

```text
PASS: theme module contract
PASS: native Odoo i18n contract
```

If either fails because of changed copy, XML IDs or routes, restore the original source semantics rather than changing the test.

### Step 5: Commit the source split

```bash
git add theme_facodi/views/snippets theme_facodi/__manifest__.py tests/test_i18n_contract.sh
git add -u theme_facodi/views/snippets.xml
git commit -m "refactor: split FACODI snippets into reusable units"
```

---

## Task 4: Harden runtime, upgrade and multilingual regression coverage

**Files:**
- Modify: `theme_facodi/tests/test_website.py`
- Modify: `theme_facodi/i18n/theme_facodi.pot`
- Modify: `theme_facodi/i18n/pt.po`
- Modify: `theme_facodi/i18n/es.po`
- Modify: `theme_facodi/i18n/fr.po`
- Modify only if required by source location checks: `tests/test_i18n_contract.sh`

**Interfaces:**
- Consumes: native header view, standard Website menu/brand/Portal components, stable snippet keys, native theme-view translations.
- Produces: clean-install and upgrade regression coverage for the refactor without custom translation or menu logic.

### Step 1: Expand runtime snippet coverage to all nine blocks

Replace the three-key set in `test_facodi_snippets_are_registered` with:

```python
keys = {
    "theme_facodi.s_facodi_hero",
    "theme_facodi.s_facodi_learning_journey",
    "theme_facodi.s_facodi_institutional",
    "theme_facodi.s_facodi_intro",
    "theme_facodi.s_facodi_features",
    "theme_facodi.s_facodi_community",
    "theme_facodi.s_facodi_roadmap",
    "theme_facodi.s_facodi_faq",
    "theme_facodi.s_facodi_course_cta",
}
```

Keep representative class assertions for Hero/Journey/Institutional and add simple existence/render assertions for the remaining six.

### Step 2: Assert the selected header still renders standard brand/menu/Portal behavior

Keep `test_homepage_uses_live_facodi_shell` but make it assert the selected template rather than the old full replacement. The rendered contract remains:

```python
self.assertIn("facodi-header", response.text)
header_html = response.text.split("<header", 1)[1].split("</header>", 1)[0]
self.assertIn('data-name="Navbar Logo"', header_html)
self.assertIn("/web/image/website/", header_html)
self.assertIn("facodi-wordmark", header_html)
```

Keep `test_native_menu_preserves_nested_and_external_links` unchanged. It proves that `website.submenu` still owns dropdown recursion, active state and external-window behavior.

Keep `test_authenticated_account_has_accessible_name` unchanged. It proves the standard authenticated Portal dropdown remains present.

### Step 3: Confirm the Website-specific native header view exists after theme application

Use the RED test added in Task 1. If the website-specific copy is not created because the theme lifecycle enables the source view differently, inspect `theme.utils` behavior and correct the implementation to match Odoo's official theme lifecycle; do not remove the test merely to pass.

### Step 4: Refresh translation source references without changing translations

The visible strings `Primary navigation` and any other header strings now belong to `theme_facodi.template_header_facodi`, not `theme_facodi.facodi_header`.

In each catalogue (`theme_facodi.pot`, `pt.po`, `es.po`, `fr.po`), replace only the source reference comment:

```text
model_terms:theme.ir.ui.view,arch:theme_facodi.facodi_header
```

with:

```text
model_terms:theme.ir.ui.view,arch:theme_facodi.template_header_facodi
```

Keep every `msgid` and existing `msgstr` unchanged.

The `s_facodi_*` XML IDs are unchanged, so their catalogue keys stay unchanged despite physical file moves.

### Step 5: Run the full Odoo 19 install test locally when a Docker worktree is available

Use the same environment as CI:

```bash
bash tests/test_module_contract.sh
bash tests/test_i18n_contract.sh

docker network create facodi-theme-native-header-test || true

docker run -d --rm --name facodi-theme-native-header-db \
  --network facodi-theme-native-header-test \
  -e POSTGRES_USER=odoo \
  -e POSTGRES_PASSWORD=odoo \
  -e POSTGRES_DB=theme_facodi_native_header_ci \
  postgres:16
```

After `pg_isready`, run Odoo with the repository and the pinned `odoo/design-themes` checkout on `addons_path`, using:

```text
-i theme_facodi --test-tags /theme_facodi --stop-after-init
```

Then rerun against the same database with:

```text
-u theme_facodi --test-tags /theme_facodi --stop-after-init
```

Expected on both runs: zero failures and zero errors.

If execution is connector-only, GitHub Actions is the authoritative equivalent of these commands; do not claim a local Docker run occurred unless it actually did.

### Step 6: Push and verify GitHub Actions on the exact head

After the task commit, inspect the CI run for the exact branch head and require success for:

- Theme repository contract;
- Native Odoo i18n contract;
- pinned design-themes checkout;
- PostgreSQL startup;
- clean Odoo theme install and test suite;
- Odoo theme upgrade and test suite.

### Step 7: Commit the runtime/i18n hardening

```bash
git add theme_facodi/tests/test_website.py \
  theme_facodi/i18n/theme_facodi.pot \
  theme_facodi/i18n/pt.po \
  theme_facodi/i18n/es.po \
  theme_facodi/i18n/fr.po \
  tests/test_i18n_contract.sh
git commit -m "test: cover native header and split snippet regressions"
```

---

## Task 5: Update release documentation and validate the visual contract

**Files:**
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/validation.md`

**Interfaces:**
- Consumes: validated Odoo 19 behavior and the approved screenshot contract.
- Produces: current architecture/release documentation that no longer describes the obsolete full-header replacement.

### Step 1: Update README for release `19.0.5.0.0`

Change the release line to `19.0.5.0.0` and document that:

- FACODI is available as a native selectable header template in Website Builder;
- the header still uses Website-managed logo/menu and Portal-managed identity;
- standard Odoo mobile header behavior remains authoritative;
- nine snippets are maintained as separate reusable QWeb source units;
- no editorial `website.page` data is imported.

Do not add operational claims that have not been verified by CI/runtime testing.

### Step 2: Replace the obsolete architecture text about full header replacement

In `docs/architecture.md`, replace the current statement that the theme “replaces the standard header” with this architecture:

```text
website.layout
├── Odoo-owned outer header and mobile header
└── theme_facodi.template_header_facodi (selectable desktop nav template)
    ├── website.placeholder_header_brand
    ├── website.navbar_nav / website.submenu
    ├── portal.placeholder_user_sign_in
    └── portal.user_dropdown
```

Document the three official Odoo integration points used:

1. `theme.utils._header_templates` registers the header view;
2. `_theme_facodi_post_copy()` enables it when the theme is copied/applied;
3. `html_builder.assets` extends `website.HeaderTemplateOption` with `header-template=facodi`.

Document that responsive mobile navigation remains `website.template_header_mobile` and receives only FACODI SCSS styling.

Update the source-ownership table so:

- `views/header.xml` owns selectable desktop nav composition;
- `views/customizations.xml` owns shell/meta/footer only;
- `views/snippets/snippets.xml` owns the Builder registry;
- `views/snippets/s_facodi_*.xml` own individual blocks.

### Step 3: Record validation evidence

Append a new section to `docs/validation.md` titled:

```markdown
## Native header and reusable snippets — 2026-09-05
```

Record only observed evidence:

- exact validated branch/head SHA;
- fast contract results;
- clean install result;
- upgrade result;
- all 9 snippet keys found;
- 10 page compositions still render;
- nested/external/active menu regression result;
- configured Website logo regression result;
- authenticated Portal dropdown result;
- multilingual route and snippet translation result;
- `/slides`, `/contactus`, `/web/login` result;
- compiled frontend assets result.

For visual equivalence, inspect the rendered staging/disposable page at desktop and mobile widths against the approved reference. Record whether these contract points match:

```text
Paper header background
Ink bottom border
configured logo left
menu right on desktop
Sun/lime account action
FACODI border/shadow language
native mobile navigation
```

If browser screenshot tooling is unavailable in the execution environment, explicitly record that automated markup/CSS checks passed and leave visual screenshot approval as the remaining human staging check; do not fabricate screenshot evidence.

### Step 4: Run doc/source contract again

```bash
bash tests/test_module_contract.sh
bash tests/test_i18n_contract.sh
```

Expected: both PASS.

### Step 5: Commit documentation

```bash
git add README.md docs/architecture.md docs/validation.md
git commit -m "docs: document native FACODI header architecture"
```

---

## Task 6: Final theme verification, review, PR, then pin the exact green commit in `facodi-deploy`

**Files — `facodi-theme`:**
- No planned production-code changes; review/verification only.

**Files — `facodi-deploy`:**
- Modify gitlink: `addons/facodi-theme`
- Modify: `tests/test_repository_contract.py`

**Interfaces:**
- Consumes: exact green `facodi-theme` commit SHA.
- Produces: two reviewable PRs: one theme PR and one deploy-composition PR; no automatic production deployment.

### Step 1: Verify the final theme branch before opening the PR

Run/inspect all of:

```bash
bash tests/test_module_contract.sh
bash tests/test_i18n_contract.sh
git diff --check
git status --short
git rev-parse HEAD
```

Use the resulting head dynamically:

```bash
THEME_SHA="$(git rev-parse HEAD)"
printf '%s\n' "$THEME_SHA"
```

Require a completed successful GitHub Actions run whose `head_sha` equals `$THEME_SHA`.

Use `superpowers:requesting-code-review` and resolve substantive findings before marking the PR ready.

### Step 2: Open the `facodi-theme` PR

Open a PR from:

```text
feat/native-header-reusable-snippets
```

to:

```text
main
```

The PR summary must state:

- no complete `<header>` replacement remains;
- header uses Odoo's selectable `HeaderTemplateOption` mechanism;
- standard logo/menu/Portal ownership preserved;
- native mobile header preserved;
- 9 snippet IDs preserved and split into reusable source files;
- 10 page compositions unchanged in contract;
- clean install + upgrade + i18n + eLearning regression results;
- production deployment not performed.

Do **not** merge without explicit user instruction.

### Step 3: Create an integration branch in `facodi-deploy` only after the theme SHA is green

From current `facodi-deploy/main`, create:

```text
integration/native-header-reusable-snippets
```

Do not copy theme source files.

Advance `addons/facodi-theme` to the exact `$THEME_SHA` using the gitlink/submodule mechanism.

### Step 4: Update the exact deployment pin test

In `facodi-deploy/tests/test_repository_contract.py`, change only the FACODI theme entry in `EXPECTED_SUBMODULES` from the old SHA to the exact `$THEME_SHA`:

```python
"addons/facodi-theme": THEME_SHA_FROM_GITLINK,
```

In the actual Python file, write the literal 40-character SHA obtained from `git rev-parse HEAD`; do not introduce a Python variable or floating branch reference.

No other addon pin changes belong in this PR.

### Step 5: Run the deploy repository verification

With recursive submodules checked out at the new pins:

```bash
python3 -m unittest tests.test_repository_contract
bash scripts/validate-repository.sh
docker compose --env-file .env.ci -f deploy/coolify/docker-compose.yml config --quiet
bash tests/test_coolify_runtime.sh
```

If execution is connector-only, require the equivalent `facodi-deploy` GitHub Actions run to finish successfully on the exact integration-branch head before claiming the integration is ready.

Expected deploy CI stages:

```text
Validate repository contract        success
Validate Coolify Compose            success
Exercise fresh migration, idempotent migration and Odoo HTTP   success
```

### Step 6: Open a separate `facodi-deploy` PR

PR scope must be limited to:

- `addons/facodi-theme` gitlink → exact green theme SHA;
- `tests/test_repository_contract.py` exact expected SHA.

The PR body must identify the corresponding `facodi-theme` PR and exact tested theme commit.

Do **not** merge or trigger a production redeploy without explicit user instruction.

---

## Final Acceptance Checklist

Before declaring this implementation complete, verify every item against the approved spec:

- [ ] No `xpath expr="//header" position="replace"` exists in `theme_facodi`.
- [ ] `theme_facodi.template_header_facodi` is registered through `theme.utils._header_templates`.
- [ ] Website Builder exposes a FACODI header option through `website.HeaderTemplateOption`.
- [ ] Header selection sets `header-template=facodi`.
- [ ] Header still uses standard Website brand/logo output.
- [ ] Header still renders dynamic standard Website menus and nested/external/active behavior.
- [ ] Anonymous sign-in and authenticated user dropdown remain standard Portal templates.
- [ ] Mobile navigation remains Odoo-native (`website.template_header_mobile`), with presentation only styled by FACODI SCSS.
- [ ] Public desktop header remains visually equivalent to the approved screenshot contract.
- [ ] All 9 FACODI snippets have one stable source template each and are registered exactly once.
- [ ] All 10 page compositions continue to reference the same `theme_facodi.s_facodi_*` IDs.
- [ ] No editorial Website pages are imported by the theme.
- [ ] No business models/controllers/ORM queries are introduced.
- [ ] English source + `pt_PT` + `es_ES` + `fr_FR` remain native Odoo translations.
- [ ] `/`, `/slides`, `/contactus`, `/web/login` and authenticated account behavior remain healthy.
- [ ] Frontend assets compile without Sass errors.
- [ ] Clean Odoo 19 theme installation passes.
- [ ] Odoo 19 theme upgrade passes.
- [ ] `facodi-theme` CI is green on the exact final SHA.
- [ ] `facodi-deploy` pins that exact SHA and no theme presentation code is duplicated there.
- [ ] `facodi-deploy` Coolify runtime CI is green on the exact integration SHA.
- [ ] No production deployment or merge occurred without explicit user instruction.
