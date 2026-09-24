from odoo import models
from odoo.tools.translate import get_translation


_HOMEPAGE_META_DESCRIPTION = (
    "Explore FACODI open courses, learning paths and community resources for "
    "accessible higher education."
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
            [("url", "=", "/"), ("website_id", "=", website.id)], limit=1
        )
        if homepage:
            for language in website.language_ids.filtered("active"):
                description = get_translation(
                    "theme_facodi",
                    language.code,
                    _HOMEPAGE_META_DESCRIPTION,
                )
                homepage.with_context(
                    lang=language.code
                ).website_meta_description = description
