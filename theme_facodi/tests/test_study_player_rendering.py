from lxml import html

from odoo.tests import HttpCase, tagged


@tagged("-at_install", "post_install")
class TestFacodiStudyPlayerRendering(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        website = cls.env["website"].get_current_website()
        theme = cls.env["ir.module.module"].search(
            [("name", "=", "theme_facodi")], limit=1
        )
        website.theme_id = theme
        theme._theme_get_stream_themes().with_context(
            load_all_views=True, apply_new_theme=True
        )._theme_load(website)
        cls.website = website

    def _course_and_slide(self, course_name, slide_name):
        channel = self.env["slide.channel"].create(
            {
                "name": course_name,
                "channel_type": "training",
                "website_id": self.website.id,
                "website_published": True,
                "visibility": "public",
                "enroll": "public",
            }
        )
        slide = self.env["slide.slide"].create(
            {
                "name": slide_name,
                "channel_id": channel.id,
                "slide_category": "article",
                "html_content": "<p>Study content</p>",
                "website_published": True,
                "is_preview": True,
            }
        )
        return channel, slide

    def _fullscreen_tree(self, slide):
        response = self.url_open(f"{slide.website_url}?fullscreen=1")
        self.assertEqual(response.status_code, 200)
        return html.fromstring(response.text)

    def test_fullscreen_exposes_facodi_study_player_root(self):
        _, slide = self._course_and_slide("FACODI Study Player", "Study lesson")
        tree = self._fullscreen_tree(slide)

        self.assertTrue(
            tree.xpath(
                "//*[contains(concat(' ', normalize-space(@class), ' '), ' facodi-study-player ')]"
            )
        )
        self.assertTrue(
            tree.xpath(
                "//*[contains(concat(' ', normalize-space(@class), ' '), ' facodi-study-player__content ')]"
            )
        )
        self.assertTrue(
            tree.xpath(
                "//*[contains(concat(' ', normalize-space(@class), ' '), ' facodi-study-player__index ')]"
            )
        )
        self.assertTrue(
            tree.xpath(
                "//*[contains(concat(' ', normalize-space(@class), ' '), ' o_wslides_fs_content ')]"
            )
        )
        self.assertTrue(
            tree.xpath(
                "//*[contains(concat(' ', normalize-space(@class), ' '), ' o_wslides_fs_sidebar_list_item ')]"
            )
        )

    def test_study_tools_render_without_fabricated_data(self):
        _, slide = self._course_and_slide("FACODI Study Tools", "Tooling lesson")
        tree = self._fullscreen_tree(slide)

        for panel in ("about", "resources", "notes", "ai"):
            self.assertTrue(tree.xpath(f"//*[@data-facodi-study-panel='{panel}']"))

        resources = tree.xpath("//*[@data-facodi-study-panel='resources']")[0]
        self.assertTrue(
            resources.xpath(
                ".//*[contains(concat(' ', normalize-space(@class), ' '), ' facodi-study-tools__empty ')]"
            )
        )

        notes_text = " ".join(
            tree.xpath("//*[@data-facodi-study-panel='notes']")[0].itertext()
        ).lower()
        self.assertTrue(
            "not saved" in notes_text
            or "not available" in notes_text
            or "coming soon" in notes_text
        )

    def test_ai_actions_are_explicitly_inert(self):
        _, slide = self._course_and_slide("FACODI AI Placeholder", "AI lesson")
        tree = self._fullscreen_tree(slide)

        actions = tree.xpath("//*[@data-facodi-ai-action]")
        self.assertGreaterEqual(len(actions), 4)
        for action in actions:
            self.assertTrue(
                action.get("disabled") is not None
                or action.get("aria-disabled") == "true"
            )

    def test_study_player_contribution_actions_preserve_course_and_lesson_context(self):
        channel, slide = self._course_and_slide(
            "FACODI Contextual Contributions",
            "Contextual lesson",
        )
        tree = self._fullscreen_tree(slide)

        resource = tree.xpath(
            "//a[@data-facodi-study-contribution='resource']/@href"
        )
        correction = tree.xpath(
            "//a[@data-facodi-study-contribution='correction']/@href"
        )
        question = tree.xpath(
            "//a[@data-facodi-study-contribution='question']/@href"
        )
        self.assertEqual(len(resource), 1)
        self.assertEqual(len(correction), 1)
        self.assertEqual(len(question), 1)

        resource_href = resource[0]
        self.assertIn("/submissions/new?type=resource", resource_href)
        self.assertIn(f"course_id={channel.id}", resource_href)
        self.assertIn(f"slide_id={slide.id}", resource_href)
        self.assertIn("source=study_player_resource_cta", resource_href)
        self.assertIn("section=lesson", resource_href)

        correction_href = correction[0]
        self.assertIn("/submissions/new?type=correction", correction_href)
        self.assertIn(f"course_id={channel.id}", correction_href)
        self.assertIn(f"slide_id={slide.id}", correction_href)
        self.assertIn("source=study_player_correction_cta", correction_href)
        self.assertIn("section=lesson", correction_href)

        question_href = question[0]
        self.assertIn("/submissions/new?type=question", question_href)
        self.assertIn(f"course_id={channel.id}", question_href)
        self.assertIn(f"slide_id={slide.id}", question_href)
        self.assertIn("source=study_player_question_cta", question_href)
        self.assertIn("section=lesson", question_href)


    def test_localized_fullscreen_keeps_facodi_and_native_exit_hooks(self):
        _, slide = self._course_and_slide(
            "FACODI Localized Study Player",
            "Localized lesson",
        )
        lang_pt = self.env["res.lang"]._activate_lang("pt_PT")
        lang_en = self.env["res.lang"]._activate_lang("en_GB")\n        self.website.language_ids = lang_en + lang_pt

        response = self.url_open(f"/pt{slide.website_url}?fullscreen=1")
        self.assertEqual(response.status_code, 200)
        tree = html.fromstring(response.text)

        self.assertTrue(
            tree.xpath(
                "//*[contains(concat(' ', normalize-space(@class), ' '), ' facodi-study-player ')]"
            )
        )
        self.assertTrue(
            tree.xpath(
                "//a[contains(concat(' ', normalize-space(@class), ' '), ' o_wslides_fs_exit_fullscreen ')]"
            )
        )

    def test_authenticated_fullscreen_preserves_native_completion_surface(self):
        channel, slide = self._course_and_slide(
            "FACODI Authenticated Study Player",
            "Authenticated lesson",
        )
        self.authenticate("admin", "admin")

        tree = self._fullscreen_tree(slide)

        self.assertTrue(
            tree.xpath(
                "//*[contains(concat(' ', normalize-space(@class), ' '), ' o_wslides_channel_completion_progressbar ')"
                " or contains(concat(' ', normalize-space(@class), ' '), ' o_wslides_channel_completion_completed ')]"
            )
        )
        self.assertTrue(
            tree.xpath(
                f"//a[contains(@href, '/slides/{channel.id}') or contains(@href, '-{channel.id}')]"
            )
        )


    def test_study_player_controls_have_complete_aria_relationships(self):
        _, slide = self._course_and_slide(
            "FACODI Accessible Study Player",
            "Accessible lesson",
        )
        tree = self._fullscreen_tree(slide)

        toggles = tree.xpath(
            "//a[contains(concat(' ', normalize-space(@class), ' '), ' o_wslides_fs_toggle_sidebar ')]"
        )
        self.assertGreaterEqual(len(toggles), 2)
        for toggle in toggles:
            self.assertEqual(toggle.get("aria-controls"), "facodi-study-index")
            self.assertIn(toggle.get("aria-expanded"), {"true", "false"})

        tabs = tree.xpath("//*[@data-facodi-study-tab]")
        self.assertEqual(len(tabs), 4)
        for tab in tabs:
            tab_id = tab.get("id")
            panel_id = tab.get("aria-controls")
            self.assertTrue(tab_id)
            self.assertTrue(panel_id)
            panels = tree.xpath(f"//*[@id='{panel_id}']")
            self.assertEqual(len(panels), 1)
            self.assertEqual(panels[0].get("aria-labelledby"), tab_id)
