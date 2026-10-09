#!/usr/bin/env python3
"""Read-only deployment gate for FACODI Website QWeb edits.

Run from repository root:
    python3 tests/test_website_view_sync.py
    python3 tests/test_website_view_sync.py --live-export /path/to/odoo-export.json

Live export format (do NOT commit credentials):
    {"views": [{"id": 5176, "arch_db": "<data>...</data>"}, ...]}

The gate does not write to Odoo and deliberately refuses to claim a sync
if a production export is not provided.
"""
import argparse
import json
import pathlib
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
SNAP = ROOT / "theme_facodi/data/website_snapshots"
FOOTER = ROOT / "theme_facodi/views/customizations.xml"
VIEWS = {
    5176: "facodi_footer", 6144: "partnerships",
    2669: "about_facodi", 6140: "privacy_policy",
    6141: "terms_of_use", 6142: "legal_notice",
    6143: "content_rights",
}
LEGAL = (
    "/privacy-policy", "/terms-of-use", "/legal-notice",
    "/content-rights", "/cookie-policy", "/accessibility",
)
REQUIRED = {
    "/courses", "/roadmaps", "/curricular-units", "/explore/content",
    "/forum", "/blog", "/contact", "/about", "/partnerships",
    "/academic-model", "/infrastructure", "/about-ualg", "/about-marcelo",
    "/my/home", *LEGAL,
}


def die(message):
    print("FAIL:", message, file=sys.stderr)
    raise SystemExit(1)


def normalize(xml):
    """Canonical structural representation ignoring indentation and comments."""
    root = ET.fromstring(xml)
    def walk(node):
        attrs = tuple(sorted(node.attrib.items()))
        value = (node.text or "").strip()
        return (node.tag, attrs, value, tuple(walk(c) for c in node))
    return walk(root)


def check_source():
    try:
        root = ET.parse(FOOTER).getroot()
    except (ET.ParseError, OSError) as exc:
        die(f"theme QWeb is not well-formed XML: {exc}")
    matches = [t for t in root.findall(".//template") if t.get("id") == "facodi_footer"]
    if len(matches) != 1:
        die(f"expected exactly one themed facodi_footer, got {len(matches)}")
    footer = matches[0]
    links = [a.attrib["href"].replace("&amp;", "&") for a in footer.findall(".//li/a") if "href" in a.attrib]
    if len(links) != 21 or len(links) != len(set(links)):
        die(f"footer must have 21 unique explicit navigation links, got {len(links)}")
    missing = REQUIRED.difference(links)
    if missing:
        die(f"required footer destinations missing: {sorted(missing)}")
    text = ET.tostring(footer, encoding="unicode")
    if "request.lang" in text or "pt_PT" in text:
        die("theme footer must use native Odoo gettext, not inline language branching")
    for locale in ("pt", "fr", "es"):
        po = (ROOT / "theme_facodi/i18n" / f"{locale}.po").read_text(encoding="utf-8")
        if "model_terms:theme.ir.ui.view,arch:theme_facodi.facodi_footer" not in po:
            die(f"{locale}.po missing native footer translation references")
        for term in ("Legal & accessibility", "Privacy policy", "Content & copyright",
                     "Learning resources", "Project author"):
            if f'msgid "{term}"' not in po:
                die(f"{locale}.po missing footer string: {term}")
    for id_, name in VIEWS.items():
        path = SNAP / f"{name}.xml"
        try:
            xml = path.read_text(encoding="utf-8")
            ET.fromstring(xml)
        except (ET.ParseError, OSError) as exc:
            die(f"invalid snapshot for view {id_}: {exc}")
    manifest = (ROOT / "theme_facodi/__manifest__.py").read_text(encoding="utf-8")
    if "data/website_snapshots/" in manifest:
        die("do not load DB snapshots from module manifest (would duplicate/overwrite pages)")
    print("PASS: theme footer structure, destinations, translations and 7 valid view snapshots")


def check_live(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        views = {int(r["id"]): r["arch_db"] for r in data["views"]}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        die(f"invalid live export: {exc}")
    if set(VIEWS).difference(views):
        die(f"live export incomplete: missing IDs {sorted(set(VIEWS).difference(views))}")

    drift = []
    for id_, name in VIEWS.items():
        if id_ == 5176:
            continue  # footer must match CURRENT CODE, not the old archived snapshot
        recorded = (SNAP / f"{name}.xml").read_text(encoding="utf-8")
        try:
            if normalize(recorded) != normalize(views[id_]):
                drift.append(f"{id_} ({name})")
        except ET.ParseError as exc:
            die(f"invalid live XML {id_}: {exc}")
    if drift:
        die("LIVE EDITORIAL PAGE DRIFT: " + ", ".join(drift) +
            "; manual reconciliation required")

    try:
        root = ET.parse(FOOTER).getroot()
        source = next(t for t in root.findall(".//template")
                      if t.get("id") == "facodi_footer")
        source_nav = source.find(".//nav")
        live_nav = ET.fromstring(views[5176]).find(".//nav")
        if source_nav is None or live_nav is None:
            die("footer nav absent from source or Odoo export")
        if normalize(ET.tostring(source_nav, encoding="unicode")) != normalize(
                ET.tostring(live_nav, encoding="unicode")):
            die("LIVE FOOTER NOT SYNCED: Odoo website copy differs from the "
                "21-link native-translation source; do not deploy until reconciled")
        # A theme source template is a second independent record when themes
        # are installed; a copied website view alone does not prove ownership.
        theme_views = data.get("theme_templates", [])
        if theme_views:
            original = next((t for t in theme_views
                             if t.get("key") == "theme_facodi.facodi_footer"), None)
            if original is None:
                die("theme.ir.ui.view footer missing from export")
            theme_nav = ET.fromstring(original["arch"]).find(".//nav")
            if theme_nav is None or normalize(ET.tostring(theme_nav, encoding="unicode")) != normalize(
                    ET.tostring(source_nav, encoding="unicode")):
                die("LIVE THEME TEMPLATE NOT SYNCED: source theme template differs")
    except ET.ParseError as exc:
        die(f"malformed live/source footer XML: {exc}")
    print("PASS: live editorial views match snapshots and website/theme footer matches code")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--live-export", type=pathlib.Path)
    args = ap.parse_args()
    check_source()
    if args.live_export:
        check_live(args.live_export)
    else:
        print("WARN: --live-export omitted; this is a static test, NOT a production sync check")
