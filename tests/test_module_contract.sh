#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

[[ -f theme_facodi/__manifest__.py ]] || fail "theme_facodi manifest missing"
[[ ! -e website_facodi ]] || fail "legacy website_facodi addon must not remain installable"
[[ -f theme_facodi/data/ir_asset.xml ]] || fail "theme primary asset record missing"
[[ ! -d theme_facodi/controllers ]] || fail "presentation theme must not add parallel learning routes/controllers"

grep -Fq '"theme_common"' theme_facodi/__manifest__.py || fail "theme_common dependency missing"
grep -Fq '"website_slides"' theme_facodi/__manifest__.py || fail "website_slides dependency missing"
grep -Fq 'Theme/Education' theme_facodi/__manifest__.py || fail "theme category must be Theme/Education"
grep -Fq 'theme_facodi.primary_variables_scss' theme_facodi/data/ir_asset.xml || fail "primary variables asset key missing"
grep -Fq 'web._assets_primary_variables' theme_facodi/data/ir_asset.xml || fail "primary variables bundle missing"

if grep -R -nE 'request\.env|sudo\(\)|href="/theme_facodi/static/src/img/favicon\.svg"|/web/content/431' theme_facodi --include='*.xml'; then
  fail "theme QWeb contains business-data access, a database asset id, or a forced favicon"
fi

# Website Builder color combinations own semantic heading colors. A global
# #wrapwrap heading override would make headings unreadable on dark combinations.
if grep -Eq '^[[:space:]]*#wrapwrap[[:space:]]+h[1-6]' theme_facodi/static/src/scss/website.scss \
   || grep -Fq 'color: $headings-color' theme_facodi/static/src/scss/website.scss; then
  fail "website.scss must not override Website Builder heading colors globally"
fi

# Default configurator snippets must not ship links to project pages that a clean
# Website install does not create. /contactus and /slides are standard routes here.
if grep -Fq 'href="/sobre"' theme_facodi/views/snippets.xml; then
  fail "default snippets must not link to undefined /sobre"
fi
grep -Fq 'href="/contactus"' theme_facodi/views/snippets.xml || fail "FACODI informational CTA must use the standard contact page"

grep -Fq 'a1818df4ade65406c0cacae8b1ea676e6f70095f' .github/workflows/ci.yml || fail "CI must pin design-themes"
grep -Fq '/mnt/design-themes' .github/workflows/ci.yml || fail "CI must mount design-themes"
grep -Fq -- '-i theme_facodi' .github/workflows/ci.yml || fail "CI must install theme_facodi"
grep -Fq -- '--test-tags /theme_facodi' .github/workflows/ci.yml || fail "CI must run theme_facodi tests"

for file in primary_variables bootstrap_overridden components website snippets website_slides; do
  [[ -f "theme_facodi/static/src/scss/${file}.scss" ]] || fail "missing ${file}.scss"
done

for color in '#142846' '#37BED2' '#3979C8' '#A7E8BE' '#EFFF00' '#F9FAFB'; do
  grep -Riq "$color" theme_facodi || fail "live FACODI color missing: $color"
done

if grep -RiqE '#6a4bff|#5dc7ff|#f7f6ff|#1f1e42|#111035' theme_facodi --exclude-dir=tests; then
  fail "superseded purple FACODI identity must not remain"
fi

grep -Fq "'facodi'" theme_facodi/static/src/scss/primary_variables.scss || fail "FACODI palette missing"
grep -Fq 'web.assets_frontend' theme_facodi/__manifest__.py || fail "frontend asset bundle missing"
grep -Fq 'web._assets_frontend_helpers' theme_facodi/data/ir_asset.xml || fail "bootstrap overrides must use frontend helpers"

grep -Fq 'facodi-header' theme_facodi/views/customizations.xml || fail "live FACODI header missing"
grep -Fq 'facodi-footer' theme_facodi/views/customizations.xml || fail "live FACODI footer missing"
grep -Fq 'website.menu_id.child_id' theme_facodi/views/customizations.xml || fail "header must use standard dynamic Website menus"
grep -Fq 'website.placeholder_header_brand' theme_facodi/views/customizations.xml || fail "header must render the standard configurable Website brand"
grep -Fq 'portal.placeholder_user_sign_in' theme_facodi/views/customizations.xml || fail "header must retain standard Portal sign-in"
grep -Fq 'content="#142846"' theme_facodi/views/customizations.xml || fail "live browser theme color missing"

python3 - <<'PY'
from pathlib import Path
from xml.etree import ElementTree


source = Path("theme_facodi/views/customizations.xml")
root = ElementTree.parse(source).getroot()
header = root.find(".//template[@id='facodi_header']")
if header is None:
    raise SystemExit("FAIL: FACODI header template missing")

parents = {
    child: parent
    for parent in header.iter()
    for child in parent
}

brand_calls = [
    node
    for node in header.iter("t")
    if node.get("t-call") == "website.placeholder_header_brand"
]
if len(brand_calls) != 1:
    raise SystemExit("FAIL: header must call the standard Website brand exactly once")

literal_brands = [
    node
    for node in header.iter("a")
    if {"navbar-brand", "facodi-wordmark"}.issubset(
        set(node.get("class", "").split())
    )
]
if literal_brands:
    raise SystemExit("FAIL: header must not replace the configured Website logo with literal text")

for call_name in (
    "portal.placeholder_user_sign_in",
    "portal.user_dropdown",
):
    calls = [
        node
        for node in header.iter("t")
        if node.get("t-call") == call_name
    ]
    if len(calls) != 1:
        raise SystemExit(f"FAIL: header must call {call_name} exactly once")
    call = calls[0]
    if parents.get(call) is None or parents[call].tag != "ul":
        raise SystemExit(f"FAIL: {call_name} must be a direct child of the navigation list")
    if "ms-lg-2" not in call.get("_item_class.f", "").split():
        raise SystemExit(f"FAIL: {call_name} must carry its own list-item spacing")
PY

grep -Fq '@media (max-width: 991.98px)' theme_facodi/static/src/scss/website.scss \
  || fail "collapsed header rules must cover the full navbar-expand-lg range"

for class_name in facodi-hero facodi-hero-board facodi-stat-card facodi-open-section; do
  grep -Fq "$class_name" theme_facodi/views/snippets.xml || fail "live FACODI snippet class missing: $class_name"
done

grep -Fq 'body.o_wslides_body .facodi-site' theme_facodi/static/src/scss/website_slides.scss \
  || fail "eLearning styling must be scoped to the active FACODI theme"
grep -Fq '.o_record_cover_container[data-res-model="slide.channel"]' theme_facodi/static/src/scss/website_slides.scss \
  || fail "live eLearning course cover styling missing"
grep -Fq '.o_wslides_js_course_join_link.btn-primary' theme_facodi/static/src/scss/website_slides.scss \
  || fail "live eLearning join action styling missing"

if grep -R -n '<record[^>]*model="website.page"' theme_facodi --include='*.xml'; then
  fail "presentation theme must not import editorial Website pages"
fi

if grep -R -n '\$facodi-' theme_facodi/static/src/scss \
    --include='*.scss' --exclude='primary_variables.scss'; then
  fail "frontend SCSS must not depend on theme-primary-only FACODI variables"
fi

if grep -R -n 'website_facodi' README.md docs/architecture.md; then
  fail "current docs still describe website_facodi as the active addon"
fi

grep -Fq 'theme_common' README.md || fail "README must document theme_common"
grep -Fq 'odoo/design-themes' docs/architecture.md || fail "architecture must document upstream design-themes"
grep -Fq 'edu-open2.odoo.com' README.md || fail "README must name the live visual source"
grep -Fq '#142846' README.md || fail "README must document live FACODI ink"
grep -Fq '#EFFF00' README.md || fail "README must document live FACODI sun"
grep -Fq 'does not import Website pages' README.md || fail "README must document the editorial-page boundary"
grep -Fq 'facodi-online.css' docs/architecture.md || fail "architecture must document the database asset source"
grep -Fq 'theme_default' docs/architecture.md || fail "architecture must document the live standard theme baseline"
grep -Fq '"version": "19.0.4.0.0"' theme_facodi/__manifest__.py || fail "live-source release version missing"

echo "PASS: theme module contract"

if grep -Rq 'prefers-color-scheme: dark\|background-image: none !important' theme_facodi/static/src/scss; then
  fail "partial dark mode or hidden editorial cover regression"
fi
grep -Fq 't-call="website.submenu"' theme_facodi/views/customizations.xml || fail "native submenu missing"
python3 - <<'CHECK'
import ast
from pathlib import Path
from xml.etree import ElementTree as ET
manifest=ast.literal_eval(Path('theme_facodi/__manifest__.py').read_text())
for path in Path('theme_facodi').rglob('*.xml'):
    ET.parse(path)
blocks={n.get('id') for n in ET.parse('theme_facodi/views/snippets.xml').getroot().findall('template')}
pages=ET.parse('theme_facodi/views/page_templates.xml').getroot()
compositions=[n for n in pages.findall('template') if n.get('id','').startswith('new_page_template_sections_')]
assert len(compositions) == 10
for page in compositions:
    for node in page.iter('t'):
        key=node.get('t-snippet-call')
        assert key.startswith('theme_facodi.') and key.split('.')[1] in blocks
CHECK
