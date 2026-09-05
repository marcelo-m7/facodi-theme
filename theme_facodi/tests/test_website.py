from odoo.tests import HttpCase, tagged


@tagged("-at_install", "post_install")
class TestFacodiTheme(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        website = cls.env["website"].get_current_website()
        theme = cls.env["ir.module.module"].search(
            [("name", "=", "theme_facodi")], limit=1
        )
        cls.assertTrue(theme, "theme_facodi module record must exist")
        website.theme_id = theme
        theme._theme_get_stream_themes().with_context(load_all_views=True)._theme_load(
            website
        )

    def test_facodi_snippets_are_registered(self):
        keys = {
            "theme_facodi.s_facodi_hero",
            "theme_facodi.s_facodi_learning_journey",
            "theme_facodi.s_facodi_institutional",
        }
        template_views = self.env["theme.ir.ui.view"].search(
            [("key", "in", list(keys))]
        )
        self.assertEqual(set(template_views.mapped("key")), keys)

        website_views = self.env["ir.ui.view"].search(
            [("key", "in", list(keys)), ("website_id", "!=", False)]
        )
        self.assertEqual(set(website_views.mapped("key")), keys)

        expected_classes = {
            "theme_facodi.s_facodi_hero": "facodi-hero-board",
            "theme_facodi.s_facodi_learning_journey": "facodi-stat-card",
            "theme_facodi.s_facodi_institutional": "facodi-open-section",
        }
        for view in website_views:
            self.assertIn(expected_classes[view.key], view.arch_db)

    def test_homepage_uses_live_facodi_shell(self):
        response = self.url_open("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("facodi-site", response.text)
        self.assertIn('<meta name="theme-color" content="#142846"', response.text)
        self.assertIn("o_header_standard facodi-header", response.text)
        header_html = response.text.split("<header", 1)[1].split("</header>", 1)[0]
        self.assertIn('data-name="Navbar Logo"', header_html)
        self.assertIn("/web/image/website/", header_html)
        self.assertIn("facodi-wordmark", header_html)
        self.assertIn("facodi-footer", response.text)

    def test_standard_favicon_is_not_replaced(self):
        response = self.url_open("/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("/theme_facodi/static/src/img/favicon.svg", response.text)
        self.assertIn("/web/image/website/", response.text)

    def test_elearning_catalog_renders(self):
        response = self.url_open("/slides")
        self.assertEqual(response.status_code, 200)
        self.assertIn("facodi-site", response.text)
