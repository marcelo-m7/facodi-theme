from odoo import models


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
            # website_meta_description is a translated standard Odoo field.
            # Keep one canonical source value and let the native PO-backed field
            # translations provide PT/ES/FR instead of overwriting each locale.
            homepage.with_context(
                lang="en_US"
            ).website_meta_description = _HOMEPAGE_META_DESCRIPTION
