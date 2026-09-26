#!/usr/bin/env bash
set -euo pipefail

fail() { echo "FAIL: $*" >&2; exit 1; }

DOC="docs/canonical_routes.md"
[[ -f "$DOC" ]] || fail "canonical route/redirect runbook missing"

for mapping in \
  '/facodi -> /' \
  '/cursos -> /slides' \
  '/roadmap -> /roadmaps' \
  '/contacto -> /contactus'; do
  grep -Fq "$mapping" "$DOC" || fail "missing permanent redirect mapping: $mapping"
done

python3 - <<'PY'
from pathlib import Path
from xml.etree import ElementTree as ET

legacy = {"/facodi", "/cursos", "/roadmap", "/contacto"}
violations = []

for path in Path("theme_facodi/views").rglob("*.xml"):
    root = ET.parse(path).getroot()
    for node in root.iter():
        href = node.get("href")
        if href in legacy:
            violations.append(f"{path}: href={href}")

if violations:
    raise SystemExit("FAIL: FACODI components still link to legacy aliases:\n" + "\n".join(violations))
PY

grep -Fq 'website.rewrite' "$DOC" || fail "redirect strategy must use native Odoo website.rewrite"
grep -Fq "redirect_type='301'" "$DOC" || fail "redirect strategy must be permanent 301"
grep -Fq '#0B1325' "$DOC" || fail "route consolidation must preserve the approved footer color"

echo "PASS: canonical FACODI route contract"
