#!/usr/bin/env bash
set -euo pipefail

fail() { echo "FAIL: $*" >&2; exit 1; }

SCSS="theme_facodi/static/src/scss/odoo_surfaces.scss"
MANIFEST="theme_facodi/__manifest__.py"

[[ -f "$SCSS" ]] || fail "systemic Odoo surface stylesheet missing"
grep -Fq 'odoo_surfaces.scss' "$MANIFEST" || fail "systemic Odoo surfaces are not loaded"
grep -Fq '"version": "19.0.10.8.0"' "$MANIFEST" || fail "theme version was not advanced"

for selector in   '.card:not('   '.btn-secondary'   '.text-bg-primary'   '.list-group-item'   '.nav-pills .nav-link'   '.page-link'   '.o_portal_wrap'   '.oe_login_form'   '.modal-content'   '.toast'   '.accordion'   '.o_search_page'   '.o_wforum_forum'   '.o_wprofile_user_profile'   '.o_wslides_quiz_question'   '.table-responsive'; do
  grep -Fq "$selector" "$SCSS" || fail "standard Odoo surface not personalized: $selector"
done

for token in   'var(--facodi-ink)'   'var(--facodi-sun)'   'var(--facodi-mint)'   'var(--facodi-cyan)'   'var(--facodi-surface-sheet)'   'var(--facodi-focus-ring)'; do
  grep -Fq "$token" "$SCSS" || fail "FACODI token not used: $token"
done

grep -Fq '@media (max-width: 767.98px)' "$SCSS" || fail "mobile treatment missing"
grep -Fq 'prefers-reduced-motion: reduce' "$SCSS" || fail "reduced motion treatment missing"

if grep -Eq '@import[[:space:]]+url|fonts\.googleapis\.com|fonts\.gstatic\.com' "$SCSS"; then
  fail "systemic surface layer must not request remote fonts"
fi

echo "PASS: systemic Odoo Campus Paper surface contract"
