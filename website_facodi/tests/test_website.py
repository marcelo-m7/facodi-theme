from odoo.tests import HttpCase, tagged


@tagged("-at_install", "post_install")
class TestWebsiteFacodi(HttpCase):
    def test_homepage_uses_facodi_layout_class(self):
        response = self.url_open("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("facodi-site", response.text)

    def test_elearning_catalog_still_renders(self):
        response = self.url_open("/slides")
        self.assertEqual(response.status_code, 200)
