import re

from odoo import models


_YOUTUBE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


class SlideChannel(models.Model):
    _inherit = "slide.channel"

    def _facodi_has_explicit_cover(self):
        """Return whether this course has an actual stored editorial cover.

        The binary field itself is authoritative here. Odoo's image route may
        later render a model placeholder when this field is empty, but that
        placeholder must not outrank a representative lesson visual.
        """
        self.ensure_one()
        return bool(self.image_1920)

    def _facodi_catalog_visuals(self):
        """Resolve each course cover from its first published video lesson.

        FACODI course cards intentionally ignore slide.channel.image_1920:
        imported/default course artwork easily becomes a repeated stock image
        across unrelated courses. The first published video is the canonical
        visual source. If that video has a stored Odoo image we use it; for a
        YouTube video we use the stored youtube_id to build the thumbnail URL
        without any provider HTTP request. Courses without a usable first
        video visual fall back to the FACODI placeholder in QWeb.

        Resolution stays non-destructive and bounded: one slide search serves
        the complete channel recordset and nothing is written back.
        """
        visuals = {
            channel.id: {
                "kind": "fallback",
                "slide": False,
                "url": False,
                "alt": channel.name or "",
            }
            for channel in self
        }
        if not self:
            return visuals

        first_videos = {}
        slides = self.env["slide.slide"].search(
            [
                ("channel_id", "in", self.ids),
                ("is_category", "=", False),
                ("website_published", "=", True),
                "|",
                ("slide_category", "=", "video"),
                "&",
                ("source_type", "=", "external"),
                ("video_url", "!=", False),
            ],
            order="channel_id asc, sequence asc, id asc",
        )
        for slide in slides:
            # Some imported FACODI records historically kept slide_category as
            # article even though Odoo correctly recognizes their external URL
            # as YouTube/Vimeo/Drive. Treat the native video metadata as the
            # source of truth for presentation while those legacy records are
            # being normalized.
            is_video = slide.slide_category == "video" or bool(slide.video_source_type)
            if is_video:
                first_videos.setdefault(slide.channel_id.id, slide)

        for channel in self:
            slide = first_videos.get(channel.id)
            if not slide:
                continue

            alt = slide.name or channel.name or ""
            if slide.image_128:
                visuals[channel.id].update(
                    {
                        "kind": "slide",
                        "slide": slide,
                        "url": False,
                        "alt": alt,
                    }
                )
                continue

            youtube_id = slide.youtube_id
            if youtube_id and _YOUTUBE_ID_RE.fullmatch(youtube_id):
                visuals[channel.id].update(
                    {
                        "kind": "youtube",
                        "slide": slide,
                        "url": f"https://i.ytimg.com/vi/{youtube_id}/hqdefault.jpg",
                        "alt": alt,
                    }
                )

        return visuals
