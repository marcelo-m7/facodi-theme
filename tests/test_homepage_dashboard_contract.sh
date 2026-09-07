#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

SNIPPET="theme_facodi/views/snippets/s_facodi_course_showcase.xml"
DATA="theme_facodi/data/facodi_course_snippet.xml"
MODEL="theme_facodi/models/website.py"
PAGES="theme_facodi/views/page_templates.xml"
REGISTRY="theme_facodi/views/snippets/snippets.xml"
MANIFEST="theme_facodi/__manifest__.py"
SCSS="theme_facodi/static/src/scss/snippets.scss"

[[ -f "$SNIPPET" ]] || fail "FACODI course showcase snippet is missing"
[[ -f "$DATA" ]] || fail "FACODI course dynamic-filter data is missing"
[[ -f "$MODEL" ]] || fail "FACODI Website snippet defaults are missing"

grep -Fq 'id="s_facodi_course_showcase"' "$SNIPPET" \
  || fail "course showcase snippet id is missing"
grep -Fq 'class="s_facodi_course_showcase' "$SNIPPET" \
  || fail "course showcase root class is missing"
grep -Fq 's_dynamic_snippet' "$SNIPPET" \
  || fail "course showcase must use Odoo dynamic snippet infrastructure"
grep -Fq 'dynamic_snippet_template' "$SNIPPET" \
  || fail "course showcase must provide Odoo dynamic snippet render target"
grep -Fq 'My learning journey' "$SNIPPET" \
  || fail "course showcase sidebar copy is missing"
grep -Fq 'Published courses' "$SNIPPET" \
  || fail "course showcase heading is missing"
grep -Fq 'Next study' "$SNIPPET" \
  || fail "course showcase next-study panel is missing"

if grep -Eq 'request\.env|sudo\(\)' "$SNIPPET"; then
  fail "course showcase must not query business data directly from QWeb"
fi

grep -Fq 'model="ir.filters"' "$DATA" \
  || fail "course showcase needs a standard ir.filters record"
grep -Fq 'model="website.snippet.filter"' "$DATA" \
  || fail "course showcase needs a standard website.snippet.filter record"
grep -Fq "slide.channel" "$DATA" \
  || fail "course showcase filter must target slide.channel"
grep -Fq "website_published" "$DATA" \
  || fail "course showcase filter must restrict results to published courses"
grep -Fq 'dynamic_filter_template_slide_channel_facodi_course_card' "$SNIPPET" \
  || fail "course showcase course-card template is missing"

grep -Fq 'def _get_snippet_defaults' "$MODEL" \
  || fail "Website snippet defaults override is missing"
grep -Fq 'theme_facodi.s_facodi_course_showcase' "$MODEL" \
  || fail "course showcase defaults are not registered"
grep -Fq 'theme_facodi.dynamic_filter_published_courses' "$MODEL" \
  || fail "course showcase does not reference its dynamic filter"
grep -Fq 'theme_facodi.dynamic_filter_template_slide_channel_facodi_course_card' "$MODEL" \
  || fail "course showcase does not reference its card template"

grep -Fq 'from . import website' theme_facodi/models/__init__.py \
  || fail "theme models package must load Website snippet defaults"
grep -Fq 'data/facodi_course_snippet.xml' "$MANIFEST" \
  || fail "dynamic-filter data is missing from the manifest"
grep -Fq 'views/snippets/s_facodi_course_showcase.xml' "$MANIFEST" \
  || fail "course showcase view is missing from the manifest"
grep -Fq 't-snippet="theme_facodi.s_facodi_course_showcase"' "$REGISTRY" \
  || fail "course showcase is not registered in Website Builder"

grep -A8 -F 'new_page_template_sections_facodi_home' "$PAGES" \
  | grep -Fq 'theme_facodi.s_facodi_course_showcase' \
  || fail "FACODI Home composition does not include the course showcase"

grep -Fq '.s_facodi_course_showcase' "$SCSS" \
  || fail "course showcase styles are missing"
grep -Fq '.facodi-course-grid' "$SCSS" \
  || fail "course grid styles are missing"
grep -Fq '.facodi-course-card' "$SCSS" \
  || fail "course card styles are missing"

echo "PASS: FACODI homepage dashboard contract"
