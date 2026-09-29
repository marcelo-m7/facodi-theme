import base64
from unittest.mock import patch

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

    def _youtube_slide(self, channel, name, **values):
        values.update(
            {
                "slide_category": "video",
                "source_type": "external",
            }
        )
        with patch(
            "odoo.addons.website_slides.models.slide_slide.SlideSlide._fetch_youtube_metadata",
            return_value=({}, None),
        ):
            return self._slide(channel, name, **values)

    def test_visual_ignores_generic_course_cover_and_uses_first_video(self):
        channel = self._channel("Explicit cover", image_1920=_TINY_PNG)
        video = self._youtube_slide(
            channel,
            "First video",
            url="https://youtu.be/dQw4w9WgXcQ",
            sequence=5,
        )

        visual = channel._facodi_catalog_visuals()[channel.id]

        self.assertEqual(visual["kind"], "youtube")
        self.assertEqual(visual["slide"], video)
        self.assertEqual(
            visual["url"],
            "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
        )

    def test_visual_uses_stored_image_from_first_video_only(self):
        channel = self._channel("Stored first-video image")
        first = self._youtube_slide(
            channel,
            "First video",
            url="https://youtu.be/dQw4w9WgXcQ",
            image_1920=_TINY_PNG,
            sequence=5,
        )
        self._slide(
            channel,
            "Non-video image must not become course cover",
            image_1920=_TINY_PNG,
            sequence=1,
        )

        visual = channel._facodi_catalog_visuals()[channel.id]

        self.assertEqual(visual["kind"], "slide")
        self.assertEqual(visual["slide"], first)
        self.assertFalse(visual["url"])

    def test_visual_accepts_legacy_article_with_native_video_metadata(self):
        channel = self._channel("Legacy imported video")
        with patch(
            "odoo.addons.website_slides.models.slide_slide.SlideSlide._fetch_youtube_metadata",
            return_value=({}, None),
        ):
            slide = self._slide(
                channel,
                "Legacy YouTube lesson",
                slide_category="article",
                source_type="external",
                video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            )
        self.assertEqual(slide.video_source_type, "youtube")
        self.assertEqual(slide.youtube_id, "dQw4w9WgXcQ")

        visual = channel._facodi_catalog_visuals()[channel.id]

        self.assertEqual(visual["kind"], "youtube")
        self.assertEqual(visual["slide"], slide)

    def test_visual_priority_uses_standard_youtube_id_without_http_fetch(self):
        channel = self._channel("YouTube fallback")
        slide = self._youtube_slide(
            channel,
            "YouTube lesson",
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
        self.assertEqual(visuals[third.id]["kind"], "fallback")

    def test_homepage_standard_filter_matches_public_catalogue_in_multilingual_contexts(self):
        website = self.env["website"].get_current_website()
        public_user = self.env.ref("base.public_user")
        en_gb = self.env["res.lang"]._activate_lang("en_GB")
        pt = self.env["res.lang"]._activate_lang("pt_PT")
        website.language_ids |= en_gb | pt

        visible = self._channel(
            "FACODI Homepage Public",
            website_id=website.id,
            visibility="public",
        )
        private = self._channel(
            "FACODI Homepage Members",
            website_id=website.id,
            visibility="members",
            enroll="invite",
        )

        standard_filter = self.env.ref("theme_facodi.dynamic_filter_published_courses")
        self.assertEqual(
            standard_filter.filter_id.domain,
            "[('visibility', 'in', ['public', 'connected'])]",
        )
        self.assertEqual(
            standard_filter.filter_id.sort,
            '["published_date desc"]',
        )

        upstream_filter = self.env.ref(
            "website_slides.dynamic_snippet_latest_courses_filter",
            raise_if_not_found=False,
        )
        if upstream_filter:
            self.assertEqual(
                standard_filter.filter_id.domain,
                upstream_filter.domain,
            )
            self.assertEqual(
                standard_filter.filter_id.sort,
                upstream_filter.sort,
            )

        for lang in ("en_GB", "pt_PT"):
            with self.subTest(lang=lang):
                values = (
                    standard_filter
                    .with_user(public_user)
                    .sudo()
                    .with_context(website_id=website.id, lang=lang)
                    ._prepare_values(
                        limit=16,
                        search_domain=[("id", "in", [visible.id, private.id])],
                    )
                )
                record_ids = {row["_record"].id for row in values}
                self.assertIn(visible.id, record_ids)
                self.assertNotIn(private.id, record_ids)

