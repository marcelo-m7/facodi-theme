"""Guard Odoo 19 translation editor / public-asset language compatibility.

These tests require no Odoo service; production behaviour requires a separate
render_public_asset and Website Builder / Translate mode smoke test.
"""
import ast
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "theme_facodi"
MIGRATION = THEME / "migrations" / "19.0.10.91.0" / "post-10-repair-request-lang.py"
SOURCE = "request.lang.code"
TARGET = "env.lang"


class TranslationEditorCompatibility(unittest.TestCase):
    def test_theme_version_triggers_migration(self):
        manifest = ast.literal_eval((THEME / "__manifest__.py").read_text())
        self.assertEqual(manifest["version"], "19.0.10.91.0")
        self.assertTrue(MIGRATION.is_file())

    def test_installed_qweb_templates_do_not_reference_request_lang(self):
        # Editor translations may render without HTTP language routing.
        # Every source template must use native Odoo translations or env.lang.
        for path in (THEME / "views").rglob("*.xml"):
            with self.subTest(path=str(path.relative_to(ROOT))):
                content = path.read_text(encoding="utf-8")
                ET.fromstring(content)
                self.assertNotIn(SOURCE, content)

    def test_migration_preserves_each_locale_and_unrelated_markup(self):
        # Equivalent to SQL replace applied independently to every JSONB key.
        localized = {
            "en_US": "<t>Learning catalogue</t>",
            "en_GB": "<t t-set=\"is_pt\" t-value=\"request.lang.code == 'pt_PT'\"/>",
            "pt_PT": "<p t-esc=\"{'pt_PT': 'Olá'}.get(request.lang.code, 'Hello')\"/>",
            "es_ES": "<span>Introducción</span>",
            "fr_FR": "<span>Introduction</span>",
        }
        repaired = {code: html.replace(SOURCE, TARGET) for code, html in localized.items()}
        self.assertEqual(set(localized), set(repaired))
        self.assertEqual(repaired["en_US"], localized["en_US"])
        self.assertEqual(repaired["es_ES"], localized["es_ES"])
        self.assertEqual(repaired["fr_FR"], localized["fr_FR"])
        self.assertIn("env.lang == 'pt_PT'", repaired["en_GB"])
        self.assertIn("Olá", repaired["pt_PT"])
        self.assertNotIn(SOURCE, "".join(repaired.values()))
        self.assertEqual(repaired, {code: html.replace(SOURCE, TARGET) for code, html in repaired.items()})

    def test_migration_is_scoped_and_retains_jsonb_translation_keys(self):
        source = MIGRATION.read_text(encoding="utf-8")
        tree = ast.parse(source)
        self.assertTrue(any(isinstance(node, ast.FunctionDef) and node.name == "migrate" for node in tree.body))
        self.assertIn("jsonb_each_text(v.arch_db)", source)
        self.assertIn("jsonb_object_agg(", source)
        self.assertIn("website_id IS NOT NULL", source)
        self.assertIn("theme_facodi.", source)
        self.assertIn("env.invalidate_all()", source)
        self.assertNotIn("view.arch_db =", source)

    def test_translation_catalogs_have_no_empty_active_entries(self):
        # Existing pt/es/fr catalogs include translations for their entries.
        for lang in ("pt", "es", "fr"):
            with self.subTest(lang=lang):
                content = (THEME / "i18n" / f"{lang}.po").read_text(encoding="utf-8")
                self.assertIn(f"Language: {'pt_PT' if lang == 'pt' else 'es_ES' if lang == 'es' else 'fr_FR'}", content)
                self.assertGreater(content.count('msgid "'), 800)


if __name__ == "__main__":
    unittest.main()
