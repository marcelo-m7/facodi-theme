#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

SCSS="theme_facodi/static/src/scss/editorial_interfaces.scss"
[[ -f "$SCSS" ]] || fail "D2 editorial interface stylesheet missing"

declare -A COMPONENTS=(
  [s_facodi_project_story]='.facodi-project-story'
  [s_facodi_principles_ledger]='.facodi-principles-ledger'
  [s_facodi_process_timeline]='.facodi-process-timeline'
  [s_facodi_contribution_board]='.facodi-contribution-board'
  [s_facodi_bulletin_hero]='.facodi-bulletin-hero'
  [s_facodi_editorial_quote]='.facodi-editorial-quote'
  [s_facodi_contact_sheet]='.facodi-contact-sheet'
  [s_facodi_policy_document]='.facodi-policy-document'
)

for snippet_id in "${!COMPONENTS[@]}"; do
  path="theme_facodi/views/snippets/components/${snippet_id}.xml"
  selector="${COMPONENTS[$snippet_id]}"
  [[ -f "$path" ]] || fail "missing D2 component source: $path"
  grep -Fq "id=\"${snippet_id}\"" "$path" || fail "$path does not define $snippet_id"
  grep -Fq "$selector" "$SCSS" || fail "missing D2 selector: $selector"
  grep -Fq "t-snippet=\"theme_facodi.${snippet_id}\"" theme_facodi/views/snippets/snippets.xml \
    || fail "$snippet_id is not registered in Website Builder"
done

for marker in \
  'min-width: 0' \
  'overflow-wrap: anywhere' \
  '@media (max-width: 767.98px)' \
  ':focus-visible' \
  'prefers-reduced-motion'; do
  grep -Fq "$marker" "$SCSS" || fail "missing D2 responsive/accessibility marker: $marker"
done

if grep -R -nE '\b[0-9]{3}[- .]?[0-9]{3}[- .]?[0-9]{3,4}\b|example@|@example\.|123 (Main|Example|Test) (Street|St)|testimonials?|subscribers?|[0-9]+[[:space:]]+partners' \
    theme_facodi/views/snippets/components/s_facodi_{project_story,principles_ledger,process_timeline,contribution_board,bulletin_hero,editorial_quote,contact_sheet,policy_document}.xml; then
  fail "D2 snippets contain fake contact data, testimonials or metrics"
fi

if grep -R -nE 'request\.env|\.search\(|\.browse\(|\.sudo\(' \
    theme_facodi/views/snippets/components/s_facodi_{project_story,principles_ledger,process_timeline,contribution_board,bulletin_hero,editorial_quote,contact_sheet,policy_document}.xml; then
  fail "D2 component QWeb must not query ORM directly"
fi

if grep -R -n '<record[^>]*model="website.page"' theme_facodi --include='*.xml'; then
  fail "presentation theme must not import fixed editorial Website pages"
fi

echo "PASS: D2 editorial component contract"

python3 - <<'PY'
from pathlib import Path
from xml.etree import ElementTree as ET

root = ET.parse("theme_facodi/views/page_templates.xml").getroot()

expected = {
    "new_page_template_sections_facodi_about": [
        "s_facodi_intro",
        "s_facodi_project_story",
        "s_facodi_principles_ledger",
        "s_facodi_process_timeline",
        "s_facodi_institutional",
        "s_facodi_editorial_routes",
        "s_facodi_cta_sheet",
    ],
    "new_page_template_sections_facodi_how": [
        "s_facodi_intro",
        "s_facodi_process_timeline",
        "s_facodi_faq",
        "s_facodi_editorial_routes",
    ],
    "new_page_template_sections_facodi_contribution": [
        "s_facodi_intro",
        "s_facodi_contribution_board",
        "s_facodi_process_timeline",
        "s_facodi_community",
        "s_facodi_cta_sheet",
        "s_facodi_editorial_routes",
    ],
    "new_page_template_sections_facodi_manifesto": [
        "s_facodi_intro",
        "s_facodi_principles_ledger",
        "s_facodi_editorial_quote",
        "s_facodi_institutional",
        "s_facodi_editorial_routes",
    ],
    "new_page_template_sections_facodi_partners": [
        "s_facodi_intro",
        "s_facodi_ecosystem",
        "s_facodi_paper_card",
        "s_facodi_community",
        "s_facodi_editorial_routes",
    ],
}

templates = {node.get("id"): node for node in root.findall("template")}
for template_id, sequence in expected.items():
    template = templates.get(template_id)
    if template is None:
        raise SystemExit(f"FAIL: missing D2 page composition {template_id}")
    actual = [
        node.get("t-snippet-call", "").split(".", 1)[1]
        for node in template.iter("t")
        if node.get("t-snippet-call", "").startswith("theme_facodi.")
    ]
    if actual != sequence:
        raise SystemExit(
            f"FAIL: {template_id} D2 sequence mismatch: {actual!r} != {sequence!r}"
        )
PY
