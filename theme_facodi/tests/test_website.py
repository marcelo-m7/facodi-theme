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
        theme._theme_get_stream_themes().with_context(
            load_all_views=True, apply_new_theme=True
        )._theme_load(website)

    def test_facodi_snippets_are_registered(self):
        keys = {
            "theme_facodi.s_facodi_hero",
            "theme_facodi.s_facodi_learning_journey",
            "theme_facodi.s_facodi_institutional",
            "theme_facodi.s_facodi_intro",
            "theme_facodi.s_facodi_features",
            "theme_facodi.s_facodi_community",
            "theme_facodi.s_facodi_roadmap",
            "theme_facodi.s_facodi_faq",
            "theme_facodi.s_facodi_course_cta",
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
            "theme_facodi.s_facodi_intro": "s_facodi_intro",
            "theme_facodi.s_facodi_features": "facodi-grid",
            "theme_facodi.s_facodi_community": "s_facodi_community",
            "theme_facodi.s_facodi_roadmap": "s_facodi_roadmap",
            "theme_facodi.s_facodi_faq": "facodi-faq",
            "theme_facodi.s_facodi_course_cta": "s_facodi_course_cta",
        }
        for view in website_views:
            self.assertIn(expected_classes[view.key], view.arch_db)

    def test_facodi_header_is_registered_as_native_theme_template(self):
        theme_view = self.env["theme.ir.ui.view"].search(
            [("key", "=", "theme_facodi.template_header_facodi")], limit=1
        )
        self.assertTrue(theme_view)
        website_view = self.env["ir.ui.view"].search(
            [
                ("key", "=", "theme_facodi.template_header_facodi"),
                ("website_id", "!=", False),
            ],
            limit=1,
        )
        self.assertTrue(website_view)
        self.assertIn("website.placeholder_header_brand", website_view.arch_db)
        self.assertIn("website.navbar_nav", website_view.arch_db)

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

    def test_native_menu_preserves_nested_and_external_links(self):
        from lxml import html

        website = self.env["website"].get_current_website()
        Menu = self.env["website.menu"]
        parent = Menu.create(
            {
                "name": "FACODI menu fixture",
                "url": "#",
                "parent_id": website.menu_id.id,
                "website_id": website.id,
            }
        )
        Menu.create(
            {
                "name": "External fixture",
                "url": "https://example.org/facodi",
                "new_window": True,
                "parent_id": parent.id,
                "website_id": website.id,
            }
        )
        Menu.create(
            {
                "name": "Active fixture",
                "url": "/slides",
                "parent_id": website.menu_id.id,
                "website_id": website.id,
            }
        )
        tree = html.fromstring(self.url_open("/slides").text)
        self.assertTrue(
            tree.xpath(
                '//header//a[@data-bs-toggle="dropdown"]/span[text()="FACODI menu fixture"]'
            )
        )
        self.assertTrue(
            tree.xpath(
                '//header//a[@target="_blank"][@href="https://example.org/facodi"]'
            )
        )
        self.assertTrue(
            tree.xpath(
                '//header//a[contains(@class,"active")]/span[text()="Active fixture"]'
            )
        )

    def test_native_templates_render_create_and_preserve_editor_content(self):
        from lxml import html, etree

        website = self.env["website"].get_current_website()
        self.authenticate("admin", "admin")
        response = self.url_open(
            "/website/get_new_page_templates",
            data='{"jsonrpc":"2.0","method":"call","params":{},"id":1}',
            headers={"Content-Type": "application/json"},
        )
        payload = response.json()
        self.assertNotIn("error", payload)
        group = next(group for group in payload["result"] if group["id"] == "facodi")
        self.assertEqual(len(group["templates"]), 10)
        for template in group["templates"]:
            tree = html.fromstring(template["template"])
            sections = tree.xpath("//section[@data-snippet]")
            self.assertEqual(len(sections), 3, template)
            self.assertTrue(
                all(
                    section.get("data-snippet").startswith("s_facodi_")
                    for section in sections
                )
            )
        sections_arch = "".join(
            etree.tostring(section, encoding="unicode") for section in sections
        )
        result = website.with_context(website_id=website.id).new_page(
            name="FACODI editor fixture", sections_arch=sections_arch
        )
        view = self.env["ir.ui.view"].browse(result["view_id"])
        view.arch_db = view.arch_db.replace(
            "</section>", "<p>Editorial preservation fixture</p></section>", 1
        )
        saved = view.arch_db
        module = self.env["ir.module.module"].search([("name", "=", "theme_facodi")])
        module._theme_get_stream_themes().with_context(load_all_views=True)._theme_load(
            website
        )
        self.assertEqual(view.arch_db, saved)
        self.assertIn("Editorial preservation fixture", view.arch_db)

    def test_standard_forms_and_compiled_frontend_assets(self):
        from lxml import html

        for route in ("/contactus", "/web/login"):
            response = self.url_open(route)
            self.assertEqual(response.status_code, 200)
            self.assertIn("facodi-site", response.text)
        tree = html.fromstring(self.url_open("/").text)
        stylesheets = tree.xpath('//link[@rel="stylesheet"]/@href')
        self.assertTrue(stylesheets)
        compiled = ""
        for url in stylesheets:
            if url.startswith("/web/assets/"):
                response = self.url_open(url)
                self.assertEqual(response.status_code, 200)
                self.assertNotIn("could not be compiled", response.text.lower())
                self.assertNotIn("sasserror", response.text.lower())
                self.assertNotIn("css_error_message", response.text)
                compiled += response.text
        self.assertIn(".facodi-site", compiled)
        self.assertIn("#F9FAFB".lower(), compiled.lower())
        self.assertRegex(compiled.lower(), r"background-color:\s*#f9fafb")
        self.assertIn(".facodi-grid", compiled)
        self.assertIn(
            "linear-gradient(120deg, var(--facodi-ink), var(--facodi-blue))", compiled
        )

    def test_authenticated_account_has_accessible_name(self):
        from lxml import html

        self.authenticate("admin", "admin")
        tree = html.fromstring(self.url_open("/").text)
        account = tree.xpath(
            "//header//a[@role='button' and @data-bs-toggle='dropdown']"
        )[0]
        self.assertIn(self.env.ref("base.user_admin").name[:23], account.text_content())
