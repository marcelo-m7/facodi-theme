from pathlib import Path

JS = Path("theme_facodi/static/src/js/facodi_study_player.js")
MANIFEST = Path("theme_facodi/__manifest__.py")
QWEB = Path("theme_facodi/views/website_slides_player.xml")


def fail(message):
    raise SystemExit(f"FAIL: {message}")


if not JS.is_file():
    fail("facodi_study_player.js missing")

source = JS.read_text(encoding="utf-8")
manifest = MANIFEST.read_text(encoding="utf-8")
qweb = QWEB.read_text(encoding="utf-8")

required = [
    ".facodi-study-player",
    ".o_wslides_fs_toggle_sidebar",
    "o_wslides_fs_sidebar_hidden",
    "data-facodi-study-tab",
    "data-facodi-study-panel",
    "aria-expanded",
    "aria-selected",
    "scrollIntoView",
    "MutationObserver",
    "facodi.study.",
]
for needle in required:
    if needle not in source:
        fail(f"missing progressive-enhancement hook: {needle}")

if "theme_facodi/static/src/js/facodi_study_player.js" not in manifest:
    fail("study player JavaScript missing from frontend assets")

for forbidden in (
    "fetch(",
    ".rpc(",
    "jsonrpc",
    "createClient",
    "supabase",
    "/slides/slide/set_completed",
):
    if forbidden.lower() in source.lower():
        fail(f"presentation JavaScript contains forbidden behavior: {forbidden}")

if "preventDefault()" in source or "stopPropagation()" in source:
    fail("FACODI JavaScript must not intercept native Odoo sidebar navigation/toggle behavior")

if 'data-facodi-index-toggle' not in qweb:
    fail("QWeb must expose the FACODI/native sidebar coordination hook")

print("PASS: FACODI study player JavaScript contract")
