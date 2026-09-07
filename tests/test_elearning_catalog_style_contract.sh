#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

SCSS="theme_facodi/static/src/scss/website_slides.scss"
[[ -f "$SCSS" ]] || fail "website_slides.scss missing"

for selector in \
  '.facodi-slides-catalog' \
  '.facodi-slides-grid' \
  '.facodi-course-media' \
  '.facodi-course-fallback' \
  '.facodi-lesson-media' \
  '.facodi-lesson-fallback' \
  '.facodi-content-type'; do
  grep -Fq "$selector" "$SCSS" || fail "missing eLearning selector: $selector"
done

grep -Fq 'grid-template-columns' "$SCSS" || fail "catalogue grid must define responsive columns"
grep -Eq 'object-fit:[[:space:]]*cover' "$SCSS" || fail "catalogue media must crop predictably"
grep -Fq ':focus-visible' "$SCSS" || fail "eLearning actions must expose keyboard focus"
grep -Fq 'prefers-reduced-motion' "$SCSS" || fail "eLearning motion must respect reduced-motion preferences"

for breakpoint in 576 992 1280 1600; do
  grep -Fq "min-width: ${breakpoint}px" "$SCSS" \
    || fail "missing responsive catalogue breakpoint: ${breakpoint}px"
done

echo "PASS: responsive eLearning catalogue style contract"