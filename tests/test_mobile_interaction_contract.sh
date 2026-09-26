#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

python3 - <<'PY'
from pathlib import Path
from xml.etree import ElementTree as ET

website_scss = Path("theme_facodi/static/src/scss/website.scss").read_text(encoding="utf-8")
slides_scss = Path("theme_facodi/static/src/scss/website_slides.scss").read_text(encoding="utf-8")
slides_xml = Path("theme_facodi/views/website_slides.xml")
root = ET.parse(slides_xml).getroot()

# Odoo 19's native mobile header uses a plain .nav-link.btn button targeting
# #top_menu_collapse_mobile and puts the visual glyph in .navbar-toggler-icon.
# The theme must therefore style those real native hooks, rather than the
# desktop/legacy .navbar-toggler class only.
if '[data-bs-target="#top_menu_collapse_mobile"]' not in website_scss:
    raise SystemExit(
        "FAIL: mobile header styling must target Odoo 19's actual offcanvas toggle"
    )
if ".navbar-toggler-icon" not in website_scss:
    raise SystemExit(
        "FAIL: mobile header must explicitly keep the native hamburger icon visible"
    )

# The FACODI content-type cue must live inside Odoo's standard lesson link.
# Keeping it as a sibling of the icon creates a non-clickable touch target on
# narrow screens and shrinks the title link users need to open the lesson.
template = root.find(".//template[@id='facodi_training_content_type_cue']")
if template is None:
    raise SystemExit("FAIL: FACODI training content-type template missing")

inside_slide_link = False
for xpath in template.findall("xpath"):
    expr = xpath.get("expr", "")
    if (
        "o_wslides_js_slides_list_slide_link" in expr
        and xpath.get("position") == "inside"
    ):
        inside_slide_link = True
        break
if not inside_slide_link:
    raise SystemExit(
        "FAIL: training content-type cue must be inside the standard clickable slide link"
    )

# A 44px minimum only works as a touch target when the inline anchor is promoted
# to a flex/block box. Keep the native Odoo link and URL behavior; only enlarge
# its presentation hit area.
anchor_marker = ".o_wslides_js_slides_list_slide_link {"
anchor_start = slides_scss.find(anchor_marker)
if anchor_start < 0:
    raise SystemExit("FAIL: training slide link style block missing")
anchor_end = slides_scss.find("}", anchor_start)
anchor_block = slides_scss[anchor_start:anchor_end]
if "display: flex" not in anchor_block:
    raise SystemExit("FAIL: training slide link must be a flex touch target")
if "min-height: 2.75rem" not in anchor_block:
    raise SystemExit("FAIL: training slide link must retain a 44px minimum touch target")
if "width: 100%" not in anchor_block:
    raise SystemExit("FAIL: training slide link must make its row width tappable on mobile")
PY

grep -Fq 'facodi-footer-campus' theme_facodi/views/customizations.xml || fail "Campus Paper footer hook missing"
grep -Fq '@media (max-width: 720px)' theme_facodi/static/src/scss/website.scss || fail "footer needs a phone layout"
grep -Fq '@media (max-width: 767.98px)' theme_facodi/static/src/scss/snippets.scss || fail "homepage needs a dedicated phone breakpoint"
grep -Fq 'overflow-wrap: anywhere' theme_facodi/static/src/scss/snippets.scss || fail "long translated homepage copy must wrap"

for selector in '.facodi-hero' '.facodi-learning-entry-grid' '.facodi-learning-steps' '.facodi-community-grid'; do
  grep -Fq "$selector" theme_facodi/static/src/scss/snippets.scss \
    || fail "missing mobile-critical selector: $selector"
done

grep -Fq 'grid-template-columns: minmax(0, 1fr)' theme_facodi/static/src/scss/snippets.scss \
  || fail "phone layouts must collapse to a shrinkable single column"

python3 - <<'PY'
from pathlib import Path

source = Path("theme_facodi/static/src/scss/snippets.scss").read_text(encoding="utf-8")
mobile = source.split("@media (max-width: 767.98px)", 1)[1].split("@media (prefers-reduced-motion", 1)[0]
if ".facodi-hero-study-board {" not in mobile:
    raise SystemExit("FAIL: phone hero study-board rule missing")
board = mobile.split(".facodi-hero-study-board {", 1)[1].split("}", 1)[0]
if "display: grid" not in board:
    raise SystemExit("FAIL: phone hero study board must use normal grid flow")
note = mobile.split(".facodi-study-note {", 1)[1].split("}", 1)[0]
if "position: static" not in note:
    raise SystemExit("FAIL: phone study notes must leave absolute positioning")
PY

grep -Fq 'min-width: 0' theme_facodi/static/src/scss/website_slides.scss \
  || fail "eLearning cards and rows must remain shrinkable"
grep -Fq 'overflow-wrap' theme_facodi/static/src/scss/website_slides.scss \
  || fail "long course and lesson text must wrap"

grep -Fq 'overscroll-behavior-inline: contain' theme_facodi/static/src/scss/curriculum.scss \
  || fail "wide curriculum tables must stay inside their scroll container"
grep -Fq 'grid-template-columns: minmax(0, 1fr)' theme_facodi/static/src/scss/curriculum.scss \
  || fail "curriculum mobile layouts must collapse to one shrinkable column"

grep -Fq '@media (max-width: 767.98px)' theme_facodi/static/src/scss/learning_interfaces.scss \
  || fail "D1 learning interfaces need an explicit phone breakpoint"
grep -Fq 'grid-template-columns: minmax(0, 1fr)' theme_facodi/static/src/scss/learning_interfaces.scss \
  || fail "D1 learning interfaces must collapse to a shrinkable phone column"
grep -Fq 'overflow-wrap: anywhere' theme_facodi/static/src/scss/learning_interfaces.scss \
  || fail "D1 learning titles and metadata must wrap on narrow screens"

echo "PASS: mobile menu, eLearning touch and Campus Paper interaction contract"

grep -Fq '@media (max-width: 767.98px)' theme_facodi/static/src/scss/editorial_interfaces.scss \
  || fail "D2 editorial interfaces need a phone breakpoint"
grep -Fq 'grid-template-columns: minmax(0, 1fr)' theme_facodi/static/src/scss/editorial_interfaces.scss \
  || fail "D2 editorial layouts must collapse to a shrinkable phone column"
grep -Fq 'overflow-wrap: anywhere' theme_facodi/static/src/scss/editorial_interfaces.scss \
  || fail "D2 editorial copy and URLs must wrap at narrow widths"

grep -Fq '.facodi-site .facodi-policy-document {' theme_facodi/static/src/scss/website_public.scss \
  || fail "D2 policy shell styling missing"
grep -Fq 'max-width: 100%' theme_facodi/static/src/scss/website_public.scss \
  || fail "D2 policy shell must stay within the phone viewport"
grep -Fq 'overflow-x: auto' theme_facodi/static/src/scss/website_public.scss \
  || fail "D2 long-form tables/code must scroll internally"
