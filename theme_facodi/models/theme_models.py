from odoo import models


FACODI_HOMEPAGE_META_DESCRIPTIONS = {
    "en_US": "Explore FACODI open courses, learning paths and community resources for accessible higher education.",
    "pt_PT": "Explore os cursos abertos, percursos de aprendizagem e recursos comunitários da FACODI para um ensino superior acessível.",
    "es_ES": "Descubre los cursos abiertos, itinerarios de aprendizaje y recursos comunitarios de FACODI para una educación superior accesible.",
    "fr_FR": "Découvrez les cours ouverts, parcours d'apprentissage et ressources communautaires de FACODI pour un enseignement supérieur accessible.",
}


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
            active_languages = self.env["res.lang"].search(
                [
                    ("code", "in", tuple(FACODI_HOMEPAGE_META_DESCRIPTIONS)),
                    ("active", "=", True),
                ]
            )
            for language in active_languages.mapped("code"):
                description = FACODI_HOMEPAGE_META_DESCRIPTIONS[language]
                homepage.with_context(lang=language).website_meta_description = description
