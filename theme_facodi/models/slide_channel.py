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
        """Resolve presentation-only visuals for all courses in ``self``.

        Resolution is deliberately non-destructive and bounded: one slide
        search serves the complete recordset, no provider HTTP request is made,
        and no derived image is written back to either course or lesson data.
        """
        visuals = {}
        uncovered = self.env["slide.channel"]

        for channel in self:
            if channel._facodi_has_explicit_cover():
                visuals[channel.id] = {
                    "kind": "channel",
                    "slide": False,
                    "url": False,
                    "alt": channel.name or "",
                }
            else:
                visuals[channel.id] = {
                    "kind": "fallback",
                    "slide": False,
                    "url": False,
                    "alt": channel.name or "",
                }
                uncovered |= channel

        if not uncovered:
            return visuals

        slides = self.env["slide.slide"].search(
            [
                ("channel_id", "in", uncovered.ids),
                ("is_category", "=", False),
                ("website_published", "=", True),
            ],
            order="sequence asc, id asc",
        )

        image_candidates = {}
        youtube_candidates = {}
        for slide in slides:
            channel_id = slide.channel_id.id

            # Use the small standard image derivative only as a presence check;
            # the QWeb image widget can request an appropriate derivative later.
            if channel_id not in image_candidates and slide.image_128:
                image_candidates[channel_id] = slide

            youtube_id = slide.youtube_id
            if (
                channel_id not in youtube_candidates
                and youtube_id
                and _YOUTUBE_ID_RE.fullmatch(youtube_id)
            ):
                youtube_candidates[channel_id] = slide

        for channel in uncovered:
            image_slide = image_candidates.get(channel.id)
            if image_slide:
                visuals[channel.id].update(
                    {
                        "kind": "slide",
                        "slide": image_slide,
                        "url": False,
                        "alt": image_slide.name or channel.name or "",
                    }
                )
                continue

            youtube_slide = youtube_candidates.get(channel.id)
            if youtube_slide:
                youtube_id = youtube_slide.youtube_id
                visuals[channel.id].update(
                    {
                        "kind": "youtube",
                        "slide": youtube_slide,
                        "url": f"https://i.ytimg.com/vi/{youtube_id}/hqdefault.jpg",
                        "alt": youtube_slide.name or channel.name or "",
                    }
                )

        return visuals
