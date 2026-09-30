#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

SCSS="theme_facodi/static/src/scss/editorial_interfaces.scss"
[[ -f "$SCSS" ]] || fail "D2 editorial interface stylesheet missing"

declare -A COMPONENTS=(
  [s_facodi_about_hero]='.facodi-about-hero'
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
    theme_facodi/views/snippets/components/s_facodi_{about_hero,project_story,principles_ledger,process_timeline,contribution_board,bulletin_hero,editorial_quote,contact_sheet,policy_document}.xml; then
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
    "new_page_template_sections_facodi_about": [],
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

grep -Fq 'grid-auto-rows: 1fr' theme_facodi/static/src/scss/editorial_interfaces.scss \
  || fail "principles ledger must equalize desktop card rows"
grep -Fq 'min-height: 13rem' theme_facodi/static/src/scss/editorial_interfaces.scss \
  || fail "principles cards need stable desktop rhythm"
grep -Fq 'grid-template-columns: 3rem minmax(0, 1fr)' theme_facodi/static/src/scss/editorial_interfaces.scss \
  || fail "process timeline must use a fixed index rail"
grep -Fq 'min-height: 5.25rem' theme_facodi/static/src/scss/editorial_interfaces.scss \
  || fail "process timeline content blocks need consistent vertical rhythm"

ABOUT_TEMPLATE="theme_facodi/views/page_templates.xml"
grep -Fq 'class="oe_structure facodi-about-rebuilt"' "$ABOUT_TEMPLATE" \
  || fail "rebuilt About page root missing"
grep -Fq 'overflow:hidden' "$ABOUT_TEMPLATE" \
  || fail "rebuilt About page must hard-stop page-level overflow"
grep -Fq 'min-width:0' "$ABOUT_TEMPLATE" \
  || fail "rebuilt About page descendants must be allowed to shrink"
grep -Fq 'overflow-wrap:anywhere' "$ABOUT_TEMPLATE" \
  || fail "rebuilt About copy must not force horizontal overflow"
grep -Fq 'id="how-it-works"' "$ABOUT_TEMPLATE" \
  || fail "rebuilt About page must preserve the how-it-works anchor"
grep -Fq 'about_resource_cta&amp;section=about' "$ABOUT_TEMPLATE" \
  || fail "rebuilt About page contribution CTA must preserve provenance"
if awk '/new_page_template_sections_facodi_about/{flag=1} /new_page_template_sections_facodi_community/{flag=0} flag' "$ABOUT_TEMPLATE" | grep -Eq 't-snippet-call|data-facodi-dot-grid|data-facodi-motion'; then
  fail "rebuilt About page must not use interactive snippet composition"
fi

if awk '/new_page_template_sections_facodi_about/{flag=1} /new_page_template_sections_facodi_community/{flag=0} flag' "$ABOUT_TEMPLATE" | grep -Eq 'position:fixed|position:absolute|100vw'; then
  fail "rebuilt About page must not introduce viewport-sized or detached layout primitives"
fi
