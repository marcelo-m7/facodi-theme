#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

COMPONENT_IDS=(
  s_facodi_highlighter_heading
  s_facodi_paper_card
  s_facodi_sticky_note
  s_facodi_folder_tabs
  s_facodi_filter_pills
  s_facodi_course_card
  s_facodi_study_steps
  s_facodi_cta_sheet
  s_facodi_metadata_row
  s_facodi_highlighter_callout
  s_facodi_project_story
  s_facodi_principles_ledger
  s_facodi_process_timeline
  s_facodi_contribution_board
  s_facodi_bulletin_hero
  s_facodi_editorial_quote
  s_facodi_contact_sheet
  s_facodi_policy_document
  s_facodi_student_id_card
  s_facodi_progress_meter
  s_facodi_uc_progress_card
  s_facodi_notebook_sheet
  s_facodi_module_index
  s_facodi_code_exercise
  s_facodi_forum_postit
  s_facodi_roadmap_metro
)

registry="theme_facodi/views/snippets/snippets.xml"
manifest="theme_facodi/__manifest__.py"
styles="theme_facodi/static/src/scss/components.scss"

[[ -f "$registry" ]] || fail "snippet registry missing"
grep -Fq 'snippet_content' "$registry" || fail "FACODI reusable blocks must register as native inner snippets"

for component_id in "${COMPONENT_IDS[@]}"; do
  path="theme_facodi/views/snippets/components/${component_id}.xml"
  [[ -f "$path" ]] || fail "missing reusable component source: $path"
  grep -Fq "id=\"${component_id}\"" "$path"     || fail "$component_id source must expose a stable template id"
  grep -Fq "data-snippet=\"${component_id}\"" "$path"     || fail "$component_id must expose a Website Builder data-snippet hook"
  grep -Fq "views/snippets/components/${component_id}.xml" "$manifest"     || fail "$component_id source must be loaded by the theme manifest"
  grep -Fq "t-snippet=\"theme_facodi.${component_id}\"" "$registry"     || fail "$component_id must be registered in the Website Builder"
done

python3 - <<'PY'
from pathlib import Path
from xml.etree import ElementTree as ET

component_dir = Path("theme_facodi/views/snippets/components")
registry_path = Path("theme_facodi/views/snippets/snippets.xml")
component_ids = {
    "s_facodi_highlighter_heading",
    "s_facodi_paper_card",
    "s_facodi_sticky_note",
    "s_facodi_folder_tabs",
    "s_facodi_filter_pills",
    "s_facodi_course_card",
    "s_facodi_study_steps",
    "s_facodi_cta_sheet",
    "s_facodi_metadata_row",
    "s_facodi_highlighter_callout",
    "s_facodi_project_story",
    "s_facodi_principles_ledger",
    "s_facodi_process_timeline",
    "s_facodi_contribution_board",
    "s_facodi_bulletin_hero",
    "s_facodi_editorial_quote",
    "s_facodi_contact_sheet",
    "s_facodi_policy_document",
    "s_facodi_student_id_card",
    "s_facodi_progress_meter",
    "s_facodi_uc_progress_card",
    "s_facodi_notebook_sheet",
    "s_facodi_module_index",
    "s_facodi_code_exercise",
    "s_facodi_forum_postit",
    "s_facodi_roadmap_metro",
}

sources = list(component_dir.glob("s_facodi_*.xml"))
if {path.stem for path in sources} != component_ids:
    raise SystemExit("FAIL: reusable component sources must match the approved Campus Paper component collection")

for path in sources:
    root = ET.parse(path).getroot()
    templates = [node for node in root.findall("template") if node.get("id") == path.stem]
    if len(templates) != 1:
        raise SystemExit(f"FAIL: {path} must define exactly one primary component template")
    template = templates[0]
    snippet_nodes = [node for node in template.iter() if node.get("data-snippet") == path.stem]
    if len(snippet_nodes) != 1:
        raise SystemExit(f"FAIL: {path.stem} must render exactly one matching data-snippet root")

registry = ET.parse(registry_path).getroot()
content_xpaths = [
    node for node in registry.iter("xpath")
    if node.get("expr") == "//snippets[@id='snippet_content']"
]
if len(content_xpaths) != 1:
    raise SystemExit("FAIL: reusable FACODI blocks must extend website.snippets#snippet_content exactly once")

registered = {}
for node in content_xpaths[0].iter("t"):
    key = node.get("t-snippet", "")
    if key.startswith("theme_facodi.s_facodi_"):
        registered[key.split(".", 1)[1]] = node

missing = component_ids - registered.keys()
if missing:
    raise SystemExit(f"FAIL: reusable component registry missing {sorted(missing)}")

for component_id in component_ids:
    node = registered[component_id]
    if node.get("group") != "facodi":
        raise SystemExit(f"FAIL: {component_id} must stay in the FACODI builder group")
    keywords = node.find("keywords")
    if keywords is None or not (keywords.text or "").strip():
        raise SystemExit(f"FAIL: {component_id} must expose Website Builder search keywords")
PY

if grep -R -nE 'request\.env|sudo\(\)|href="/web/login"|/web/content/[0-9]+|o_not_editable|oe_unremovable|oe_unmovable'     theme_facodi/views/snippets/components --include='*.xml'; then
  fail "reusable components must stay editor-friendly and avoid business-data access, private login CTAs, or database asset ids"
fi

for class_name in \
  facodi-highlighter-heading \\
  facodi-paper-card \\
  facodi-sticky-note \\
  facodi-folder-tabs \\
  facodi-filter-pills \\
  facodi-static-course-card \\
  facodi-study-steps \\
  facodi-cta-sheet \\
  facodi-metadata-row \\
  facodi-highlighter-callout \\
  facodi-student-id-card \\
  facodi-progress-meter \\
  facodi-uc-progress-card \\
  facodi-notebook-sheet \\
  facodi-module-index \\
  facodi-code-exercise \\
  facodi-forum-postit \\
  facodi-roadmap-metro; do
  grep -Fq ".$class_name" "$styles"     || fail "missing reusable component style: $class_name"
done

echo "PASS: reusable FACODI Campus Paper component contract"
