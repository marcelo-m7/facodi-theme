import base64
from unittest.mock import patch

from lxml import html

from odoo.tests import HttpCase, tagged


_TINY_PNG = base64.b64encode(
    base64.b64decode(
        b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl2nC8AAAAASUVORK5CYII="
    )
)


@tagged("-at_install", "post_install")
class TestFacodiElearningCatalogRendering(HttpCase):
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
        cls.Channel = cls.env["slide.channel"]
        cls.Slide = cls.env["slide.slide"]

    def _channel(self, name, **values):
        values.update(
            {
                "name": name,
                "channel_type": values.get("channel_type", "training"),
                "website_id": self.website.id,
                "website_published": True,
                "visibility": "public",
                "enroll": "public",
            }
        )
        return self.Channel.create(values)

    def _slide(self, channel, name, **values):
        vals = {
            "name": name,
            "channel_id": channel.id,
            "slide_category": values.pop("slide_category", "infographic"),
            "source_type": values.pop("source_type", "local_file"),
            "website_published": True,
            "is_preview": True,
            "sequence": values.pop("sequence", 10),
        }
        vals.update(values)
        return self.Slide.create(vals)

    def test_catalogue_renders_dynamic_visual_sources_and_standard_hooks(self):
        explicit = self._channel("FACODI Explicit Cover", image_1920=_TINY_PNG)

        from_slide = self._channel("FACODI Slide Cover")
        slide_image = self._slide(
            from_slide,
            "Representative visual lesson",
            image_1920=_TINY_PNG,
        )

        from_youtube = self._channel("FACODI YouTube Cover")
        with patch(
            "odoo.addons.website_slides.models.slide_slide.SlideSlide._fetch_youtube_metadata",
            return_value=({}, None),
        ):
            youtube_slide = self._slide(
                from_youtube,
                "Representative YouTube lesson",
                slide_category="video",
                source_type="external",
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            )
        self.assertEqual(youtube_slide.youtube_id, "dQw4w9WgXcQ")

        fallback = self._channel("FACODI No Image")

        response = self.url_open("/slides")
        self.assertEqual(response.status_code, 200)
        tree = html.fromstring(response.text)

        self.assertTrue(tree.xpath("//*[contains(concat(' ', normalize-space(@class), ' '), ' facodi-slides-catalog ')]"))
        self.assertTrue(tree.xpath("//*[contains(concat(' ', normalize-space(@class), ' '), ' facodi-slides-grid ')]"))
        self.assertGreaterEqual(
            len(tree.xpath("//a[contains(concat(' ', normalize-space(@class), ' '), ' o_wslides_course_card ')]")),
            4,
        )

        explicit_media = tree.xpath(
            f"//a[contains(@href, '/slides/{explicit.id}') or contains(@href, '-{explicit.id}') ]//*[contains(@class, 'facodi-course-media')]//img"
        )
        self.assertTrue(explicit_media)
        self.assertIn(f"slide.channel/{explicit.id}/image_", explicit_media[0].get("src", ""))

        slide_media = tree.xpath(
            f"//a[contains(@href, '/slides/{from_slide.id}') or contains(@href, '-{from_slide.id}') ]//*[contains(@class, 'facodi-course-media')]//img"
        )
        self.assertTrue(slide_media)
        self.assertIn(f"slide.slide/{slide_image.id}/image_", slide_media[0].get("src", ""))

        youtube_media = tree.xpath(
            f"//a[contains(@href, '/slides/{from_youtube.id}') or contains(@href, '-{from_youtube.id}') ]//*[contains(@class, 'facodi-course-media')]//img"
        )
        self.assertTrue(youtube_media)
        self.assertEqual(
            youtube_media[0].get("src"),
            "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
        )
        self.assertEqual(youtube_media[0].get("loading"), "lazy")

        fallback_card = tree.xpath(
            f"//a[contains(@href, '/slides/{fallback.id}') or contains(@href, '-{fallback.id}') ]//*[contains(concat(' ', normalize-space(@class), ' '), ' facodi-course-fallback ')]"
        )
        self.assertTrue(fallback_card)
        self.assertFalse(fallback_card[0].xpath(".//img"))

    def test_training_and_documentation_keep_standard_hooks_with_facodi_type_cues(self):
        training = self._channel("FACODI Training Content", channel_type="training")
        with patch(
            "odoo.addons.website_slides.models.slide_slide.SlideSlide._fetch_youtube_metadata",
            return_value=({}, None),
        ):
            self._slide(
                training,
                "Video lesson",
                slide_category="video",
                source_type="external",
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                sequence=1,
            )
        self._slide(
            training,
            "Article lesson",
            slide_category="article",
            html_content="<p>Accessible article content.</p>",
            sequence=2,
        )
        self._slide(
            training,
            "Knowledge check",
            slide_category="quiz",
            sequence=3,
        )

        training_response = self.url_open(training.website_url)
        self.assertEqual(training_response.status_code, 200)
        training_tree = html.fromstring(training_response.text)
        self.assertTrue(
            training_tree.xpath(
                "//*[contains(concat(' ', normalize-space(@class), ' '), ' o_wslides_slides_list_slide ')]"
            )
        )
        self.assertTrue(
            training_tree.xpath(
                "//*[contains(concat(' ', normalize-space(@class), ' '), ' o_wslides_js_slides_list_slide_link ')]"
            )
        )
        self.assertTrue(
            training_tree.xpath(
                "//*[contains(concat(' ', normalize-space(@class), ' '), ' facodi-content-type-video ')]"
            )
        )
        self.assertTrue(
            training_tree.xpath(
                "//*[contains(concat(' ', normalize-space(@class), ' '), ' facodi-content-type-article ')]"
            )
        )
        self.assertTrue(
            training_tree.xpath(
                "//*[contains(concat(' ', normalize-space(@class), ' '), ' facodi-content-type-quiz ')]"
            )
        )

        documentation = self._channel(
            "FACODI Documentation Content",
            channel_type="documentation",
        )
        doc_slide = self._slide(
            documentation,
            "Illustrated reference",
            slide_category="infographic",
            image_1920=_TINY_PNG,
        )
        documentation_response = self.url_open(documentation.website_url)
        self.assertEqual(documentation_response.status_code, 200)
        documentation_tree = html.fromstring(documentation_response.text)
        lesson_cards = documentation_tree.xpath(
            "//*[contains(concat(' ', normalize-space(@class), ' '), ' o_wslides_lesson_card ')]"
        )
        self.assertTrue(lesson_cards)
        self.assertTrue(
            documentation_tree.xpath(
                "//*[contains(concat(' ', normalize-space(@class), ' '), ' facodi-content-type-infographic ')]"
            )
        )
        media = documentation_tree.xpath(
            f"//*[contains(concat(' ', normalize-space(@class), ' '), ' o_wslides_lesson_card ')]//*[contains(@src, 'slide.slide/{doc_slide.id}/image_')]"
        )
        self.assertTrue(media)
