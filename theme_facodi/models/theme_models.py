from odoo import models


class ThemeUtils(models.AbstractModel):
    _inherit = "theme.utils"

    @property
    def _header_templates(self):
        return ["theme_facodi.template_header_facodi"] + super()._header_templates

    def _theme_facodi_post_copy(self, mod):
        self.enable_view("theme_facodi.template_header_facodi")
