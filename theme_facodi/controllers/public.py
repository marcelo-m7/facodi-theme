from odoo import http
from odoo.http import request


class FacodiThemePublicController(http.Controller):
    @http.route(
        "/visual-direction",
        type="http",
        auth="public",
        website=True,
        sitemap=False,
        methods=["GET"],
    )
    def visual_direction(self, **_kwargs):
        return request.render("theme_facodi.visual_direction_page")
