"""Read-only contract checks for FACODI SEA-EU Gdańsk landing snapshot.

The snapshot is editorial data exported from the live Odoo DB. These tests
must NEVER create users, publish pages, subscribe people, or import the snapshot.
"""
from pathlib import Path
import ast
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "theme_facodi" / "data" / "website_snapshots" / "sea_eu_2026.xml"
MANIFEST = ROOT / "theme_facodi" / "__manifest__.py"


class SeaEuCampaignSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content = SNAPSHOT.read_text(encoding="utf-8")
        cls.root = ET.fromstring(cls.content)
        cls.manifest = ast.literal_eval(MANIFEST.read_text(encoding="utf-8"))

    def test_live_view_identity(self):
        self.assertEqual(self.root.tag, "t")
        self.assertEqual(self.root.attrib.get("t-name"), "website.facodi_seaeu_2026")

    def test_content_is_bilingual(self):
        self.assertIn("request.lang.code == 'pt_PT'", self.content)
        self.assertIn("Gdańsk foi só o começo.", self.content)
        self.assertIn("Gdańsk was just the start.", self.content)

    def test_standard_routes_and_separate_opt_in(self):
        self.assertIn('href="/web/signup"', self.content)
        self.assertIn('href="/slides"', self.content)
        self.assertIn('href="/privacy-policy"', self.content)
        self.assertIn('href="/terms-of-use"', self.content)
        self.assertIn('t-call="website_mass_mailing.s_newsletter_block_form_template"', self.content)
        self.assertNotIn("/website/form/submit", self.content)
        self.assertNotIn("mailing.contact.create(", self.content)

    def test_academic_and_conference_boundaries(self):
        self.assertIn("não atribui graus", self.content)
        self.assertIn("does not award academic degrees", self.content)
        self.assertIn("https://sea-eu.org/being-sea-eu-conference/", self.content)
        self.assertIn('rel="noopener noreferrer"', self.content)

    def test_basic_responsiveness_accessibility(self):
        self.assertIn("@media(max-width:760px)", self.content)
        self.assertIn("prefers-reduced-motion", self.content)
        self.assertIn("focus-visible", self.content)
        self.assertEqual(self.content.count('class="f-hero"'), 2)

    def test_never_auto_install_editorial_snapshot(self):
        self.assertNotIn(
            "data/website_snapshots/sea_eu_2026.xml",
            self.manifest.get("data", []),
            "Never auto-install or overwrite editor-managed landing pages",
        )


if __name__ == "__main__":
    unittest.main()
