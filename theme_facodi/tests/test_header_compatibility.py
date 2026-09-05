from odoo.tests import HttpCase, tagged


@tagged("-at_install", "post_install")
class TestFacodiHeaderCompatibility(HttpCase):
    def test_header_survives_existing_website_header_customization(self):
        website = self.env["website"].get_current_website()
        theme = self.env["ir.module.module"].search(
            [("name", "=", "theme_facodi")], limit=1
        )
        self.assertTrue(theme)

        website.theme_id = theme
        theme._theme_get_stream_themes().with_context(
            load_all_views=True, apply_new_theme=True
        )._theme_load(website)

        self.env["ir.ui.view"].create(
            {
                "name": "FACODI legacy header compatibility fixture",
                "type": "qweb",
                "key": "theme_facodi_test.header_without_nav",
                "inherit_id": self.env.ref("website.layout").id,
                "website_id": website.id,
                "priority": 10,
                "arch_db": (
                    '<xpath expr="//header//nav" position="replace">'
                    '<div class="legacy-header-shell"/>'
                    "</xpath>"
                ),
            }
        )

        response = self.url_open("/web/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn("facodi-header", response.text)
