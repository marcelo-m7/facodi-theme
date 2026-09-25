#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

SCSS="theme_facodi/static/src/scss/learning_interfaces.scss"
[[ -f "$SCSS" ]] || fail "D1 learning interface stylesheet missing"

for selector in \
  '.facodi-learning-hero' \
  '.facodi-index-tabs' \
  '.facodi-filter-sheet' \
  '.facodi-record-card' \
  '.facodi-study-progress' \
  '.facodi-module-stack' \
  '.facodi-reference-rail' \
  '.facodi-open-callout'; do
  grep -Fq "$selector" "$SCSS" || fail "missing D1 selector: $selector"
done

for marker in \
  'min-width: 0' \
  'overflow-wrap: anywhere' \
  '@media (max-width: 767.98px)' \
  'grid-template-columns: minmax(0, 1fr)' \
  ':focus-visible' \
  'prefers-reduced-motion'; do
  grep -Fq "$marker" "$SCSS" || fail "missing D1 responsive/accessibility marker: $marker"
done

if grep -R -nE 'My Notebook|Class Questions|Open Bibliography|verified answer|[0-9]{2,}[[:space:]]+students' \
    theme_facodi --include='*.xml' --include='*.scss'; then
  fail "unsupported Stitch-only learning feature or fictional student count found"
fi

echo "PASS: D1 learning interface primitives contract"
