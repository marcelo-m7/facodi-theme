#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

HERO="theme_facodi/views/snippets/s_facodi_hero.xml"

for anchor in 'Knowledge is everywhere.' 'Find your next step.' 'Explore courses' 'See how FACODI works' 'facodi-hero-study-board' 'facodi-study-sheet' 'facodi-study-note' 'facodi-study-route' 'data-facodi-dot-grid' 'facodi-dot-grid__canvas'; do
  grep -Fq "$anchor" "$HERO" || fail "Campus Paper hero missing: $anchor"
done
if grep -Fq 'facodi-live-dot' "$HERO"; then fail "hero must not imply live status without real data"; fi

JOURNEY="theme_facodi/views/snippets/s_facodi_learning_journey.xml"
FEATURES="theme_facodi/views/snippets/s_facodi_features.xml"

for anchor in 'Explore learning in the way that makes sense to you.' 'Courses' 'Roadmaps' 'Curricular units' 'facodi-learning-entry-grid'; do
  grep -Fq "$anchor" "$JOURNEY" || fail "learning entry section missing: $anchor"
done
for route in '/courses' '/roadmaps' '/curricular-units'; do
  grep -Fq "href=\"$route\"" "$JOURNEY" || fail "learning entry route missing: $route"
done
for anchor in 'From a question to the next useful link.' 'Choose a question' 'Study at your pace' 'Follow the useful thread' 'Leave the trail clearer' 'facodi-learning-steps'; do
  grep -Fq "$anchor" "$FEATURES" || fail "learning steps missing: $anchor"
done

AREAS="theme_facodi/views/snippets/s_facodi_academic_areas.xml"
ECOSYSTEM="theme_facodi/views/snippets/s_facodi_ecosystem.xml"
REGISTRY="theme_facodi/views/snippets/snippets.xml"
PAGES="theme_facodi/views/page_templates.xml"
MANIFEST="theme_facodi/__manifest__.py"
SCSS="theme_facodi/static/src/scss/foundation_v2.scss"
COMPONENTS="theme_facodi/static/src/scss/components.scss"
SLIDES="theme_facodi/static/src/scss/website_slides.scss"

[[ -f "$AREAS" ]] || fail "academic areas snippet is missing"
[[ -f "$ECOSYSTEM" ]] || fail "ecosystem snippet is missing"
[[ -f "$SCSS" ]] || fail "Foundation v2 stylesheet is missing"

grep -Fq 'id="s_facodi_academic_areas"' "$AREAS" \
  || fail "academic areas snippet id is missing"
grep -Fq 'data-snippet="s_facodi_academic_areas"' "$AREAS" \
  || fail "academic areas snippet must expose its Website Builder identity"
for label in 'Computing &amp; Technology' 'Mathematics &amp; Data' 'Design &amp; Visual Culture' 'Business &amp; Organisations' 'Community learning'; do
  grep -Fq "$label" "$AREAS" || fail "academic areas source is missing: $label"
done
grep -Fq 'href="/courses"' "$AREAS" \
  || fail "academic areas must link to standard eLearning catalogue"
grep -Fq 'href="/curricular-units"' "$AREAS" \
  || fail "academic areas must link to FACODI curricular units"
if grep -Fq 'href="/website/search"' "$AREAS"; then
  fail "academic areas must not fall back to generic Website search"
fi

grep -Fq 'id="s_facodi_ecosystem"' "$ECOSYSTEM" \
  || fail "ecosystem snippet id is missing"
grep -Fq 'data-snippet="s_facodi_ecosystem"' "$ECOSYSTEM" \
  || fail "ecosystem snippet must expose its Website Builder identity"
for label in 'Open resources' 'Community learning' 'University network'; do
  grep -Fq "$label" "$ECOSYSTEM" || fail "ecosystem source is missing: $label"
done
grep -Fq 'source=ecosystem_contact_cta&amp;section=ecosystem&amp;topic=partnership' "$ECOSYSTEM" \
  || fail "ecosystem contact action must preserve contextual partnership intent"
grep -Fq 'href="/sobre">See how FACODI works' "$HERO" \
  || fail "hero explanation CTA must route to the live FACODI About page"
grep -R -Fq 'href="/contactus"' theme_facodi/views/snippets --include='*.xml' \
  && fail "theme snippets must not bypass the contextual contact intake"

if grep -Eq 'request\.env|sudo\(\)' "$AREAS" "$ECOSYSTEM"; then
  fail "Foundation v2 editorial snippets must not query business data directly"
fi

for id in s_facodi_academic_areas s_facodi_ecosystem; do
  grep -Fq "t-snippet=\"theme_facodi.${id}\"" "$REGISTRY" \
    || fail "$id is not registered in Website Builder"
  grep -Fq "views/snippets/${id}.xml" "$MANIFEST" \
    || fail "$id is not loaded by the manifest"
done
grep -Fq 'theme_facodi/static/src/scss/foundation_v2.scss' "$MANIFEST" \
  || fail "Foundation v2 stylesheet is not loaded in frontend assets"

python3 - <<'PY'
from pathlib import Path
from xml.etree import ElementTree as ET

root = ET.parse(Path('theme_facodi/views/page_templates.xml')).getroot()
compositions = {
    node.get('id'): [
        child.get('t-snippet-call')
        for child in node.findall('.//t[@t-snippet-call]')
    ]
    for node in root.findall('.//template')
}

required = {
    'new_page_template_sections_facodi_home': {
        'theme_facodi.s_facodi_academic_areas',
    },
    'new_page_template_sections_facodi_pathways': {
      'theme_facodi.s_facodi_editorial_pathway',
    },
    'new_page_template_sections_facodi_partners': {
        'theme_facodi.s_facodi_ecosystem',
    },
    'new_page_template_sections_facodi_community': {
        'theme_facodi.s_facodi_ecosystem',
    },
}
for composition, snippets in required.items():
    actual = set(compositions.get(composition, []))
    missing = snippets - actual
    if missing:
        raise SystemExit(f"FAIL: {composition} missing {sorted(missing)}")
PY

grep -Fq '.s_facodi_academic_areas' "$SCSS" \
  || fail "academic areas styles are missing"
grep -Fq '.facodi-area-card' "$SCSS" \
  || fail "academic area card styles are missing"
grep -Fq '.s_facodi_ecosystem' "$SCSS" \
  || fail "ecosystem styles are missing"
grep -Fq '.facodi-ecosystem-card' "$SCSS" \
  || fail "ecosystem card styles are missing"

# Standard Website/Bootstrap components remain functional and receive only
# scoped FACODI presentation overrides.
for selector in '.badge' '.breadcrumb' '.dropdown-item' '.pagination'; do
  grep -Fq "$selector" "$COMPONENTS" \
    || fail "standard Website component personalization missing: $selector"
done

# eLearning personalization must target real website_slides classes instead of
# replacing the standard course/slide templates.
for selector in '.o_wslides_slide_list_category_header' '.o_wslides_slides_list_slide'; do
  grep -Fq "$selector" "$SLIDES" \
    || fail "standard eLearning presentation selector missing: $selector"
done

python3 - <<'PY'
from xml.etree import ElementTree as ET
root = ET.parse("theme_facodi/views/page_templates.xml").getroot()
home = root.find(".//template[@id='new_page_template_sections_facodi_home']")
calls = [n.get("t-snippet-call") for n in home.iter("t") if n.get("t-snippet-call")]
expected = [
    "theme_facodi.s_facodi_hero",
    "theme_facodi.s_facodi_course_showcase",
    "theme_facodi.s_facodi_learning_journey",
    "theme_facodi.s_facodi_features",
    "theme_facodi.s_facodi_academic_areas",
    "theme_facodi.s_facodi_community",
    "theme_facodi.s_facodi_institutional",
    "theme_facodi.s_facodi_course_cta",
]
if calls != expected:
    raise SystemExit(f"FAIL: homepage order {calls!r} != {expected!r}")
PY

INTRO="theme_facodi/views/snippets/s_facodi_intro.xml"
ROUTES="theme_facodi/views/snippets/s_facodi_editorial_routes.xml"
PATHWAY="theme_facodi/views/snippets/s_facodi_editorial_pathway.xml"

grep -Fq 'facodi-editorial-intro-sheet' "$INTRO" \
  || fail "editorial intro must expose a paper-sheet hook"
grep -Fq 'facodi-editorial-route-card' "$ROUTES" \
  || fail "editorial routes need reusable paper cards"
grep -Fq 'facodi-editorial-pathway-sheet' "$PATHWAY" \
  || fail "editorial pathway needs a paper-sheet hook"

echo "PASS: FACODI Website Foundation v2 contract"

DOT_GRID="theme_facodi/static/src/js/facodi_dot_grid.js"
grep -Fq 'requestAnimationFrame' "$DOT_GRID" \
  || fail "dot grid must render through requestAnimationFrame"
grep -Fq 'ResizeObserver' "$DOT_GRID" \
  || fail "dot grid must resize with its hero"
grep -Fq 'prefers-reduced-motion: reduce' "$DOT_GRID" \
  || fail "dot grid must respect reduced motion"
if grep -Eq 'from .(react|gsap)|import .(react|gsap)' "$DOT_GRID"; then
  fail "dot grid must remain dependency-free inside the Odoo frontend"
fi
