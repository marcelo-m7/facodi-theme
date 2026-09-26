import json

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
            "theme_facodi.s_facodi_course_showcase",
            "theme_facodi.s_facodi_academic_areas",
            "theme_facodi.s_facodi_institutional",
            "theme_facodi.s_facodi_intro",
            "theme_facodi.s_facodi_features",
            "theme_facodi.s_facodi_community",
            "theme_facodi.s_facodi_ecosystem",
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
            "theme_facodi.s_facodi_hero": "facodi-hero-study-board",
            "theme_facodi.s_facodi_learning_journey": "facodi-learning-entry-grid",
            "theme_facodi.s_facodi_course_showcase": "facodi-course-grid",
            "theme_facodi.s_facodi_academic_areas": "facodi-area-grid",
            "theme_facodi.s_facodi_institutional": "facodi-institutional-sheet",
            "theme_facodi.s_facodi_intro": "facodi-editorial-intro-sheet",
            "theme_facodi.s_facodi_features": "facodi-learning-steps",
            "theme_facodi.s_facodi_community": "s_facodi_community",
            "theme_facodi.s_facodi_ecosystem": "facodi-ecosystem-grid",
            "theme_facodi.s_facodi_roadmap": "s_facodi_roadmap",
            "theme_facodi.s_facodi_faq": "facodi-faq",
            "theme_facodi.s_facodi_course_cta": "s_facodi_course_cta",
        }
        for view in website_views:
            self.assertIn(expected_classes[view.key], view.arch_db)

        ecosystem = website_views.filtered(
            lambda view: view.key == "theme_facodi.s_facodi_ecosystem"
        )
        self.assertEqual(len(ecosystem), 1)
        self.assertIn("facodi-ecosystem-partners", ecosystem.arch_db)
        self.assertIn('href="https://sea-eu.org/"', ecosystem.arch_db)
        self.assertIn('href="https://corvanis.com/"', ecosystem.arch_db)
        self.assertEqual(
            ecosystem.arch_db.count('target="_blank" rel="noopener noreferrer"'),
            2,
        )

    def test_reusable_campus_paper_blocks_are_native_builder_snippets(self):
        keys = {
            "theme_facodi.s_facodi_highlighter_heading",
            "theme_facodi.s_facodi_paper_card",
            "theme_facodi.s_facodi_sticky_note",
            "theme_facodi.s_facodi_folder_tabs",
            "theme_facodi.s_facodi_filter_pills",
            "theme_facodi.s_facodi_course_card",
            "theme_facodi.s_facodi_study_steps",
            "theme_facodi.s_facodi_cta_sheet",
            "theme_facodi.s_facodi_metadata_row",
            "theme_facodi.s_facodi_highlighter_callout",
            "theme_facodi.s_facodi_project_story",
            "theme_facodi.s_facodi_principles_ledger",
            "theme_facodi.s_facodi_process_timeline",
            "theme_facodi.s_facodi_contribution_board",
            "theme_facodi.s_facodi_bulletin_hero",
            "theme_facodi.s_facodi_editorial_quote",
            "theme_facodi.s_facodi_contact_sheet",
            "theme_facodi.s_facodi_policy_document",
            "theme_facodi.s_facodi_student_id_card",
            "theme_facodi.s_facodi_progress_meter",
            "theme_facodi.s_facodi_uc_progress_card",
            "theme_facodi.s_facodi_notebook_sheet",
            "theme_facodi.s_facodi_module_index",
            "theme_facodi.s_facodi_code_exercise",
            "theme_facodi.s_facodi_forum_postit",
            "theme_facodi.s_facodi_roadmap_metro",
        }
        theme_views = self.env["theme.ir.ui.view"].search([("key", "in", list(keys))])
        self.assertEqual(set(theme_views.mapped("key")), keys)

        website_views = self.env["ir.ui.view"].search(
            [("key", "in", list(keys)), ("website_id", "!=", False)]
        )
        self.assertEqual(set(website_views.mapped("key")), keys)

        expected_classes = {
            "theme_facodi.s_facodi_highlighter_heading": "facodi-highlighter-heading",
            "theme_facodi.s_facodi_paper_card": "facodi-paper-card",
            "theme_facodi.s_facodi_sticky_note": "facodi-sticky-note",
            "theme_facodi.s_facodi_folder_tabs": "facodi-folder-tabs",
            "theme_facodi.s_facodi_filter_pills": "facodi-filter-pills",
            "theme_facodi.s_facodi_course_card": "facodi-static-course-card",
            "theme_facodi.s_facodi_study_steps": "facodi-study-steps",
            "theme_facodi.s_facodi_cta_sheet": "facodi-cta-sheet",
            "theme_facodi.s_facodi_metadata_row": "facodi-metadata-row",
            "theme_facodi.s_facodi_highlighter_callout": "facodi-highlighter-callout",
            "theme_facodi.s_facodi_project_story": "facodi-project-story",
            "theme_facodi.s_facodi_principles_ledger": "facodi-principles-ledger",
            "theme_facodi.s_facodi_process_timeline": "facodi-process-timeline",
            "theme_facodi.s_facodi_contribution_board": "facodi-contribution-board",
            "theme_facodi.s_facodi_bulletin_hero": "facodi-bulletin-hero",
            "theme_facodi.s_facodi_editorial_quote": "facodi-editorial-quote",
            "theme_facodi.s_facodi_contact_sheet": "facodi-contact-sheet",
            "theme_facodi.s_facodi_policy_document": "facodi-policy-document",
            "theme_facodi.s_facodi_student_id_card": "facodi-student-id-card",
            "theme_facodi.s_facodi_progress_meter": "facodi-progress-meter",
            "theme_facodi.s_facodi_uc_progress_card": "facodi-uc-progress-card",
            "theme_facodi.s_facodi_notebook_sheet": "facodi-notebook-sheet",
            "theme_facodi.s_facodi_module_index": "facodi-module-index",
            "theme_facodi.s_facodi_code_exercise": "facodi-code-exercise",
            "theme_facodi.s_facodi_forum_postit": "facodi-forum-postit",
            "theme_facodi.s_facodi_roadmap_metro": "facodi-roadmap-metro",
        }
        for view in website_views:
            self.assertIn(expected_classes[view.key], view.arch_db)
            self.assertNotIn("/web/login", view.arch_db)
            self.assertNotIn("request.env", view.arch_db)
            self.assertNotIn("sudo(", view.arch_db)
            self.assertNotIn("o_not_editable", view.arch_db)
            self.assertNotIn("oe_unremovable", view.arch_db)
            self.assertNotIn("oe_unmovable", view.arch_db)

        website = self.env["website"].get_current_website()
        registry = self.env.ref("website.snippets").with_context(
            website_id=website.id,
            load_all_views=True,
        )
        combined_registry = registry.get_combined_arch()
        for key in keys:
            self.assertIn(f't-snippet="{key}"', combined_registry)

    def test_course_showcase_uses_standard_dynamic_filter(self):
        dynamic_filter = self.env.ref("theme_facodi.dynamic_filter_published_courses")
        self.assertEqual(dynamic_filter.model_name, "slide.channel")
        self.assertEqual(dynamic_filter.limit, 6)
        self.assertEqual(
            dynamic_filter.filter_id.domain,
            '[("website_published", "=", True)]',
        )

        defaults = self.env["website"]._get_snippet_defaults(
            "theme_facodi.s_facodi_course_showcase"
        )
        self.assertEqual(
            defaults["filter_xmlid"],
            "theme_facodi.dynamic_filter_published_courses",
        )
        self.assertEqual(
            defaults["template_key"],
            "theme_facodi.dynamic_filter_template_slide_channel_facodi_course_card",
        )

        showcase = self.env["ir.ui.view"].search(
            [
                ("key", "=", "theme_facodi.s_facodi_course_showcase"),
                ("website_id", "!=", False),
            ],
            limit=1,
        )
        self.assertTrue(showcase)
        self.assertIn("s_dynamic_snippet_container", showcase.arch_db)
        self.assertIn("s_dynamic_snippet_content", showcase.arch_db)
        self.assertIn("dynamic_snippet_template", showcase.arch_db)

    def test_course_showcase_does_not_invent_courses_when_none_are_published(self):
        channels = self.env["slide.channel"].search([("website_published", "=", True)])
        channels.write({"website_published": False})

        showcase = self.env["ir.ui.view"].search(
            [
                ("key", "=", "theme_facodi.s_facodi_course_showcase"),
                ("website_id", "!=", False),
            ],
            limit=1,
        )
        self.assertTrue(showcase)
        self.assertIn("s_dynamic_snippet_content", showcase.arch_db)
        self.assertIn(
            "Course cards appear here when published courses are available.",
            showcase.arch_db,
        )
        self.assertNotIn("Introduction to Algorithms", showcase.arch_db)

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
        self.assertIn("website.template_header_mobile", website_view.arch_db)

    def test_homepage_uses_live_facodi_shell(self):
        from lxml import html

        response = self.url_open("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("facodi-site", response.text)
        self.assertIn('<meta name="theme-color" content="#142846"', response.text)
        tree = html.fromstring(response.text)
        desktop_nav = tree.xpath(
            "//header//nav[contains(concat(' ', normalize-space(@class), ' '), ' facodi-header ')]"
        )
        self.assertEqual(len(desktop_nav), 1)
        desktop_classes = set(desktop_nav[0].get("class", "").split())
        self.assertIn("d-none", desktop_classes)
        self.assertIn("d-lg-block", desktop_classes)
        header_html = response.text.split("<header", 1)[1].split("</header>", 1)[0]
        self.assertIn('data-name="Navbar Logo"', header_html)
        self.assertIn("/web/image/website/", header_html)
        self.assertIn("facodi-wordmark", header_html)
        self.assertTrue(
            tree.xpath(
                "//header//*[contains(concat(' ', normalize-space(@class), ' '), ' o_header_mobile_buttons_wrap ')]"
            ),
            "standard Odoo mobile header must remain rendered",
        )
        self.assertIn("facodi-footer", response.text)
        self.assertNotIn("o_brand_promotion", response.text)
        self.assertNotIn("odoo_logo_tiny.png", response.text)

    def test_campus_paper_hero_snippet_is_available_without_overwriting_homepage(self):
        hero = self.env["ir.ui.view"].search(
            [
                ("key", "=", "theme_facodi.s_facodi_hero"),
                ("website_id", "!=", False),
            ],
            limit=1,
        )
        self.assertTrue(hero)
        self.assertIn("facodi-hero-study-board", hero.arch_db)
        self.assertIn("Learn in public.", hero.arch_db)
        self.assertNotIn("real-time", hero.arch_db.lower())

    def test_learning_entry_snippet_keeps_canonical_routes(self):
        journey = self.env["ir.ui.view"].search(
            [
                ("key", "=", "theme_facodi.s_facodi_learning_journey"),
                ("website_id", "!=", False),
            ],
            limit=1,
        )
        self.assertTrue(journey)
        for route, label in (
            ("/slides", "Courses"),
            ("/roadmaps", "Roadmaps"),
            ("/unidades-curriculares", "Curricular units"),
        ):
            self.assertIn(f'href="{route}"', journey.arch_db)
            self.assertIn(label, journey.arch_db)

    def test_homepage_metadata_uses_public_canonical_and_localized_descriptions(self):
        from lxml import html

        response = self.url_open("/")
        self.assertEqual(response.status_code, 200)
        tree = html.fromstring(response.text)
        descriptions = tree.xpath('//meta[@name="description"]/@content')
        open_graph_descriptions = tree.xpath(
            '//meta[@property="og:description"]/@content'
        )
        canonicals = tree.xpath('//link[@rel="canonical"]/@href')
        self.assertEqual(len(descriptions), 1)
        self.assertEqual(open_graph_descriptions, descriptions)
        self.assertIn("FACODI", descriptions[0])
        self.assertEqual(len(canonicals), 1)
        self.assertTrue(canonicals[0].endswith("/"))
        self.assertNotIn("/facodi", canonicals[0].rstrip("/"))

        website = self.env["website"].get_current_website()
        homepage = self.env["website.page"].search(
            [("url", "=", "/"), ("website_id", "=", website.id)],
            limit=1,
        )
        self.assertTrue(homepage)
        self.assertIn(
            "Explore FACODI open courses",
            homepage.with_context(lang="en_US").website_meta_description,
        )

    def test_campus_paper_shell_keeps_native_header_footer_and_forms(self):
        from lxml import html

        tree = html.fromstring(self.url_open("/").text)
        self.assertTrue(tree.xpath("//header//*[contains(@class, 'facodi-nav-shell')]"))
        self.assertTrue(
            tree.xpath("//*[@id='footer' and contains(@class, 'facodi-footer-campus')]")
        )
        self.assertTrue(
            tree.xpath("//*[@id='footer']//*[contains(@class, 'facodi-footer-note')]")
        )

        login = self.url_open("/web/login")
        self.assertEqual(login.status_code, 200)
        self.assertIn("form-control", login.text)

    def test_standard_favicon_is_not_replaced(self):
        response = self.url_open("/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("/theme_facodi/static/src/img/favicon.svg", response.text)
        self.assertIn("/web/image/website/", response.text)

    def test_elearning_catalog_renders(self):
        from lxml import html

        response = self.url_open("/slides")
        self.assertEqual(response.status_code, 200)
        self.assertIn("facodi-site", response.text)
        tree = html.fromstring(response.text)
        description = tree.xpath('//meta[@name="description"]/@content')
        self.assertEqual(len(description), 1)
        self.assertIn("Browse FACODI open courses", description[0])
        self.assertIn("facodi-learning-catalogue-hero", response.text)
        self.assertIn("facodi-index-tabs--courses", response.text)

    def test_rendered_catalogue_course_card_has_d1_hook(self):
        from lxml import html

        website = self.env["website"].get_current_website()
        channel = self.env["slide.channel"].create(
            {
                "name": "FACODI D1 Card Hook Regression",
                "website_id": website.id,
                "website_published": True,
                "is_published": True,
                "visibility": "public",
                "enroll": "public",
            }
        )
        response = self.url_open("/slides")
        self.assertEqual(response.status_code, 200)
        tree = html.fromstring(response.text)
        cards = tree.xpath(
            f"//a[contains(concat(' ', normalize-space(@class), ' '), "
            f"' facodi-course-record-card ') and @href='{channel.website_url}']"
        )
        self.assertEqual(
            len(cards),
            1,
            "D1 course card hook must survive Odoo's dynamic t-attf-class rendering",
        )

    def test_rendered_course_cover_preserves_custom_style_and_default_signature(self):
        from lxml import html

        website = self.env["website"].get_current_website()
        Channel = self.env["slide.channel"]

        default_channel = Channel.create(
            {
                "name": "FACODI Default Cover Regression",
                "website_id": website.id,
                "website_published": True,
            }
        )
        default_props = json.loads(default_channel.cover_properties)
        default_style = default_props["background_color_style"]
        self.assertIn(
            "linear-gradient(120deg, #875A7B, #78516F)",
            default_style,
        )

        custom_style = (
            "background-color: #123456; "
            "background-image: linear-gradient(45deg, #111111, #222222);"
        )
        custom_props = dict(default_props, background_color_style=custom_style)
        custom_channel = Channel.create(
            {
                "name": "FACODI Custom Cover Regression",
                "website_id": website.id,
                "website_published": True,
                "cover_properties": json.dumps(custom_props),
            }
        )

        for channel, expected_style in (
            (default_channel, default_style),
            (custom_channel, custom_style),
        ):
            response = self.url_open(channel.website_url)
            self.assertEqual(response.status_code, 200)
            tree = html.fromstring(response.text)
            cover = tree.xpath(
                "//div[contains(concat(' ', normalize-space(@class), ' '), "
                "' o_record_cover_container ') "
                f"and @data-res-model='slide.channel' and @data-res-id='{channel.id}']"
            )
            self.assertEqual(len(cover), 1)
            self.assertEqual(cover[0].get("style"), expected_style)

        rendered_default_signature = "linear-gradient(120deg, #875A7B, #78516F)"
        default_response = self.url_open(default_channel.website_url)
        custom_response = self.url_open(custom_channel.website_url)
        self.assertIn(rendered_default_signature, default_response.text)
        self.assertNotIn(
            rendered_default_signature,
            custom_response.text,
            "custom cover must not match the exact default-cover CSS selector",
        )

        self.assertNotEqual(
            custom_channel.cover_properties,
            default_channel.cover_properties,
            "editor-selected cover properties must remain distinct from Odoo defaults",
        )

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
        from lxml import etree, html

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

        rendered_templates = [template["template"] for template in group["templates"]]
        for class_name in (
            "facodi-project-story",
            "facodi-principles-ledger",
            "facodi-process-timeline",
            "facodi-contribution-board",
            "facodi-editorial-quote",
        ):
            self.assertTrue(
                any(class_name in rendered for rendered in rendered_templates),
                f"D2 page-picker output must render {class_name}",
            )

        home_blocks = None
        for template in group["templates"]:
            tree = html.fromstring(template["template"])
            blocks = tree.xpath("//*[@data-snippet]")
            self.assertGreaterEqual(len(blocks), 3, template)
            self.assertTrue(
                all(
                    block.get("data-snippet").startswith("s_facodi_")
                    for block in blocks
                )
            )
            if "facodi-hero-study-board" in template["template"]:
                self.assertIsNone(home_blocks, "FACODI Home template must be unique")
                home_blocks = blocks
                self.assertIn("Learn in public.", template["template"])
                self.assertIn("A good discovery deserves company.", template["template"])
                self.assertIn("Keep the useful thread going.", template["template"])

        self.assertIsNotNone(home_blocks, "FACODI Home must render the learner hero")
        sections_arch = "".join(
            etree.tostring(block, encoding="unicode") for block in home_blocks
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

    def test_d2_does_not_create_fixed_editorial_pages(self):
        website = self.env["website"].get_current_website()
        pages = self.env["website.page"].search(
            [
                ("website_id", "=", website.id),
                ("url", "in", ["/sobre", "/contribuir", "/manifesto", "/parceiros"]),
            ]
        )
        self.assertFalse(
            pages,
            "D2 must provide page-picker compositions without importing fixed Website pages",
        )

    def test_d2_blog_index_and_articles_preserve_native_data(self):
        from lxml import html

        website = self.env["website"].get_current_website()
        blog = self.env["blog.blog"].create(
            {"name": "FACODI D2 Bulletin Fixture", "website_id": website.id}
        )
        tag = self.env["blog.tag"].create({"name": "D2 editorial"})
        sparse = self.env["blog.post"].create(
            {
                "name": "Sparse D2 bulletin post",
                "blog_id": blog.id,
                "content": "<p>Sparse D2 content.</p>",
                "is_published": True,
            }
        )
        custom_cover = (
            '{"background-image": "linear-gradient(45deg, #112233, #445566)", '
            '"resize_class": "o_record_has_cover o_half_screen_height", "opacity": "0"}'
        )
        rich = self.env["blog.post"].create(
            {
                "name": "Rich D2 bulletin post",
                "subtitle": "A real subtitle",
                "blog_id": blog.id,
                "author_id": self.env.user.id,
                "tag_ids": [(4, tag.id)],
                "content": "<h2>Rich section</h2><p>Rich D2 content.</p>",
                "is_published": True,
                "cover_properties": custom_cover,
            }
        )

        index = self.url_open("/blog")
        self.assertEqual(index.status_code, 200)
        tree = html.fromstring(index.text)
        self.assertTrue(tree.xpath("//*[contains(@class, 'facodi-blog-index')]"))
        self.assertTrue(tree.xpath("//*[contains(@class, 'facodi-bulletin-hero')]"))
        self.assertGreaterEqual(
            len(tree.xpath("//article[contains(@class, 'facodi-bulletin-card')]")),
            2,
        )
        self.assertIn(sparse.name, index.text)
        self.assertIn(rich.name, index.text)

        sparse_response = self.url_open(sparse.website_url)
        self.assertEqual(sparse_response.status_code, 200)
        self.assertIn("facodi-blog-article", sparse_response.text)
        self.assertIn("facodi-blog-prose", sparse_response.text)
        self.assertIn("Sparse D2 content.", sparse_response.text)
        sparse_tree = html.fromstring(sparse_response.text)
        self.assertFalse(
            sparse_tree.xpath(
                "//*[@id='o_wblog_post_top']"
                "//*[contains(concat(' ', normalize-space(@class), ' '), "
                "' o_wblog_post_subtitle ')]"
            ),
            "sparse current-post header must not fabricate a subtitle",
        )

        rich_response = self.url_open(rich.website_url)
        self.assertEqual(rich_response.status_code, 200)
        self.assertIn("Rich D2 content.", rich_response.text)
        rich_tree = html.fromstring(rich_response.text)
        rich_subtitles = rich_tree.xpath(
            "//*[@id='o_wblog_post_top']"
            "//*[contains(concat(' ', normalize-space(@class), ' '), "
            "' o_wblog_post_subtitle ')]/text()"
        )
        self.assertIn("A real subtitle", rich_subtitles)
        self.assertIn("D2 editorial", rich_response.text)
        self.assertIn("linear-gradient(45deg, #112233, #445566)", rich_response.text)
        self.assertEqual(rich.cover_properties, custom_cover)

    def test_d2_contact_preserves_native_form(self):
        from lxml import html

        response = self.url_open("/contactus")
        self.assertEqual(response.status_code, 200)
        tree = html.fromstring(response.text)

        self.assertTrue(
            tree.xpath(
                "//*[@id='wrap' and contains(concat(' ', normalize-space(@class), ' '), "
                "' facodi-contact-page ')]"
            )
        )
        self.assertTrue(
            tree.xpath(
                "//*[contains(concat(' ', normalize-space(@class), ' '), "
                "' facodi-contact-form-sheet ')]"
            )
        )
        self.assertTrue(
            tree.xpath(
                "//*[contains(concat(' ', normalize-space(@class), ' '), "
                "' facodi-contact-context ')]"
            )
        )

        forms = tree.xpath("//form[@id='contactus_form']")
        self.assertEqual(len(forms), 1)
        form = forms[0]
        self.assertEqual(form.get("action"), "/website/form/")
        names = set(form.xpath(".//*[@name]/@name"))
        self.assertTrue(
            {"name", "phone", "email_from", "company", "subject", "description"}.issubset(
                names
            )
        )
        self.assertEqual(
            len(
                form.xpath(
                    ".//*[contains(concat(' ', normalize-space(@class), ' '), "
                    "' s_website_form_send ')]"
                )
            ),
            1,
        )

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
        self.assertIn(".facodi-course-grid", compiled)
        self.assertIn(".facodi-area-grid", compiled)
        self.assertIn(".facodi-ecosystem-grid", compiled)
        self.assertIn("--facodi-ink-deep", compiled)
        self.assertIn("--facodi-paper-warm", compiled)
        self.assertIn(".facodi-grid-paper", compiled)
        self.assertIn(".facodi-postit", compiled)
        self.assertIn(".facodi-learning-card", compiled)
        self.assertIn(".facodi-course-catalogue-paper", compiled)
        self.assertIn(".facodi-learning-catalogue-hero", compiled)
        self.assertIn(".facodi-index-tabs--courses", compiled)
        self.assertIn(".facodi-course-record-card", compiled)
        self.assertIn(".facodi-course-study-shell", compiled)
        self.assertIn(".o_wslides_course_card", compiled)
        self.assertIn(".o_wslides_slide_list_category_header", compiled)
        self.assertIn(".o_wslides_js_course_join_link.btn-primary", compiled)
        self.assertIn("var(--facodi-mint-strong)", compiled)
        self.assertIn(".facodi-curriculum-pathway", compiled)
        self.assertIn(".facodi-curriculum-map__unit", compiled)
        self.assertIn(".facodi-coverage-badge", compiled)
        self.assertIn(".facodi-record-card--roadmap", compiled)
        self.assertIn(".facodi-record-card--unit", compiled)
        self.assertIn(".facodi-roadmap-study-path", compiled)
        self.assertIn(".facodi-unit-layout", compiled)
        self.assertIn(".facodi-reference-rail", compiled)
        self.assertIn(".facodi-module-detail", compiled)
        self.assertIn(".facodi-course-alignment-sheet", compiled)
        self.assertIn(".facodi-open-callout", compiled)
        self.assertIn(".facodi-blog-index", compiled)
        self.assertIn(".facodi-bulletin-card", compiled)
        self.assertIn(".facodi-blog-article", compiled)
        self.assertIn(".facodi-blog-prose", compiled)
        self.assertIn(".facodi-project-story", compiled)
        self.assertIn(".facodi-principles-ledger", compiled)
        self.assertIn(".facodi-process-timeline", compiled)
        self.assertIn(".facodi-contribution-board", compiled)
        self.assertIn(".facodi-editorial-quote", compiled)
        self.assertIn(".facodi-contact-sheet", compiled)
        self.assertIn(".facodi-contact-page", compiled)
        self.assertIn(".facodi-contact-form-sheet", compiled)
        self.assertIn(".facodi-policy-document", compiled)
        self.assertIn(".o_cookies_discrete.show", compiled)
        self.assertIn("safe-area-inset-bottom", compiled)
        self.assertIn(
            "linear-gradient(120deg, var(--facodi-paper-warm), var(--facodi-mint))", compiled
        )

    def test_backend_and_print_assets_compile(self):
        for bundle in ("web.assets_web", "web.assets_web_print"):
            response = self.url_open(f"/web/assets/debug/{bundle}.css")
            self.assertEqual(response.status_code, 200, bundle)
            compiled = response.text.lower()
            self.assertNotIn("css_error_message", compiled, bundle)
            self.assertNotIn("sasserror", compiled, bundle)
            self.assertNotIn("function rgb is missing argument", compiled, bundle)

    def test_authenticated_account_has_accessible_name(self):
        from lxml import html

        self.authenticate("admin", "admin")
        tree = html.fromstring(self.url_open("/").text)
        account = tree.xpath(
            "//header//a[@role='button' and @data-bs-toggle='dropdown']"
        )[0]
        self.assertIn(self.env.ref("base.user_admin").name[:23], account.text_content())
