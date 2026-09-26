#!/usr/bin/env bash
set -euo pipefail
fail(){ echo "FAIL: $*" >&2; exit 1; }

SCSS="theme_facodi/static/src/scss/portal.scss"
MANIFEST="theme_facodi/__manifest__.py"

[[ -f "$SCSS" ]] || fail "portal stylesheet missing"
grep -Fq 'portal.scss' "$MANIFEST" || fail "portal stylesheet is not loaded"
# Release progression is owned by tests/test_module_contract.sh. This surface
# contract validates portal behavior/styles and must not pin an older patch version.

for selector in   '[data-facodi-portal-home="1"]'   '.facodi-portal-campus'   '.facodi-portal-board'   '.facodi-momentum-strip'   '.facodi-dashboard-action'   '.facodi-dashboard-submission'   '.o_portal_index_card'   '.o_portal_wrap:has(' '.facodi-latest-wins' '.facodi-latest-win' '.facodi-course-progress' \
  '[data-facodi-academic-map="1"]' \
  '[data-facodi-campus-pulse="1"]' \
  '.facodi-academic-map__unit' \
  '.facodi-campus-pulse__post'; do
  grep -R -Fq --include='*.scss' "$selector" theme_facodi/static/src/scss \
    || fail "portal identity selector missing from frontend SCSS: $selector"
done

for color in '#E8FD36' '#72F6B8' '#34B6CE' '#FF70A6' '#FFAE33'; do
  grep -Riq "$color" theme_facodi/static/src/scss || fail "Digital Highlighter color missing: $color"
done

grep -Fq '@media (max-width: 767.98px)' "$SCSS" || fail "mobile portal treatment missing"
grep -Fq 'prefers-reduced-motion: reduce' "$SCSS" || fail "reduced-motion portal treatment missing"

echo "PASS: FACODI portal home contract"
