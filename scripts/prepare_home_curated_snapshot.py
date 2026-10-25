#!/usr/bin/env python3
"""Prepare an editor-owned homepage snapshot for manual recovery, offline.

The archive intentionally preserves the exact XPath stored in Odoo on
2026-10-22. That installed parent used a ``section``; the current theme
source uses a ``div``. Generate a portable *candidate* against an explicit
parent view without changing the archived snapshot or an Odoo database.
"""

import argparse
import copy
import sys
from pathlib import Path

from lxml import etree


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "theme_facodi/data/website_snapshots/home_curated_courses_2026.xml"
TARGET_CLASS = "s_dynamic_snippet_content"
PORTABLE_XPATH = (
    "//*[contains(concat(' ', normalize-space(@class), ' '), "
    "' s_dynamic_snippet_content ')]"
)


def prepare_candidate(snapshot: Path, parent: Path) -> bytes:
    """Return recovery XML only when the requested parent has one target."""
    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    archived = etree.parse(str(snapshot), parser)
    root = archived.getroot()
    instructions = root.xpath("./xpath") if root.tag == "data" else []
    if len(instructions) != 1 or instructions[0].get("position") != "before":
        raise ValueError("expected one archived before-position XPath")
    if TARGET_CLASS not in (instructions[0].get("expr") or ""):
        raise ValueError("archive is not the expected course-showcase snapshot")

    installed_parent = etree.parse(str(parent), parser)
    matches = installed_parent.xpath(PORTABLE_XPATH)
    if len(matches) != 1:
        raise ValueError(
            f"expected exactly one {TARGET_CLASS} target in parent; found {len(matches)}"
        )

    candidate = copy.deepcopy(root)
    candidate.xpath("./xpath")[0].set("expr", PORTABLE_XPATH)
    return etree.tostring(
        candidate, encoding="utf-8", xml_declaration=True, pretty_print=True
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", type=Path, required=True,
                        help="Explicit exported parent ir.ui.view arch_db or theme XML")
    parser.add_argument("--output", type=Path, required=True,
                        help="New local candidate file; will not overwrite an existing file")
    args = parser.parse_args()
    try:
        if args.output.resolve() == ARCHIVE.resolve():
            raise ValueError("refusing to overwrite the historical archive")
        candidate = prepare_candidate(ARCHIVE, args.parent)
        with args.output.open("xb") as destination:
            destination.write(candidate)
    except (OSError, ValueError, etree.XMLSyntaxError, etree.XPathError) as exc:
        print(f"Recovery candidate not created: {exc}", file=sys.stderr)
        return 1
    print("Prepared local candidate only. Validate in staging before any manual Odoo import.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
