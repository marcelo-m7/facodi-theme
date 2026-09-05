from odoo.tests import HttpCase, tagged


@tagged("-at_install", "post_install")
class TestFacodiTheme(HttpCase):
    def test_facodi_snippets_are_registered(self):
        keys = {
            "theme_facodi.s_facodi_hero",
            "theme_facodi.s_facodi_learning_journey",
            "theme_facodi.s_facodi_institutional",
        }
        views = self.env["ir.ui.view"].search([("key", "in", list(keys))])
        self.assertEqual(set(views.mapped("key")), keys)
