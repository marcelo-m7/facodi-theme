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

echo "PASS: mobile menu and eLearning touch interaction contract"
