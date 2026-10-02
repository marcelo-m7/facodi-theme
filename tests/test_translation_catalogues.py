"""Native catalogue coverage and interpolation safety, without an Odoo server."""
import ast
from collections import Counter
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1] / 'theme_facodi'


def messages(path):
    result = []
    entry = {}
    key = None
    for line in path.read_text().splitlines() + ['']:
        if not line.strip():
            if entry.get('msgid'):
                result.append(entry)
            entry = {}
            key = None
        elif line.startswith(('msgid ', 'msgstr ')):
            key, value = line.split(' ', 1)
            entry[key] = ast.literal_eval(value)
        elif line.startswith('"') and key:
            entry[key] += ast.literal_eval(line)
    return result


class TranslationCatalogueTest(unittest.TestCase):
    def test_supported_catalogues_have_no_empty_or_duplicate_messages(self):
        for locale in ('pt', 'es', 'fr'):
            entries = messages(ROOT / 'i18n' / (locale + '.po'))
            with self.subTest(locale=locale):
                self.assertFalse([e['msgid'] for e in entries if not e.get('msgstr')])
                self.assertEqual(len(entries), len({e['msgid'] for e in entries}))
                template = messages(ROOT / 'i18n' / (ROOT.name + '.pot'))
                self.assertEqual({e['msgid'] for e in entries}, {e['msgid'] for e in template})

    def test_portal_and_contribution_messages_are_translated(self):
        required = {'Profile summary', 'Lesson study tools', '<span>Badges</span>', 'Member since',
                    'Open full contact form', 'Search courses', 'Community courses'}
        for locale in ('pt', 'es', 'fr'):
            translated = {e['msgid']: e['msgstr'] for e in messages(ROOT / 'i18n' / (locale + '.po'))}
            with self.subTest(locale=locale):
                self.assertTrue(required <= translated.keys())
                self.assertTrue(all(translated[t] != t for t in required))

    def test_code_messages_have_native_odoo_translation_flags(self):
        for path in (ROOT / 'i18n').glob('*'):
            for block in re.split(r'\n\s*\n', path.read_text()):
                if re.search(r'^#: code:.*\.py:', block, re.M):
                    with self.subTest(catalogue=path.name, block=block[:100]):
                        self.assertIn('#. odoo-python', block)
                if re.search(r'^#: code:.*\.js:', block, re.M):
                    with self.subTest(catalogue=path.name, block=block[:100]):
                        self.assertIn('#. odoo-javascript', block)

    def test_translation_preserves_interpolation_tokens(self):
        pattern = r'%\([^)]+\)[a-zA-Z]|(?<!%)%[sdf]'
        for locale in ('pt', 'es', 'fr'):
            for entry in messages(ROOT / 'i18n' / (locale + '.po')):
                with self.subTest(locale=locale, source=entry['msgid']):
                    self.assertEqual(Counter(re.findall(pattern, entry['msgid'])),
                                     Counter(re.findall(pattern, entry['msgstr'])))

    def test_profile_uses_english_source_and_localized_date_widget(self):
        source = (ROOT / 'views' / 'website_profile.xml').read_text()
        self.assertIn('>FACODI · Community</span>', source)
        self.assertIn('aria-label="Profile summary"', source)
        self.assertIn('"widget": "date"', source)
        self.assertNotIn('strftime', source)
        self.assertNotIn('>Distintivos</span>', source)

    def test_executable_css_and_code_are_excluded_from_translation(self):
        error = (ROOT / 'views' / 'http_error.xml').read_text()
        exercise = (ROOT / 'views' / 'snippets' / 'components' / 's_facodi_code_exercise.xml').read_text()
        self.assertIn('expr="//style" position="inside" t-translation="off"', error)
        self.assertIn('<pre t-translation="off"><code>def search', exercise)


if __name__ == '__main__':
    unittest.main()
