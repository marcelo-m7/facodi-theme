"""Read-only contract for editor-owned FACODI homepage localisation."""
from pathlib import Path
import ast
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "theme_facodi/data/website_snapshots/home_curated_courses_2026.xml"
MANIFEST = ROOT / "theme_facodi/__manifest__.py"


class CuratedHomepageSnapshotContract(unittest.TestCase):
    def test_four_language_labels_and_links(self):
        s = PATH.read_text(encoding="utf-8")
        root = ET.fromstring(s)
        self.assertEqual(root.tag, "data")
        for locale in ("pt_PT", "es_ES", "fr_FR"):
            with self.subTest(locale=locale):
                self.assertEqual(s.count("'" + locale + "':"), 18)
        self.assertEqual(s.count(".get(env.lang,"), 18)
        self.assertNotIn("request.lang", s)
        for course in ("44", "46", "47"):
            self.assertIn("-" + course + '"', s)

    def test_snapshot_is_not_installed_as_module_data(self):
        manifest = ast.literal_eval(MANIFEST.read_text(encoding="utf-8"))
        self.assertNotIn(
            "data/website_snapshots/home_curated_courses_2026.xml",
            manifest.get("data", []),
            "Editorial content must remain owned by the Odoo website editor",
        )


if __name__ == "__main__":
    unittest.main()
