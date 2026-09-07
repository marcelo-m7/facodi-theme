import base64

from odoo.tests import TransactionCase, tagged


_TINY_PNG = base64.b64encode(
    base64.b64decode(
        b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl2nC8AAAAASUVORK5CYII="
    )
)


@tagged("-at_install", "post_install")
class TestFacodiCatalogVisualResolver(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Channel = cls.env["slide.channel"]
        cls.Slide = cls.env["slide.slide"]

    def _channel(self, name, **values):
        values.update(
            {
                "name": name,
                "channel_type": values.get("channel_type", "training"),
                "website_published": values.get("website_published", True),
            }
        )
        return self.Channel.create(values)

    def _slide(self, channel, name, **values):
        vals = {
            "name": name,
            "channel_id": channel.id,
            "slide_category": values.pop("slide_category", "infographic"),
            "source_type": values.pop("source_type", "local_file"),
            "website_published": values.pop("website_published", True),
            "sequence": values.pop("sequence", 10),
        }
        vals.update(values)
        return self.Slide.create(vals)

    def test_visual_priority_prefers_explicit_course_cover(self):
        channel = self._channel("Explicit cover", image_1920=_TINY_PNG)
        self._slide(channel, "Content image", image_1920=_TINY_PNG)

        visual = channel._facodi_catalog_visuals()[channel.id]

        self.assertEqual(visual["kind"], "channel")
        self.assertFalse(visual["slide"])
        self.assertFalse(visual["url"])

    def test_visual_priority_uses_stored_slide_image_before_youtube(self):
        channel = self._channel("Stored slide image")
        youtube = self._slide(
            channel,
            "YouTube first in sequence",
            slide_category="video",
            source_type="external",
            url="https://youtu.be/dQw4w9WgXcQ",
            sequence=5,
        )
        image = self._slide(
            channel,
            "Representative image",
            image_1920=_TINY_PNG,
            sequence=20,
        )

        visual = channel._facodi_catalog_visuals()[channel.id]

        self.assertEqual(visual["kind"], "slide")
        self.assertEqual(visual["slide"], image)
        self.assertNotEqual(visual["slide"], youtube)
        self.assertFalse(visual["url"])

    def test_visual_priority_uses_standard_youtube_id_without_http_fetch(self):
        channel = self._channel("YouTube fallback")
        slide = self._slide(
            channel,
            "YouTube lesson",
            slide_category="video",
            source_type="external",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        )
        self.assertEqual(slide.youtube_id, "dQw4w9WgXcQ")

        visual = channel._facodi_catalog_visuals()[channel.id]

        self.assertEqual(visual["kind"], "youtube")
        self.assertEqual(visual["slide"], slide)
        self.assertEqual(
            visual["url"],
            "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
        )

    def test_visual_falls_back_when_no_usable_content_exists(self):
        channel = self._channel("No imagery")
        visual = channel._facodi_catalog_visuals()[channel.id]

        self.assertEqual(visual["kind"], "fallback")
        self.assertFalse(visual["slide"])
        self.assertFalse(visual["url"])
        self.assertEqual(visual["alt"], "No imagery")

    def test_unpublished_and_category_slides_are_not_visual_candidates(self):
        channel = self._channel("No private leakage")
        unpublished = self._slide(
            channel,
            "Unpublished image",
            image_1920=_TINY_PNG,
            website_published=False,
            sequence=1,
        )
        self._slide(
            channel,
            "Section",
            is_category=True,
            image_1920=_TINY_PNG,
            sequence=2,
        )

        visual = channel._facodi_catalog_visuals()[channel.id]

        self.assertEqual(visual["kind"], "fallback")
        self.assertNotEqual(visual["slide"], unpublished)

    def test_batch_resolver_returns_one_entry_per_channel(self):
        first = self._channel("First")
        second = self._channel("Second")
        third = self._channel("Third", image_1920=_TINY_PNG)
        channels = first | second | third

        visuals = channels._facodi_catalog_visuals()

        self.assertEqual(set(visuals), set(channels.ids))
        self.assertEqual(visuals[third.id]["kind"], "channel")
