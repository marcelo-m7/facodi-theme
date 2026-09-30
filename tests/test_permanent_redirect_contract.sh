#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

DATA="theme_facodi/data/website_rewrites.xml"
MIGRATION="theme_facodi/migrations/19.0.10.1.0/post-10-permanent-editorial-redirects.py"

[[ -f "$DATA" ]] || fail "permanent redirect data missing"
[[ -f "$MIGRATION" ]] || fail "permanent redirect migration missing"

grep -Fq '"data/website_rewrites.xml"' theme_facodi/__manifest__.py   || fail "redirect data must be loaded by manifest"

for mapping in   '/facodi|/'   '/sobre|/about'   '/manifesto|/about'   '/comunidade|/about'   '/parceiros|/about'   '/roadmap|/about#how-it-works'   '/como-contribuir|/contribuir/recurso'   '/contribuir|/contribuir/recurso'; do
  from="${mapping%%|*}"
  to="${mapping#*|}"
  grep -Fq "<field name=\"url_from\">${from}</field>" "$DATA"     || fail "missing 301 source ${from}"
  grep -Fq "<field name=\"url_to\">${to}</field>" "$DATA"     || fail "missing 301 target ${to}"
done

count="$(grep -c '<field name="redirect_type">301</field>' "$DATA")"
[[ "$count" -eq 8 ]] || fail "expected exactly eight permanent redirect records"

if grep -Fq '<field name="url_from">/roadmaps</field>' "$DATA"; then
  fail "curriculum /roadmaps route must never be redirected"
fi
if grep -Fq '<field name="url_from">/contribuir/recurso</field>' "$DATA"; then
  fail "guided contribution route must remain canonical"
fi

grep -Fq "is_published" "$MIGRATION"   || fail "legacy editor-owned pages must be unpublished before 301 fallback"
grep -Fq "website.menu" "$MIGRATION"   || fail "internal Website menus must be moved to canonical URLs"
grep -Fq "website.rewrite" "$MIGRATION"   || fail "migration must reconcile native Odoo rewrite records"
grep -Fq '"redirect_type": "301"' "$MIGRATION"   || fail "migration must reconcile redirects as permanent 301"
grep -Fq "/roadmaps" "$MIGRATION" && fail "migration must not touch curriculum /roadmaps"

grep -Fq 'background-color: #0B1325 !important' theme_facodi/static/src/scss/website.scss   || fail "footer shell must remain #0B1325"
grep -Fq 'background: #0B1325' theme_facodi/static/src/scss/website.scss   || fail "FACODI footer must remain #0B1325"

MIGRATION="theme_facodi/migrations/19.0.10.74.0/post-10-canonical-about-route.py"
[[ -f "$MIGRATION" ]] || fail "canonical About migration missing"
grep -Fq '("/sobre", "/about")' "$MIGRATION" \
  || fail "canonical About migration must retain /sobre as a 301 source"
grep -Fq 'canonical_page.write({"url": "/about"})' "$MIGRATION" \
  || fail "canonical About migration must preserve the editor-owned page"

echo "PASS: permanent editorial redirect contract"
