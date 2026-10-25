"""Read-only contract for editor-owned FACODI homepage localisation."""
from pathlib import Path
import ast
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "theme_facodi/data/website_snapshots/home_curated_courses_2026.xml"
MANIFEST = ROOT / "theme_facodi/__manifest__.py"
PARENT_SOURCE = ROOT / "theme_facodi/views/snippets/s_facodi_course_showcase.xml"
PREPARER = ROOT / "scripts/prepare_home_curated_snapshot.py"


class CuratedHomepageSnapshotContract(unittest.TestCase):
    def prepare(self, parent, output):
        return subprocess.run(
            [sys.executable, str(PREPARER), "--parent", str(parent),
             "--output", str(output)],
            capture_output=True, text=True, check=False,
        )

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

    def test_portable_recovery_matches_current_source_without_changing_archive(self):
        original = PATH.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "candidate.xml"
            result = self.prepare(PARENT_SOURCE, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            candidate = etree.parse(str(output))
            selector = candidate.find("xpath").get("expr")
            targets = etree.parse(str(PARENT_SOURCE)).xpath(selector)
            self.assertEqual(len(targets), 1)
            self.assertEqual(targets[0].tag, "div")
            self.assertEqual(output.read_text(encoding="utf-8").count(".get(env.lang,"), 18)
        self.assertEqual(PATH.read_bytes(), original)

    def test_portable_recovery_also_matches_legacy_live_section(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory) / "installed-parent.xml"
            output = Path(directory) / "candidate.xml"
            parent.write_text(
                '<template><section class="s_dynamic_snippet_content o_not_editable"/></template>',
                encoding="utf-8",
            )
            result = self.prepare(parent, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            original_selector = etree.parse(str(PATH)).find("xpath").get("expr")
            self.assertEqual(len(etree.parse(str(parent)).xpath(original_selector)), 1)
            self.assertEqual(len(etree.parse(str(PARENT_SOURCE)).xpath(original_selector)), 0)
            selector = etree.parse(str(output)).find("xpath").get("expr")
            self.assertEqual(len(etree.parse(str(parent)).xpath(selector)), 1)

    def test_portable_recovery_fails_closed_on_missing_or_ambiguous_target(self):
        for markup in (
            '<template><section class="unrelated"/></template>',
            '<template><div class="s_dynamic_snippet_content"/>'
            '<section class="s_dynamic_snippet_content"/></template>',
        ):
            with self.subTest(markup=markup), tempfile.TemporaryDirectory() as directory:
                parent = Path(directory) / "parent.xml"
                output = Path(directory) / "candidate.xml"
                parent.write_text(markup, encoding="utf-8")
                result = self.prepare(parent, output)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("exactly one", result.stderr)
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
