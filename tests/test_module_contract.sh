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
