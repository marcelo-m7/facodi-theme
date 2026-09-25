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
  '.facodi-content-type' \
  '.o_record_cover_container[data-res-model="slide.channel"]' \
  '.o_wslides_course_nav' \
  '.o_wslides_course_card' \
  '.o_wslides_slide_list_category_header' \
  '.o_wslides_slides_list_slide' \
  '.o_wslides_js_course_join_link.btn-primary' \
  '.o_wslides_done_button.btn-primary'; do
  grep -Fq "$selector" "$SCSS" || fail "missing eLearning selector: $selector"
done

grep -Fq 'grid-template-columns' "$SCSS" || fail "catalogue grid must define responsive columns"
grep -Eq 'object-fit:[[:space:]]*cover' "$SCSS" || fail "catalogue media must crop predictably"
grep -Fq ':focus-visible' "$SCSS" || fail "eLearning actions must expose keyboard focus"
grep -Fq 'prefers-reduced-motion' "$SCSS" || fail "eLearning motion must respect reduced-motion preferences"
grep -Fq 'var(--facodi-shadow)' "$SCSS" || fail "eLearning cards must use shared Campus Paper shadow"
grep -Fq 'var(--facodi-sun)' "$SCSS" || fail "eLearning primary actions must use the highlighter accent"
grep -Fq '[style*="linear-gradient(120deg, #875A7B, #78516F)"]' "$SCSS" || fail "default-cover override must remain editor-safe"

for breakpoint in 576 992 1280 1600; do
  grep -Fq "min-width: ${breakpoint}px" "$SCSS" \
    || fail "missing responsive catalogue breakpoint: ${breakpoint}px"
done



python3 - <<'PY'
from pathlib import Path

source = Path("theme_facodi/static/src/scss/website_slides.scss").read_text(encoding="utf-8")
selector = '.o_record_cover_container[data-res-model="slide.channel"][style*="linear-gradient(120deg, #875A7B, #78516F)"]'
override = "background-image: linear-gradient(120deg, var(--facodi-paper-warm), var(--facodi-mint)) !important;"
start = source.find(selector)
if start < 0:
    raise SystemExit("FAIL: exact default-cover override missing")
if source.count(override) != 1:
    raise SystemExit("FAIL: default-cover !important override must exist exactly once")
block = source[start:]
if override not in block:
    raise SystemExit("FAIL: default-cover override must be scoped under the exact Odoo default selector")
if ".o_wslides_course_header" not in block or ".o_wslides_lesson_header" not in block:
    raise SystemExit("FAIL: light default cover must explicitly restyle course and lesson headings")
if "color: var(--facodi-ink)" not in block:
    raise SystemExit("FAIL: light default cover headings must use dark ink text")
PY

echo "PASS: responsive eLearning catalogue style contract"