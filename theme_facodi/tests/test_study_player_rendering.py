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

    def test_fullscreen_exposes_facodi_study_player_root(self):
        channel = self.env["slide.channel"].create({
            "name": "FACODI Study Player",
            "channel_type": "training",
            "website_id": self.website.id,
            "website_published": True,
            "visibility": "public",
            "enroll": "public",
        })
        slide = self.env["slide.slide"].create({
            "name": "Study lesson",
            "channel_id": channel.id,
            "slide_category": "article",
            "html_content": "<p>Study content</p>",
            "website_published": True,
            "is_preview": True,
        })
        response = self.url_open(f"{slide.website_url}?fullscreen=1")
        self.assertEqual(response.status_code, 200)
        tree = html.fromstring(response.text)
        self.assertTrue(tree.xpath(
            "//*[contains(concat(' ', normalize-space(@class), ' '), ' facodi-study-player ')]"
        ))
        self.assertTrue(tree.xpath(
            "//*[contains(concat(' ', normalize-space(@class), ' '), ' o_wslides_fs_content ')]"
        ))
        self.assertTrue(tree.xpath(
            "//*[contains(concat(' ', normalize-space(@class), ' '), ' o_wslides_fs_sidebar_list_item ')]"
        ))
