#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

XML="theme_facodi/views/website_public.xml"
SCSS="theme_facodi/static/src/scss/website_public.scss"

[[ -f "$XML" ]] || fail "D2 public Website inheritance missing"
[[ -f "$SCSS" ]] || fail "D2 public Website stylesheet missing"

grep -Fq 'inherit_id="website.contactus"' "$XML"   || fail "Contact styling must inherit native website.contactus"

for hook in   'facodi-contact-page'   'facodi-contact-form-sheet'   'facodi-contact-context'; do
  grep -Fq "$hook" "$XML" || fail "missing native Contact hook: $hook"
done

if grep -Eq '<form([[:space:]>])' "$XML"; then
  fail "D2 Contact inheritance must not introduce a second form"
fi

if grep -Eiq 'mailto:|tel:|[0-9]{3}[- .]?[0-9]{3}[- .]?[0-9]{3,4}|@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' "$XML"; then
  fail "D2 Contact inheritance must not hard-code mutable contact data"
fi

for selector in   '.facodi-contact-page'   '.facodi-contact-form-sheet'   '.facodi-contact-context'   '#contactus_form'   '.s_website_form_send'; do
  grep -Fq "$selector" "$SCSS" || fail "missing Contact style selector: $selector"
done

for marker in   'min-width: 0'   'overflow-wrap: anywhere'   '@media (max-width: 767.98px)'   ':focus-visible'; do
  grep -Fq "$marker" "$SCSS" || fail "missing Contact responsive/accessibility marker: $marker"
done

python3 - <<'PY'
from pathlib import Path
from xml.etree import ElementTree as ET

root = ET.parse("theme_facodi/views/website_public.xml").getroot()
templates = [node for node in root.findall("template") if node.get("inherit_id") == "website.contactus"]
if len(templates) != 1:
    raise SystemExit("FAIL: expected exactly one D2 inheritance of website.contactus")

template = templates[0]
if list(template.iter("form")):
    raise SystemExit("FAIL: native Contact form must not be duplicated")

for xpath in template.iter("xpath"):
    expr = xpath.get("expr", "")
    if "contactus_form" in expr and xpath.get("position") == "replace":
        raise SystemExit("FAIL: D2 must not replace #contactus_form")
PY

grep -Fq '"views/website_public.xml"' theme_facodi/__manifest__.py   || fail "D2 public Website view must be loaded by manifest"
grep -Fq '"theme_facodi/static/src/scss/website_public.scss"' theme_facodi/__manifest__.py   || fail "D2 public Website stylesheet must be loaded by frontend assets"

echo "PASS: D2 public Contact contract"

for selector in   '.facodi-policy-document'   '.facodi-policy-document h1'   '.facodi-policy-document h2'   '.facodi-policy-document h3'   '.facodi-policy-document a'   '.facodi-policy-document pre'   '.facodi-policy-document code'   '.facodi-policy-document table'   '.facodi-policy-document img'   '.facodi-policy-document iframe'   '.facodi-policy-document video'; do
  grep -Fq "$selector" "$SCSS" || fail "missing D2 policy readability selector: $selector"
done

for marker in   'overflow-x: auto'   'max-width: 100%'   'overflow-wrap: anywhere'   'max-width: 50rem'; do
  grep -Fq "$marker" "$SCSS" || fail "missing D2 policy containment marker: $marker"
done

POLICY_XML="theme_facodi/views/snippets/components/s_facodi_policy_document.xml"
if grep -Eiq 'privacy policy|cookie policy|terms and conditions|data controller|retention period' "$POLICY_XML"; then
  fail "policy snippet must remain a presentation shell, not legal authorship"
fi
