#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

SNIPPET="theme_facodi/views/snippets/s_facodi_course_showcase.xml"
MODEL="theme_facodi/models/website.py"
PAGES="theme_facodi/views/page_templates.xml"
REGISTRY="theme_facodi/views/snippets/snippets.xml"
MANIFEST="theme_facodi/__manifest__.py"
SCSS="theme_facodi/static/src/scss/snippets.scss"

[[ -f "$SNIPPET" ]] || fail "FACODI course showcase snippet is missing"
[[ -f "$MODEL" ]] || fail "FACODI Website snippet defaults are missing"

grep -Fq 'id="s_facodi_course_showcase"' "$SNIPPET" \
  || fail "course showcase snippet id is missing"
grep -Fq 'class="s_facodi_course_showcase' "$SNIPPET" \
  || fail "course showcase root class is missing"
grep -Fq 's_dynamic_snippet' "$SNIPPET" \
  || fail "course showcase must use Odoo dynamic snippet infrastructure"
grep -Fq 's_dynamic_snippet_container' "$SNIPPET" \
  || fail "course showcase must preserve Odoo dynamic snippet container contract"
grep -Fq 's_dynamic_snippet_content' "$SNIPPET" \
  || fail "course showcase must preserve Odoo dynamic snippet content contract"
grep -Fq 'dynamic_snippet_template' "$SNIPPET" \
  || fail "course showcase must provide Odoo dynamic snippet render target"
grep -Fq "t-att-data-filter-id=\"env.ref('theme_facodi.dynamic_filter_published_courses').id\"" "$SNIPPET" \
  || fail "course showcase must persist the FACODI presentation wrapper on the snippet root"
grep -Fq 'data-template-key="theme_facodi.dynamic_filter_template_slide_channel_facodi_course_card"' "$SNIPPET" \
  || fail "course showcase must persist its card template on the snippet root"
grep -Fq 'data-number-of-records="6"' "$SNIPPET" \
  || fail "course showcase must persist its record count on the snippet root"
grep -Fq 'Learning catalogue' "$SNIPPET" \
  || fail "course showcase learning-navigation label is missing"
for selector in 'data-facodi-content-type="roadmaps"' 'data-facodi-content-type="curricular-units"' 'data-facodi-content-type="courses"'; do
  grep -Fq "$selector" "$SNIPPET" \
    || fail "course showcase learning selector is missing $selector"
done
grep -Fq 'source=course_showcase_contribute&amp;section=learning-catalogue' "$SNIPPET" \
  || fail "course showcase contribution tab must preserve catalogue context"
for label in 'Roadmaps' 'Curricular Units' 'Courses' 'Contribute'; do
  grep -Fq "$label" "$SNIPPET" \
    || fail "course showcase learning navigation is missing label: $label"
done
if grep -Fq 'href="/web/login"' "$SNIPPET"; then
  fail "homepage learning navigation must not present login as a Saved destination"
fi
if grep -Fq 'href="/website/search"' "$SNIPPET"; then
  fail "homepage learning navigation must not use generic website search as Discover"
fi
grep -Fq 'Start somewhere useful.' "$SNIPPET" \
  || fail "course showcase heading is missing"
grep -Fq 'facodi-course-catalogue-paper' "$SNIPPET" \
  || fail "Campus Paper catalogue shell missing"
grep -Fq 'Course cards appear here when published courses are available.' "$SNIPPET" \
  || fail "standard empty-state message missing"
if grep -Eq 'UC-[0-9]+|Introduction to Algorithms|Web Open' "$SNIPPET"; then
  fail "dynamic course showcase must not ship invented static courses"
fi
grep -Fq 'Keep exploring' "$SNIPPET" \
  || fail "course showcase continuation panel is missing"

if grep -Eq 'request\.env|sudo\(\)' "$SNIPPET"; then
  fail "course showcase must not query business data directly from QWeb"
fi

[[ -f theme_facodi/data/facodi_course_snippet.xml ]] \
  || fail "FACODI course presentation wrapper data is missing"
grep -Fq 'id="published_courses_filter" model="ir.filters"' theme_facodi/data/facodi_course_snippet.xml \
  || fail "version-tolerant course visibility compatibility filter is missing"
grep -Fq "[('visibility', 'in', ['public', 'connected'])]" theme_facodi/data/facodi_course_snippet.xml \
  || fail "compatibility filter must mirror Odoo's canonical eLearning visibility domain"
grep -Fq '<field name="sort">[]</field>' theme_facodi/data/facodi_course_snippet.xml \
  || fail "compatibility filter must defer to slide.channel native ordering"
if grep -Fq 'website_published' theme_facodi/data/facodi_course_snippet.xml; then
  fail "homepage filter must not regress to publication-only visibility semantics"
fi
grep -Fq 'model="website.snippet.filter"' theme_facodi/data/facodi_course_snippet.xml \
  || fail "course showcase presentation wrapper must use website.snippet.filter"
grep -Fq 'ref="theme_facodi.published_courses_filter"' theme_facodi/data/facodi_course_snippet.xml \
  || fail "course showcase wrapper must bind to the compatibility visibility filter"
grep -Fq 'dynamic_filter_template_slide_channel_facodi_course_card' "$SNIPPET" \
  || fail "course showcase course-card template is missing"

grep -Fq 'def _get_snippet_defaults' "$MODEL" \
  || fail "Website snippet defaults override is missing"
grep -Fq 'theme_facodi.s_facodi_course_showcase' "$MODEL" \
  || fail "course showcase defaults are not registered"
grep -Fq 'theme_facodi.dynamic_filter_published_courses' "$MODEL" \
  || fail "course showcase builder defaults must reference the FACODI presentation wrapper"
grep -Fq 'theme_facodi.dynamic_filter_template_slide_channel_facodi_course_card' "$MODEL" \
  || fail "course showcase does not reference its card template"

grep -Fq 'from . import website' theme_facodi/models/__init__.py \
  || fail "theme models package must load Website snippet defaults"
grep -Fq 'data/facodi_course_snippet.xml' "$MANIFEST" \
  || fail "course presentation wrapper data must remain in the manifest"
[[ -f theme_facodi/migrations/19.0.10.70.0/post-10-align-course-filter.py ]] \
  || fail "course visibility alignment migration is missing"
grep -Fq "[('visibility', 'in', ['public', 'connected'])]" theme_facodi/migrations/19.0.10.70.0/post-10-align-course-filter.py \
  || fail "upgrade migration must align persisted visibility semantics"
[[ ! -f theme_facodi/migrations/19.0.10.70.0/post-10-retire-course-filter.py ]] \
  || fail "obsolete retire-course-filter migration must stay removed"
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
grep -Fq 'data-facodi-catalogue-switcher="1"' "$SNIPPET" \
  || fail "dynamic homepage catalogue selector missing"
grep -Fq 'theme_facodi/static/src/js/facodi_catalogue_switcher.js' "$MANIFEST" \
  || fail "dynamic homepage catalogue JavaScript missing from frontend assets"

echo "PASS: FACODI homepage dashboard contract"
