#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

SCSS="theme_facodi/static/src/scss/website_slides_player.scss"
MANIFEST="theme_facodi/__manifest__.py"
PLAYER_XML="theme_facodi/views/website_slides_player.xml"

[[ -f "$PLAYER_XML" ]] || fail "study player QWeb missing"
[[ -f "$SCSS" ]] || fail "website_slides_player.scss missing"

grep -Fq 'theme_facodi/static/src/scss/website_slides_player.scss' "$MANIFEST"   || fail "study player stylesheet missing from frontend assets"

for selector in   '.facodi-study-player'   '.facodi-study-player__content'   '.facodi-study-player__index'   '.facodi-study-tools'   '.facodi-study-tools__tab'   '.facodi-study-tools__panel'   '.o_wslides_fs_sidebar_list_item.active'; do
  grep -Fq "$selector" "$SCSS" || fail "missing study player selector: $selector"
done

for token in   'var(--facodi-ink)'   'var(--facodi-sun)'   'var(--facodi-mint)'   'var(--facodi-cyan)'   'var(--facodi-shadow)'; do
  grep -Fq "$token" "$SCSS" || fail "study player must reuse FACODI token: $token"
done

grep -Fq ':focus-visible' "$SCSS"   || fail "study player must expose visible keyboard focus"
grep -Fq 'background: var(--facodi-sun) !important' "$SCSS" \
  || fail "active study controls must keep the high-contrast FACODI sun surface"
grep -Fq 'color: var(--facodi-ink) !important' "$SCSS" \
  || fail "study controls must force readable ink text against Odoo fullscreen styles"
grep -Fq '.facodi-study-tools__contribution' "$SCSS" \
  || fail "study contribution buttons need fullscreen-specific contrast styling"
grep -Fq 'prefers-reduced-motion' "$SCSS"   || fail "study player must respect reduced-motion preferences"
grep -Eq '@media[[:space:]]*\(max-width:[[:space:]]*767\.98px\)' "$SCSS"   || fail "study player mobile breakpoint missing"
grep -Fq 'body.o_wslides_body .facodi-study-player' "$SCSS" \
  || fail "fullscreen player styles must not depend on the normal .facodi-site website wrapper"
grep -Fq 'min-height: 72vh' "$SCSS" \
  || fail "video/document ratio needs a stable fullscreen minimum height"
grep -Fq 'iframe,' "$SCSS" \
  || fail "native iframe players must be preserved explicitly"

if grep -Eiq 'fonts\.googleapis|fonts\.gstatic|https?://.*\.(woff2?|ttf|otf)' "$SCSS"; then
  fail "study player must not load remote fonts"
fi

if grep -Eiq 'supabase|createClient|fetch\(' "$SCSS" "$PLAYER_XML"; then
  fail "presentation-only player must not contain Supabase/network client code"
fi

if grep -Eq '\.search\(' "$PLAYER_XML"; then
  fail "study player QWeb must not perform ORM searches"
fi

echo "PASS: FACODI study player style contract"
