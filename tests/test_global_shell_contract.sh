#!/usr/bin/env bash
set -euo pipefail

fail() { echo "FAIL: $*" >&2; exit 1; }

HEADER="theme_facodi/views/header.xml"
FOOTER="theme_facodi/views/customizations.xml"
SCSS="theme_facodi/static/src/scss/website.scss"

for anchor in   'facodi-nav-shell'   'website.navbar_nav'   'portal.placeholder_user_sign_in'   'portal.user_dropdown'   'website.template_header_mobile'; do
  grep -Fq "$anchor" "$HEADER" || fail "native header hook missing: $anchor"
done

for anchor in 'facodi-footer-campus' 'facodi-footer-note' 'facodi-footer-links'; do
  grep -Fq "$anchor" "$FOOTER" || fail "footer Campus Paper hook missing: $anchor"
done

for selector in   '.facodi-header'   '.facodi-dropdown-menu'   '.o_header_mobile'   '.facodi-footer-campus'   '.facodi-footer-note'   '.facodi-site .form-control'   '.facodi-site .form-select'; do
  grep -Fq "$selector" "$SCSS" || fail "global Campus Paper selector missing: $selector"
done

grep -Fq ':focus-visible' "$SCSS" || fail "global shell needs keyboard focus styles"
grep -Fq 'min-height: 2.75rem' "$SCSS" || fail "public actions must keep a 44px target"

echo "PASS: Campus Paper global shell contract"
