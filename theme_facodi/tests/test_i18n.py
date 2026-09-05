from odoo.tests import HttpCase, tagged


@tagged("-at_install", "post_install")
class TestFacodiThemeTranslations(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env["website"].get_current_website()
        cls.module = cls.env["ir.module.module"].search(
            [("name", "=", "theme_facodi")], limit=1
        )
        if not cls.module:
            raise AssertionError("theme_facodi module record must exist")
        cls.website.theme_id = cls.module
        cls.module._theme_get_stream_themes().with_context(load_all_views=True)._theme_load(
            cls.website
        )

        Lang = cls.env["res.lang"]
        cls.lang_en = cls.env.ref("base.lang_en")
        cls.lang_pt = Lang._activate_lang("pt_PT")
        cls.lang_es = Lang._activate_lang("es_ES")
        cls.lang_fr = Lang._activate_lang("fr_FR")
        if not (cls.lang_pt and cls.lang_es and cls.lang_fr):
            raise AssertionError("FACODI website languages must be available")

        cls.module._update_translations(["pt_PT", "es_ES", "fr_FR"])
        cls.website.language_ids = (
            cls.lang_en + cls.lang_pt + cls.lang_es + cls.lang_fr
        )
        cls.website.default_lang_id = cls.lang_en

    def test_english_is_the_default_website_language(self):
        response = self.url_open("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Digital Community College. Open, collaborative and accessible higher education.",
            response.text,
        )
        self.assertNotIn("Faculdade Comunitária Digital.", response.text)

    def test_standard_website_language_routes_render_theme_translations(self):
        cases = {
            "pt": "Faculdade Comunitária Digital. Ensino superior aberto, colaborativo e acessível.",
            "es": "Facultad Comunitaria Digital. Educación superior abierta, colaborativa y accesible.",
            "fr": "Faculté Communautaire Numérique. Enseignement supérieur ouvert, collaboratif et accessible.",
        }
        for url_code, expected in cases.items():
            with self.subTest(language=url_code):
                response = self.url_open(f"/{url_code}/")
                self.assertEqual(response.status_code, 200)
                self.assertIn(expected, response.text)

    def test_builder_snippet_copy_uses_native_translations(self):
        view = self.env["ir.ui.view"].search(
            [
                ("key", "=", "theme_facodi.s_facodi_hero"),
                ("website_id", "=", self.website.id),
            ],
            limit=1,
        )
        self.assertTrue(view)
        expected_by_lang = {
            "en_US": "Learn together with the community",
            "pt_PT": "Aprenda em comunidade",
            "es_ES": "Aprende en comunidad",
            "fr_FR": "Apprenez avec la communauté",
        }
        for lang, expected in expected_by_lang.items():
            with self.subTest(language=lang):
                self.assertIn(expected, view.with_context(lang=lang).arch_db)
