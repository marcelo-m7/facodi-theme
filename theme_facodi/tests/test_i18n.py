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

        Lang = cls.env["res.lang"]
        cls.lang_en = cls.env.ref("base.lang_en")
        cls.lang_pt = Lang._activate_lang("pt_PT")
        cls.lang_es = Lang._activate_lang("es_ES")
        cls.lang_fr = Lang._activate_lang("fr_FR")
        if not (cls.lang_pt and cls.lang_es and cls.lang_fr):
            raise AssertionError("FACODI website languages must be available")

        # Odoo stores theme source views in theme.ir.ui.view and transfers their
        # stored translations to website-specific ir.ui.view copies in _post_copy.
        # Load the native PO catalogues before applying/reloading the theme so the
        # standard theme lifecycle can propagate those translations.
        cls.module._update_translations(["pt_PT", "es_ES", "fr_FR"])
        cls.website.language_ids = (
            cls.lang_en + cls.lang_pt + cls.lang_es + cls.lang_fr
        )
        cls.website.default_lang_id = cls.lang_en
        cls.website.theme_id = cls.module
        cls.module._theme_get_stream_themes().with_context(load_all_views=True)._theme_load(
            cls.website
        )

    def _website_view(self, key):
        view = self.env["ir.ui.view"].search(
            [("key", "=", key), ("website_id", "=", self.website.id)],
            limit=1,
        )
        self.assertTrue(view, f"website view {key} must exist")
        return view

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
            "pt": (
                "Faculdade Comunitária Digital. Ensino superior aberto, colaborativo e acessível.",
                "Código aberto para aprender em público.",
                "Criado por",
            ),
            "es": (
                "Facultad Comunitaria Digital. Educación superior abierta, colaborativa y accesible.",
                "Código abierto para aprender en público.",
                "Creado por",
            ),
            "fr": (
                "Faculté Communautaire Numérique. Enseignement supérieur ouvert, collaboratif et accessible.",
                "Code ouvert pour apprendre en public.",
                "Créé par",
            ),
        }
        for url_code, expected_terms in cases.items():
            with self.subTest(language=url_code):
                response = self.url_open(f"/{url_code}/")
                self.assertEqual(response.status_code, 200)
                for expected in expected_terms:
                    self.assertIn(expected, response.text)

    def test_builder_snippet_copy_uses_native_translations(self):
        hero = self._website_view("theme_facodi.s_facodi_hero")
        expected_by_lang = {
            "en_US": (
                "Learn together with the community",
                "Explore courses",
                "Learning map",
                "Find a course",
            ),
            "pt_PT": (
                "Aprenda em comunidade",
                "Explorar cursos",
                "Mapa de aprendizagem",
                "Encontre um curso",
            ),
            "es_ES": (
                "Aprende en comunidad",
                "Explorar cursos",
                "Mapa de aprendizaje",
                "Encuentra un curso",
            ),
            "fr_FR": (
                "Apprenez avec la communauté",
                "Explorer les cours",
                "Carte d’apprentissage",
                "Trouvez un cours",
            ),
        }
        for lang, expected_terms in expected_by_lang.items():
            with self.subTest(language=lang):
                arch = hero.with_context(lang=lang).arch_db
                for expected in expected_terms:
                    self.assertIn(expected, arch)

    def test_learning_journey_cards_use_native_translations(self):
        journey = self._website_view("theme_facodi.s_facodi_learning_journey")
        expected_by_lang = {
            "pt_PT": ("Como funciona", "Passo 01", "Descubra"),
            "es_ES": ("Cómo funciona", "Paso 01", "Descubre"),
            "fr_FR": ("Comment ça fonctionne", "Étape 01", "Découvrez"),
        }
        for lang, expected_terms in expected_by_lang.items():
            with self.subTest(language=lang):
                arch = journey.with_context(lang=lang).arch_db
                for expected in expected_terms:
                    self.assertIn(expected, arch)
