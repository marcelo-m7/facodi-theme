# FACODI Native Header and Reusable Snippets Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Apply TDD to behavioral changes and use `superpowers:verification-before-completion` before any completion claim.

**Goal:** Preserve the approved FACODI navigation appearance while replacing the unconditional whole-header override with Odoo 19's supported selectable header-template mechanism, and persist the nine existing FACODI Website Builder blocks as independently maintainable reusable QWeb units without changing their public XML IDs, translations, page-composition contracts, or eLearning ownership.

**Architecture:** `theme_facodi` remains presentation-only. A FACODI header view is registered through `theme.utils._header_templates`, enabled by the theme post-copy hook, and exposed in the native `website.HeaderTemplateOption` picker through `html_builder.assets`. The view follows Odoo 19's own `theme_test_custo` pattern and replaces only `//header//nav`; Odoo retains the outer header, configured logo, menu records, submenu recursion, Portal identity, mobile header and editor controls. The nine `s_facodi_*` templates retain their stable XML IDs but move from one monolithic file to one file per block plus a registry file. `facodi-deploy` remains composition-only and advances its exact theme gitlink only after theme CI is green.

**Tech Stack:** Odoo 19 Community, `theme_common`, `website_slides`, `theme.utils`, Website Builder / `html_builder.assets`, QWeb/XML, SCSS/Bootstrap, Python `odoo.tests.HttpCase`, Odoo native PO/POT i18n, Bash contract tests, PostgreSQL 16, Docker, GitHub Actions, Git submodules, Coolify runtime validation.

**Spec:** `docs/superpowers/specs/2026-09-05-native-header-reusable-snippets-design.md`

## Global Constraints

- Work on `marcelo-m7/facodi-theme` branch `feat/native-header-reusable-snippets`; never implement directly on `main`.
- Target **Odoo 19 Community** only.
- Keep dependencies exactly `theme_common` and `website_slides`.
- Preserve the approved FACODI palette: Ink `#142846`, Cyan `#37BED2`, Blue `#3979C8`, Mint `#A7E8BE`, Sun `#EFFF00`, Paper `#F9FAFB`.
- Preserve the approved public header contract: configurable logo left, dynamic Website menu right on desktop, lime Portal/user action, Paper background, Ink separator, FACODI geometry and focus behavior.
- Do not style Odoo backend/editor chrome.
- Website owns logo, menus, pages and editor state. Portal owns identity navigation. `website_slides` owns catalogue/course/lesson/progress behavior.
- No `request.env`, `sudo()`, ORM search in QWeb, custom course catalogue, controller, parallel authentication, parallel mobile menu, forced logo/favicon, or business-addon dependency.
- Do not use `xpath expr="//header" position="replace"` anywhere in the theme.
- Keep all nine `s_facodi_*` XML IDs unchanged.
- Keep all ten current New Page compositions and their `t-snippet-call` contracts unchanged.
- Keep English as source language and `pt_PT`, `es_ES`, `fr_FR` through standard Odoo i18n.
- Keep `odoo/design-themes` pinned at `a1818df4ade65406c0cacae8b1ea676e6f70095f` for this cycle.
- Do not copy theme QWeb or SCSS into `facodi-deploy`.
- Do not merge PRs or trigger production deployment without explicit user instruction.

---

## Task 1: Establish RED contracts for the native header and split snippets

**Files:**
- Modify: `tests/test_module_contract.sh`
- Modify: `tests/test_i18n_contract.sh`
- Modify: `theme_facodi/tests/test_website.py`

**Interfaces:**
- Consumes: current monolithic source and existing Odoo 19 CI.
- Produces: failing tests that define the supported header extension points and new source boundaries before implementation.

### Step 1: Add native-header file and ownership assertions

In `tests/test_module_contract.sh`, replace the old assumptions that require `facodi-header` and all menu calls inside `views/customizations.xml` with:

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
  || fail "theme root must load models"
grep -Fq 'from . import theme_models' theme_facodi/models/__init__.py \
  || fail "theme models package must load theme_models"
grep -Fq '_inherit = "theme.utils"' theme_facodi/models/theme_models.py \
  || fail "theme.utils extension missing"
grep -Fq 'theme_facodi.template_header_facodi' theme_facodi/models/theme_models.py \
  || fail "FACODI header must be registered by theme.utils"
grep -Fq '_theme_facodi_post_copy' theme_facodi/models/theme_models.py \
  || fail "FACODI theme post-copy hook missing"

grep -Fq 'views/header.xml' theme_facodi/__manifest__.py \
  || fail "header view missing from manifest"
grep -Fq 'html_builder.assets' theme_facodi/__manifest__.py \
  || fail "Website Builder asset bundle missing"
grep -Fq 'theme_facodi/static/src/builder/**/*' theme_facodi/__manifest__.py \
  || fail "FACODI builder assets missing"

if grep -R -n '<xpath[^>]*expr="//header"[^>]*position="replace"' theme_facodi --include='*.xml'; then
  fail "theme must not replace the complete Odoo header"
fi

grep -Fq 'id="template_header_facodi"' theme_facodi/views/header.xml \
  || fail "FACODI header template missing"
grep -Fq 'xpath expr="//header//nav" position="replace"' theme_facodi/views/header.xml \
  || fail "FACODI header must replace only the standard nav extension point"
grep -Fq 'website.placeholder_header_brand' theme_facodi/views/header.xml \
  || fail "standard configurable Website brand missing"
grep -Fq 'website.navbar_nav' theme_facodi/views/header.xml \
  || fail "standard navbar wrapper missing"
grep -Fq 'website.menu_id.child_id' theme_facodi/views/header.xml \
  || fail "dynamic Website menus missing"
grep -Fq 't-call="website.submenu"' theme_facodi/views/header.xml \
  || fail "native submenu recursion missing"
grep -Fq 'portal.placeholder_user_sign_in' theme_facodi/views/header.xml \
  || fail "standard Portal sign-in missing"
grep -Fq 'portal.user_dropdown' theme_facodi/views/header.xml \
  || fail "standard Portal user dropdown missing"

grep -Fq 't-inherit="website.HeaderTemplateOption"' theme_facodi/static/src/builder/header.xml \
  || fail "FACODI must extend the native header template picker"
grep -Fq "'header-template': 'facodi'" theme_facodi/static/src/builder/header.xml \
  || fail "FACODI picker must set header-template=facodi"
grep -Fq "views: ['theme_facodi.template_header_facodi']" theme_facodi/static/src/builder/header.xml \
  || fail "FACODI picker must activate its header view"
```

### Step 2: Add exact split-snippet assertions

Still in `tests/test_module_contract.sh`, add:

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
[[ ! -f theme_facodi/views/snippets.xml ]] \
  || fail "legacy monolithic snippets.xml must be removed"

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
```

Replace the current XML parser block so it discovers templates across the split directory:

```python
from pathlib import Path
from xml.etree import ElementTree as ET

snippet_dir = Path("theme_facodi/views/snippets")
blocks = set()
for path in snippet_dir.glob("s_facodi_*.xml"):
    root = ET.parse(path).getroot()
    for node in root.findall("template"):
        snippet_id = node.get("id", "")
        if snippet_id.startswith("s_facodi_"):
            blocks.add(snippet_id)

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

### Step 3: Point the source-language contract at the future Hero file

In `tests/test_i18n_contract.sh`, replace:

```bash
grep -Fq 'Learn together with the community' "$VIEWS_DIR/snippets.xml" || fail "snippet source language must be English"
```

with:

```bash
grep -Fq 'Learn together with the community' "$VIEWS_DIR/snippets/s_facodi_hero.xml" \
  || fail "hero source language must remain English"
```

Keep all existing rules against hard-coded Portuguese branches and custom language selection.

### Step 4: Add runtime registration coverage

In `theme_facodi/tests/test_website.py`, expand `test_facodi_snippets_are_registered` to these nine keys:

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

Add:

```python
def test_facodi_header_is_registered_as_native_theme_template(self):
    theme_view = self.env["theme.ir.ui.view"].search(
        [("key", "=", "theme_facodi.template_header_facodi")], limit=1
    )
    self.assertTrue(theme_view)
    website_view = self.env["ir.ui.view"].search(
        [
            ("key", "=", "theme_facodi.template_header_facodi"),
            ("website_id", "=", self.website.id),
        ],
        limit=1,
    )
    self.assertTrue(website_view)
    self.assertIn("website.placeholder_header_brand", website_view.arch_db)
    self.assertIn("website.navbar_nav", website_view.arch_db)
```

Keep the existing nested/external/active menu and authenticated account tests unchanged.

### Step 5: Confirm RED

Run:

```bash
bash tests/test_module_contract.sh
bash tests/test_i18n_contract.sh
```

Expected first failures are missing native-header files and missing split Hero source. Do not proceed if the new tests unexpectedly pass against the old implementation.

### Step 6: Commit RED tests

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
- Consumes: `theme.utils`, `website.layout`, `website.HeaderTemplateOption`, `website.navbar_nav`, Website menus, Portal identity and the standard Odoo mobile header.
- Produces: header view key `theme_facodi.template_header_facodi` and builder value `header-template=facodi`.

### Step 1: Load the theme-utils extension

Replace the empty root init with:

```python
from . import models
```

Create `theme_facodi/models/__init__.py`:

```python
from . import theme_models
```

Create `theme_facodi/models/theme_models.py` following Odoo 19 `theme_test_custo`:

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

### Step 2: Create the selectable header and replace only `//header//nav`

Create `theme_facodi/views/header.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="template_header_facodi"
              inherit_id="website.layout"
              name="FACODI Header Template">
        <xpath expr="//header" position="attributes">
            <attribute name="class" add="facodi-header" separator=" "/>
        </xpath>
        <xpath expr="//header//nav" position="replace">
            <nav data-name="Navbar"
                 aria-label="Primary navigation"
                 class="navbar navbar-expand-lg">
                <div id="o_main_nav" class="container-fluid facodi-nav-shell">
                    <t t-call="website.placeholder_header_brand">
                        <t t-set="_link_class" t-valuef="facodi-wordmark"/>
                    </t>
                    <t t-call="website.navbar_nav">
                        <t t-set="_nav_class" t-valuef="ms-auto align-items-lg-center gap-lg-1"/>
                        <t t-foreach="website.menu_id.child_id" t-as="submenu">
                            <t t-call="website.submenu">
                                <t t-set="item_class" t-valuef="nav-item"/>
                                <t t-set="link_class" t-valuef="nav-link"/>
                                <t t-set="dropdown_menu_classes" t-valuef="facodi-dropdown-menu"/>
                            </t>
                        </t>
                        <t t-call="portal.placeholder_user_sign_in">
                            <t t-set="_item_class" t-valuef="nav-item ms-lg-2"/>
                            <t t-set="_link_class" t-valuef="btn facodi-button facodi-button-primary"/>
                        </t>
                        <t t-call="portal.user_dropdown">
                            <t t-set="_user_name" t-value="true"/>
                            <t t-set="_item_class" t-valuef="nav-item dropdown ms-lg-2"/>
                            <t t-set="_link_class" t-valuef="btn facodi-button facodi-button-primary border-0"/>
                            <t t-set="_dropdown_menu_class" t-valuef="dropdown-menu-end"/>
                        </t>
                    </t>
                </div>
            </nav>
        </xpath>
    </template>
</odoo>
```

This intentionally matches the official Odoo 19 design-theme pattern: the template inherits `website.layout` but replaces only its header navigation node.

### Step 3: Remove the old unconditional header template

Delete only the `<template id="facodi_header" ...>` block from `theme_facodi/views/customizations.xml`.

Preserve unchanged:

- `website_layout` adding `facodi-site`;
- the `#142846` theme-color meta;
- the existing FACODI footer.

### Step 4: Add the native Website Builder option

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

### Step 5: Add a local header preview icon

Create `theme_facodi/static/src/img/template_header_facodi.svg` exactly as:

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

### Step 6: Register the header view and builder assets

Update `theme_facodi/__manifest__.py`:

```python
"version": "19.0.5.0.0",
```

Load `views/header.xml` immediately before `views/customizations.xml`.

Add:

```python
"html_builder.assets": [
    "theme_facodi/static/src/builder/**/*",
],
```

Leave the existing `web.assets_frontend` list intact.

### Step 7: Style the standard mobile header instead of creating another menu

In `theme_facodi/static/src/scss/website.scss`:

- keep `.facodi-header`, `.facodi-nav-shell`, `.facodi-dropdown-menu`, footer and focus styles;
- remove old CSS that assumes the custom desktop `navbar-collapse` is also the mobile navigation implementation;
- add presentation-only rules for Odoo's native mobile header:

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

Do not add a FACODI-specific mobile QWeb menu.

### Step 8: Run the fast contract

```bash
bash tests/test_module_contract.sh
```

Expected: native-header checks now pass; execution still stops on the intentionally unmet split-snippet contract until Task 3.

### Step 9: Commit

```bash
git add theme_facodi/__init__.py theme_facodi/models theme_facodi/views/header.xml \
  theme_facodi/views/customizations.xml theme_facodi/static/src/builder/header.xml \
  theme_facodi/static/src/img/template_header_facodi.svg \
  theme_facodi/static/src/scss/website.scss theme_facodi/__manifest__.py
git commit -m "refactor: use native selectable FACODI header"
```

---

## Task 3: Split all nine FACODI snippets into reusable source units

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
- Consumes: the nine existing `<template id="s_facodi_*">` subtrees from `views/snippets.xml`.
- Produces: the exact same nine QWeb identities, each in one focused file, plus a Builder registry file.

### Step 1: Move each existing template subtree without changing its public content

Use this exact source-to-target mapping:

```text
views/snippets.xml::s_facodi_hero             -> views/snippets/s_facodi_hero.xml
views/snippets.xml::s_facodi_learning_journey -> views/snippets/s_facodi_learning_journey.xml
views/snippets.xml::s_facodi_institutional    -> views/snippets/s_facodi_institutional.xml
views/snippets.xml::s_facodi_intro            -> views/snippets/s_facodi_intro.xml
views/snippets.xml::s_facodi_features         -> views/snippets/s_facodi_features.xml
views/snippets.xml::s_facodi_community        -> views/snippets/s_facodi_community.xml
views/snippets.xml::s_facodi_roadmap          -> views/snippets/s_facodi_roadmap.xml
views/snippets.xml::s_facodi_faq              -> views/snippets/s_facodi_faq.xml
views/snippets.xml::s_facodi_course_cta       -> views/snippets/s_facodi_course_cta.xml
```

Each target file has the standard envelope:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    [the complete existing template subtree for that exact XML ID]
</odoo>
```

The bracketed phrase above is an execution instruction, not new markup: copy the existing subtree from the current repository source without editing it. Verify the resulting diff is a pure move of template content. Specifically preserve template IDs, `data-snippet`, class names, English copy, routes and `t-translation="off"` markers.

### Step 2: Create a registry-only file

Create `theme_facodi/views/snippets/snippets.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="snippets" inherit_id="website.snippets" name="FACODI snippets">
        <xpath expr="//t[@id='installed_snippets_hook']" position="after">
            <t snippet-group="facodi" t-snippet="website.s_snippet_group" string="FACODI" t-thumbnail="/theme_facodi/static/description/theme_facodi.svg"/>
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

Replace `"views/snippets.xml"` in the manifest with this order:

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

Delete the old `theme_facodi/views/snippets.xml` only after all ten new files exist.

### Step 4: Confirm GREEN source contracts

```bash
bash tests/test_module_contract.sh
bash tests/test_i18n_contract.sh
```

Expected:

```text
PASS: theme module contract
PASS: native Odoo i18n contract
```

If moving content changes a string, route, XML ID or class, restore the original source instead of weakening the contract.

### Step 5: Commit

```bash
git add theme_facodi/views/snippets theme_facodi/__manifest__.py tests/test_i18n_contract.sh
git add -u theme_facodi/views/snippets.xml
git commit -m "refactor: split FACODI snippets into reusable units"
```

---

## Task 4: Harden runtime, upgrade and multilingual regressions

**Files:**
- Modify: `theme_facodi/tests/test_website.py`
- Modify: `theme_facodi/i18n/theme_facodi.pot`
- Modify: `theme_facodi/i18n/pt.po`
- Modify: `theme_facodi/i18n/es.po`
- Modify: `theme_facodi/i18n/fr.po`

**Interfaces:**
- Consumes: native theme header, standard Website/Portal behavior, split snippet sources and current native translations.
- Produces: install/upgrade/runtime proof without a parallel translation or navigation stack.

### Step 1: Keep rendered-shell assertions tied to public behavior

In `test_homepage_uses_live_facodi_shell`, keep/adjust assertions so the rendered page proves:

```python
self.assertIn("facodi-site", response.text)
self.assertIn("facodi-header", response.text)
header_html = response.text.split("<header", 1)[1].split("</header>", 1)[0]
self.assertIn('data-name="Navbar Logo"', header_html)
self.assertIn("/web/image/website/", header_html)
self.assertIn("facodi-wordmark", header_html)
```

Keep the existing favicon regression. Keep the nested/external/active menu test. Keep the authenticated account accessible-name test.

### Step 2: Keep all nine snippet views and all ten compositions exercised

The expanded nine-key test from Task 1 stays in place. The existing page-template test must still:

- find exactly ten `new_page_template_sections_facodi_*` views;
- render each composition;
- preserve editor-owned content after theme reload/upgrade.

Do not add `website.page` XML records.

### Step 3: Refresh only header translation source references

In `theme_facodi.pot`, `pt.po`, `es.po`, and `fr.po`, replace source-reference comments:

```text
model_terms:theme.ir.ui.view,arch:theme_facodi.facodi_header
```

with:

```text
model_terms:theme.ir.ui.view,arch:theme_facodi.template_header_facodi
```

Do not change the existing `msgid` or `msgstr` values. The `s_facodi_*` IDs remain stable, so their translation keys do not change when files move.

### Step 4: Run clean-install and upgrade tests

Use the existing repository CI commands/environment. Locally, when a Docker worktree is available:

```bash
bash tests/test_module_contract.sh
bash tests/test_i18n_contract.sh
```

Then run Odoo 19 with the repository plus pinned design-themes on `addons_path`:

```text
-d theme_facodi_ci -i theme_facodi --workers=0 --without-demo=True --test-tags /theme_facodi --stop-after-init
```

and against the same database:

```text
-d theme_facodi_ci -u theme_facodi --workers=0 --without-demo=True --test-tags /theme_facodi --stop-after-init
```

Expected: zero failures and zero errors in both runs.

If execution is connector-only, GitHub Actions is the authoritative equivalent; do not claim a local Docker run occurred unless it actually did.

### Step 5: Require green CI on the exact head

Inspect the GitHub Actions run whose `head_sha` equals the current branch head. Require success for:

- Theme repository contract;
- Native Odoo i18n contract;
- pinned design-themes checkout;
- PostgreSQL startup;
- clean Odoo install/test;
- Odoo upgrade/test.

### Step 6: Commit

```bash
git add theme_facodi/tests/test_website.py theme_facodi/i18n
git commit -m "test: cover native header and split snippet regressions"
```

---

## Task 5: Update release/architecture docs and validate the approved visual contract

**Files:**
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/validation.md`

**Interfaces:**
- Consumes: observed runtime/CI evidence and approved screenshot contract.
- Produces: accurate release documentation for `19.0.5.0.0`.

### Step 1: Update README

Document release `19.0.5.0.0` and state that:

- FACODI is a native selectable Website header template;
- Website owns configured logo and menu records;
- Portal owns anonymous/authenticated identity controls;
- Odoo's standard mobile header remains authoritative;
- nine snippets are maintained as separate reusable QWeb units;
- ten New Page compositions reuse those IDs;
- the theme imports no editorial `website.page` records.

### Step 2: Correct the architecture document

Replace the obsolete “full header replacement” description with:

```text
website.layout
├── Odoo-owned outer header and standard mobile header
└── theme_facodi.template_header_facodi
    ├── website.placeholder_header_brand
    ├── website.navbar_nav / website.submenu
    ├── portal.placeholder_user_sign_in
    └── portal.user_dropdown
```

Document the three native integration points:

1. `theme.utils._header_templates` registers the custom header;
2. `_theme_facodi_post_copy()` enables it during theme lifecycle;
3. `html_builder.assets` extends `website.HeaderTemplateOption` and sets `header-template=facodi`.

Update source ownership:

```text
views/header.xml                         selectable desktop nav composition
views/customizations.xml                 shell/meta/footer only
views/snippets/snippets.xml              Builder registry only
views/snippets/s_facodi_*.xml            individual reusable blocks
static/src/builder/header.xml             Website Builder header picker extension
```

### Step 3: Append observed validation evidence

Add `## Native header and reusable snippets — 2026-09-05` to `docs/validation.md` and record only evidence actually obtained:

- exact validated branch SHA;
- fast contracts;
- clean install;
- upgrade;
- 9 snippet views;
- 10 page compositions;
- dynamic nested/external/active menus;
- configured Website logo;
- Portal dropdown;
- multilingual routes/snippets;
- `/slides`, `/contactus`, `/web/login`;
- compiled frontend assets.

For visual validation, compare desktop and mobile staging/disposable rendering to these approved reference points:

```text
Paper header background
Ink bottom separator
configured logo left
dynamic menu right on desktop
Sun/lime account action
FACODI border/shadow language
Odoo-native mobile navigation
```

If the execution environment cannot capture/render a browser screenshot, record that automated markup/CSS behavior passed and explicitly leave screenshot equivalence as a human staging check. Never invent screenshot evidence.

### Step 4: Re-run source contracts and commit

```bash
bash tests/test_module_contract.sh
bash tests/test_i18n_contract.sh
git add README.md docs/architecture.md docs/validation.md
git commit -m "docs: document native FACODI header architecture"
```

---

## Task 6: Final theme verification and review PR

**Files:** no planned production changes; verification/review only.

**Interfaces:**
- Consumes: final `facodi-theme` branch head.
- Produces: reviewable theme PR with exact green evidence.

### Step 1: Run final verification

```bash
bash tests/test_module_contract.sh
bash tests/test_i18n_contract.sh
git diff --check
git status --short
git rev-parse HEAD
```

Capture the immutable head:

```bash
THEME_SHA="$(git rev-parse HEAD)"
printf '%s\n' "$THEME_SHA"
```

Require a completed successful GitHub Actions run whose `head_sha` equals `$THEME_SHA`.

### Step 2: Request code review

Invoke `superpowers:requesting-code-review`. Resolve substantive findings and re-run verification after every code change. Use `superpowers:verification-before-completion` before declaring the branch ready.

### Step 3: Open the theme PR

Open from `feat/native-header-reusable-snippets` to `main`. PR body must state:

- whole-header replacement removed;
- native selectable header mechanism used;
- standard logo/menu/Portal/mobile ownership preserved;
- all 9 snippet IDs preserved and split;
- all 10 page compositions preserved;
- install, upgrade, i18n and eLearning regression results;
- exact tested `$THEME_SHA`;
- production deployment not performed.

Do not merge without explicit user instruction.

---

## Task 7: Pin the exact green theme commit in `facodi-deploy`

**Repository:** `marcelo-m7/facodi-deploy`

**Files:**
- Modify gitlink: `addons/facodi-theme`
- Modify: `tests/test_repository_contract.py`

**Interfaces:**
- Consumes: exact green `THEME_SHA` from Task 6.
- Produces: isolated deployment-composition PR, without copied presentation source.

### Step 1: Create the deploy integration branch

From current `facodi-deploy/main`, create:

```text
integration/native-header-reusable-snippets
```

No theme HTML, XML or SCSS belongs in this repository.

### Step 2: Advance only the theme gitlink

In a git worktree execution, run:

```bash
git -C addons/facodi-theme fetch origin "$THEME_SHA"
git -C addons/facodi-theme checkout "$THEME_SHA"
git add addons/facodi-theme
```

In connector execution, create/update the gitlink entry to the same 40-character `$THEME_SHA`; do not point to a branch name.

### Step 3: Update the exact-pin test with the same literal SHA

In `tests/test_repository_contract.py`, change only the value for:

```python
"addons/facodi-theme"
```

to the literal 40-character value produced by Task 6's `git rev-parse HEAD`.

Verify the source test and actual gitlink agree:

```bash
python3 -m unittest tests.test_repository_contract
```

### Step 4: Run deploy validation

```bash
bash scripts/validate-repository.sh
docker compose --env-file .env.ci -f deploy/coolify/docker-compose.yml config --quiet
bash tests/test_coolify_runtime.sh
```

If execution is connector-only, require the equivalent GitHub Actions run on the exact integration head. Expected CI stages:

```text
Validate repository contract                                  success
Validate Coolify Compose                                      success
Exercise fresh migration, idempotent migration and Odoo HTTP success
```

### Step 5: Open a separate deploy PR

The PR diff must be limited to:

```text
addons/facodi-theme               gitlink -> exact green theme SHA
tests/test_repository_contract.py matching expected SHA
```

Reference the corresponding theme PR and exact tested commit. Do not merge or redeploy production without explicit user instruction.

---

## Final Acceptance Checklist

- [ ] No complete core-header replacement remains.
- [ ] `theme_facodi.template_header_facodi` is registered by `theme.utils`.
- [ ] Website Builder exposes the FACODI header in `website.HeaderTemplateOption`.
- [ ] Header selection sets `header-template=facodi`.
- [ ] Configured Website logo remains authoritative.
- [ ] Dynamic menu, nested menu, active state and external-target behavior remain standard Odoo behavior.
- [ ] Anonymous sign-in and authenticated user dropdown remain standard Portal templates.
- [ ] Mobile navigation remains Odoo-native and receives presentation-only FACODI styling.
- [ ] Desktop public header remains visually equivalent to the approved screenshot contract.
- [ ] All 9 FACODI blocks are independently registered and defined exactly once.
- [ ] All 10 page compositions continue to use stable `theme_facodi.s_facodi_*` calls.
- [ ] No `website.page` editorial dump is added.
- [ ] No business model/controller/QWeb ORM access is added.
- [ ] English source and `pt_PT`/`es_ES`/`fr_FR` remain native Odoo translations.
- [ ] `/`, `/slides`, `/contactus`, `/web/login` and authenticated account behavior remain healthy.
- [ ] Frontend assets compile without Sass errors.
- [ ] Clean Odoo 19 install passes.
- [ ] Odoo 19 upgrade passes.
- [ ] `facodi-theme` CI is green on the exact final SHA.
- [ ] `facodi-deploy` pins that exact SHA only.
- [ ] `facodi-deploy` Coolify runtime CI is green on the exact integration SHA.
- [ ] No merge or production deployment occurred without explicit user instruction.
