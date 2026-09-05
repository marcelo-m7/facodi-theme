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
[[ ! -d theme_facodi/controllers ]] || fail "presentation theme must not add parallel learning routes/controllers"

grep -Fq '"theme_common"' theme_facodi/__manifest__.py || fail "theme_common dependency missing"
grep -Fq '"website_slides"' theme_facodi/__manifest__.py || fail "website_slides dependency missing"
grep -Fq 'Theme/Education' theme_facodi/__manifest__.py || fail "theme category must be Theme/Education"
grep -Fq 'theme_facodi.primary_variables_scss' theme_facodi/data/ir_asset.xml || fail "primary variables asset key missing"
grep -Fq 'web._assets_primary_variables' theme_facodi/data/ir_asset.xml || fail "primary variables bundle missing"

if grep -R -nE 'request\.env|sudo\(\)|href="/theme_facodi/static/src/img/favicon\.svg"' theme_facodi --include='*.xml'; then
  fail "theme QWeb contains business-data access or a forced favicon"
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

grep -Fq '#6a4bff' theme_facodi/static/src/scss/primary_variables.scss || fail "FACODI purple missing"
grep -Fq '#5dc7ff' theme_facodi/static/src/scss/primary_variables.scss || fail "FACODI blue missing"
grep -Fq "'facodi'" theme_facodi/static/src/scss/primary_variables.scss || fail "FACODI palette missing"
grep -Fq 'web.assets_frontend' theme_facodi/__manifest__.py || fail "frontend asset bundle missing"
grep -Fq 'web._assets_frontend_helpers' theme_facodi/data/ir_asset.xml || fail "bootstrap overrides must use frontend helpers"

if grep -R -n '\$facodi-' theme_facodi/static/src/scss \
    --include='*.scss' --exclude='primary_variables.scss'; then
  fail "frontend SCSS must not depend on theme-primary-only FACODI variables"
fi

if grep -R -n 'website_facodi' README.md docs/architecture.md; then
  fail "current docs still describe website_facodi as the active addon"
fi

grep -Fq 'theme_common' README.md || fail "README must document theme_common"
grep -Fq 'odoo/design-themes' docs/architecture.md || fail "architecture must document upstream design-themes"

echo "PASS: theme module contract"
