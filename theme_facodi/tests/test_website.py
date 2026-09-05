from odoo.tests import HttpCase, tagged


@tagged("-at_install", "post_install")
class TestFacodiTheme(HttpCase):
    def test_facodi_snippets_are_registered(self):
        keys = {
            "theme_facodi.s_facodi_hero",
            "theme_facodi.s_facodi_learning_journey",
            "theme_facodi.s_facodi_institutional",
        }
        # Theme modules are loaded as template records first; Odoo copies them
        # to ir.ui.view only when the theme is applied to a website.
        views = self.env["theme.ir.ui.view"].search([("key", "in", list(keys))])
        self.assertEqual(set(views.mapped("key")), keys)

    def test_homepage_uses_facodi_layout_class(self):
        response = self.url_open("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("facodi-site", response.text)

    def test_standard_favicon_is_not_replaced(self):
        response = self.url_open("/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("/theme_facodi/static/src/img/favicon.svg", response.text)

    def test_elearning_catalog_renders(self):
        response = self.url_open("/slides")
        self.assertEqual(response.status_code, 200)
