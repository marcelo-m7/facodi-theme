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



class WebsiteMenu(models.Model):
    _inherit = "website.menu"

    def _facodi_landing_url(self):
        """Return a canonical destination for a parent menu without mutating it.

        Odoo intentionally computes parent-menu URLs as '#'. FACODI keeps that
        standard data contract and resolves the text-link destination from the
        canonical child routes already present in the menu tree.
        """
        self.ensure_one()
        if not self.child_id:
            clean_url = self._clean_url()
            return clean_url if clean_url and clean_url != "#" else False

        child_urls = set(self.child_id.filtered("is_visible").mapped("url"))
        if "/courses" in child_urls and "/roadmaps" in child_urls:
            return "/explore"
        if "/academic-model" in child_urls or "/about-ualg" in child_urls:
            return "/sobre"
        # Community intentionally remains a disclosure-only parent until
        # FACODI has a dedicated community landing page. A child such as /forum
        # is not silently promoted to a different information-architecture role.
        return False
