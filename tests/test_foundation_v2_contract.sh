#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

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
for label in 'Computing &amp; Technology' 'Mathematics &amp; Data' 'Business &amp; Society' 'Languages &amp; Culture'; do
  grep -Fq "$label" "$AREAS" || fail "academic areas source is missing: $label"
done
grep -Fq 'href="/slides"' "$AREAS" \
  || fail "academic areas must link to standard eLearning catalogue"
grep -Fq 'href="/website/search"' "$AREAS" \
  || fail "academic areas must link to standard Website search"

grep -Fq 'id="s_facodi_ecosystem"' "$ECOSYSTEM" \
  || fail "ecosystem snippet id is missing"
grep -Fq 'data-snippet="s_facodi_ecosystem"' "$ECOSYSTEM" \
  || fail "ecosystem snippet must expose its Website Builder identity"
for label in 'Open resources' 'Community learning' 'University network'; do
  grep -Fq "$label" "$ECOSYSTEM" || fail "ecosystem source is missing: $label"
done
grep -Fq 'href="/contactus"' "$ECOSYSTEM" \
  || fail "ecosystem contribution action must use standard contact page"

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
        'theme_facodi.s_facodi_ecosystem',
    },
    'new_page_template_sections_facodi_pathways': {
        'theme_facodi.s_facodi_academic_areas',
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

echo "PASS: FACODI Website Foundation v2 contract"
