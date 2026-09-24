from odoo import models
from odoo.tools.translate import LazyTranslate


_lt = LazyTranslate(__name__)
_HOMEPAGE_META_DESCRIPTION = _lt(
    "Explore FACODI open courses, learning paths and community resources for accessible higher education."
)


class ThemeUtils(models.AbstractModel):
    _inherit = "theme.utils"

    @property
    def _header_templates(self):
        return ["theme_facodi.template_header_facodi"] + super()._header_templates

    def _theme_facodi_post_copy(self, mod):
        self.enable_view("theme_facodi.template_header_facodi")
        website = self.env["website"].get_current_website()
        homepage = self.env["website.page"].search(
            [("url", "=", "/"), ("website_id", "=", website.id)],
            limit=1,
        )
        if not homepage:
            return

        # website.layout prioritizes website.page SEO fields. Keep the source
        # term bound to theme_facodi with LazyTranslate, then evaluate it for
        # each active Website language through the standard translated field.
        for language in website.language_ids.filtered("active"):
            description = self.with_context(lang=language.code).env._(
                _HOMEPAGE_META_DESCRIPTION
            )
            homepage.with_context(
                lang=language.code
            ).website_meta_description = description
