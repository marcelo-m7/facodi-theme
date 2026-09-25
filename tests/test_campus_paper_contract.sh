#!/usr/bin/env bash
set -euo pipefail

fail() { echo "FAIL: $*" >&2; exit 1; }

TOKENS="theme_facodi/static/src/scss/campus_paper_tokens.scss"
PRIMITIVES="theme_facodi/static/src/scss/paper_primitives.scss"
MANIFEST="theme_facodi/__manifest__.py"

[[ -f "$TOKENS" ]] || fail "Campus Paper token file missing"
[[ -f "$PRIMITIVES" ]] || fail "Campus Paper primitive file missing"

for token in --facodi-ink-deep --facodi-sun-bright --facodi-mint-strong   --facodi-sky --facodi-coral --facodi-pink --facodi-paper-warm   --facodi-surface-page --facodi-surface-sheet --facodi-border   --facodi-shadow --facodi-shadow-hover --facodi-focus-ring; do
  grep -Fq -- "$token" "$TOKENS" || fail "missing token: $token"
done

for selector in .facodi-paper .facodi-grid-paper .facodi-sheet .facodi-note   .facodi-postit .facodi-highlight .facodi-marker-line .facodi-label   .facodi-tab .facodi-button-ghost; do
  grep -Fq "$selector" "$PRIMITIVES" || fail "missing primitive: $selector"
done

grep -Fq 'campus_paper_tokens.scss' "$MANIFEST" || fail "tokens not loaded"
grep -Fq 'paper_primitives.scss' "$MANIFEST" || fail "primitives not loaded"
grep -Fq '.facodi-text-link' theme_facodi/static/src/scss/components.scss \
  || fail "reusable FACODI text-link primitive missing"

for obsolete in   '.facodi-hero-board'   '.facodi-dashboard'   '.facodi-side-nav'   '.facodi-dashboard-main'   '.facodi-insights'   '.facodi-roadmap-card'   '.facodi-open-section'   '.facodi-open-actions'; do
  if grep -Fq "$obsolete" theme_facodi/static/src/scss/snippets.scss; then
    fail "obsolete pre-Campus-Paper selector remains: $obsolete"
  fi
done
grep -Fq ':focus-visible' "$PRIMITIVES" || fail "focus treatment missing"
grep -Fq 'prefers-reduced-motion: reduce' "$PRIMITIVES" || fail "reduced-motion treatment missing"

if grep -RniE '@import[[:space:]]+url|fonts\.googleapis\.com|fonts\.gstatic\.com'   theme_facodi/static theme_facodi/views; then
  fail "theme must not request remote fonts"
fi

echo "PASS: Campus Paper design-system contract"
