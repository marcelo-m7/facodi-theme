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
        cls.lang_en_gb = Lang._activate_lang("en_GB")
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
        cls.module._theme_get_stream_themes().with_context(
            load_all_views=True, apply_new_theme=True
        )._theme_load(cls.website)

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
            "Open learning resources, curricular context and community contributions — organised to help people study, discover and share knowledge.",
            response.text,
        )
        self.assertNotIn("Recursos de aprendizagem abertos", response.text)

    def test_standard_website_language_routes_render_theme_translations(self):
        from lxml import html

        cases = {
            "pt": (
                "Recursos de aprendizagem abertos, contexto curricular e contributos da comunidade — organizados para ajudar pessoas a estudar, descobrir e partilhar conhecimento.",
                "Código aberto para aprender em público.",
                "Criado por",
                "Explore os cursos abertos, percursos de aprendizagem e recursos comunitários da FACODI",
            ),
            "es": (
                "Recursos de aprendizaje abiertos, contexto curricular y contribuciones de la comunidad — organizados para ayudar a estudiar, descubrir y compartir conocimiento.",
                "Código abierto para aprender en público.",
                "Creado por",
                "Descubre los cursos abiertos, itinerarios de aprendizaje y recursos comunitarios de FACODI",
            ),
            "fr": (
                "Ressources d’apprentissage ouvertes, contexte curriculaire et contributions de la communauté — organisés pour aider à étudier, découvrir et partager des connaissances.",
                "Code ouvert pour apprendre en public.",
                "Créé par",
                "Découvrez les cours ouverts, parcours d'apprentissage et ressources communautaires de FACODI",
            ),
        }
        for url_code, expected_terms in cases.items():
            with self.subTest(language=url_code):
                response = self.url_open(f"/{url_code}/")
                self.assertEqual(response.status_code, 200)
                for expected in expected_terms[:3]:
                    self.assertIn(expected, response.text)
                description = html.fromstring(response.text).xpath(
                    '//meta[@name="description"]/@content'
                )
                self.assertEqual(len(description), 1)
                self.assertIn(expected_terms[3], description[0])

    def test_native_odoo_canonical_and_hreflang_contract(self):
        from lxml import html
        from urllib.parse import urlparse

        def seo_links(path):
            response = self.url_open(path)
            self.assertEqual(response.status_code, 200)
            tree = html.fromstring(response.text)
            canonical = tree.xpath('//link[@rel="canonical"]/@href')
            alternates = {
                node.get("hreflang"): node.get("href")
                for node in tree.xpath('//link[@rel="alternate"][@hreflang]')
            }
            self.assertEqual(len(canonical), 1)
            self.assertIn("x-default", alternates)
            self.assertGreaterEqual(len(alternates), 5)
            for href in [canonical[0], *alternates.values()]:
                parsed = urlparse(href)
                self.assertTrue(parsed.scheme)
                self.assertTrue(parsed.netloc)
            return canonical[0], alternates

        canonical, alternates = seo_links("/")
        self.assertTrue(canonical.endswith("/"))
        alternate_paths = {urlparse(href).path for href in alternates.values()}
        self.assertIn("/", alternate_paths)
        self.assertIn("/pt", alternate_paths)
        self.assertIn("/es", alternate_paths)
        self.assertIn("/fr", alternate_paths)
        self.assertEqual(urlparse(alternates["x-default"]).path, "/")

        for locale in ("pt", "es", "fr"):
            with self.subTest(locale=locale):
                canonical, alternates = seo_links(f"/{locale}")
                self.assertEqual(urlparse(canonical).path, f"/{locale}")
                self.assertEqual(urlparse(alternates["x-default"]).path, "/")

    def test_native_odoo_sitemap_remains_available(self):
        response = self.url_open("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        content_type = response.headers.get("Content-Type", "")
        self.assertIn("xml", content_type.lower())
        self.assertIn("<loc>", response.text)
        self.assertIn(self.base_url(), response.text)
        self.assertNotIn("/web/login", response.text)

    def test_builder_snippet_copy_uses_native_translations(self):
        hero = self._website_view("theme_facodi.s_facodi_hero")
        expected_by_lang = {
            "en_GB": (
                "Knowledge is everywhere.",
                "Find your next step.",
                "Explore courses",
                "Field notebook",
                "Curricular unit",
                "Start from reviewed academic context.",
                "Course",
                "Keep following the useful thread.",
            ),
            "pt_PT": (
                "Há conhecimento por todo o lado.",
                "Encontra o teu próximo passo.",
                "Explorar cursos",
                "Caderno de campo",
                "Unidade curricular",
                "Começa por contexto académico revisto.",
                "Curso",
                "Continua a seguir o fio útil.",
            ),
            "es_ES": (
                "El conocimiento está en todas partes.",
                "Encuentra tu próximo paso.",
                "Explorar cursos",
                "Cuaderno de campo",
                "Unidad curricular",
                "Empieza desde un contexto académico revisado.",
                "Curso",
                "Sigue el hilo útil.",
            ),
            "fr_FR": (
                "Le savoir est partout.",
                "Trouvez votre prochaine étape.",
                "Explorer les cours",
                "Carnet de terrain",
                "Unité d’enseignement",
                "Commencez par un contexte académique vérifié.",
                "Cours",
                "Continuez à suivre le fil utile.",
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
            "pt_PT": (
                "Escolhe o teu caminho",
                "Explora a aprendizagem da forma que faz sentido para ti.",
                "Cursos",
                "Percursos de aprendizagem",
                "Unidades curriculares",
            ),
            "es_ES": (
                "Elige tu ruta",
                "Explora el aprendizaje de la forma que tenga sentido para ti.",
                "Cursos",
                "Rutas de aprendizaje",
                "Unidades curriculares",
            ),
            "fr_FR": (
                "Choisissez votre parcours",
                "Explorez l’apprentissage de la manière qui vous convient.",
                "Cours",
                "Parcours d’apprentissage",
                "Unités d’enseignement",
            ),
        }
        for lang, expected_terms in expected_by_lang.items():
            with self.subTest(language=lang):
                arch = journey.with_context(lang=lang).arch_db
                for expected in expected_terms:
                    self.assertIn(expected, arch)

    def test_course_dashboard_uses_native_translations(self):
        showcase = self._website_view("theme_facodi.s_facodi_course_showcase")
        expected_by_lang = {
            "pt_PT": (
                "Catálogo de aprendizagem",
                "Percursos de aprendizagem",
                "Unidades curriculares",
                "Cursos",
                "Contribua",
                "Começa por algo útil.",
                "Continuar a explorar",
                "Ver catálogo",
            ),
            "es_ES": (
                "Catálogo de aprendizaje",
                "Rutas de aprendizaje",
                "Unidades curriculares",
                "Cursos",
                "Contribuye",
                "Empieza por algo útil.",
                "Seguir explorando",
                "Ver catálogo",
            ),
            "fr_FR": (
                "Catalogue d’apprentissage",
                "Parcours d’apprentissage",
                "Unités d’enseignement",
                "Cours",
                "Contribuez",
                "Commencez par quelque chose d’utile.",
                "Continuer à explorer",
                "Voir le catalogue",
            ),
        }
        for lang, expected_terms in expected_by_lang.items():
            with self.subTest(language=lang):
                arch = showcase.with_context(lang=lang).arch_db
                for expected in expected_terms:
                    self.assertIn(expected, arch)


    def test_editorial_route_cards_use_native_translations(self):
        routes = self._website_view("theme_facodi.s_facodi_editorial_routes")
        expected_by_lang = {
            "pt_PT": (
                "Mantém alguns separadores abertos.",
                "Destinos editoriais da FACODI",
                "Encontra o próximo caminho útil para explorar",
                "Explora os cursos publicados e segue o fio até aos recursos de aprendizagem.",
                "Traz a pergunta ainda por organizar",
                "Faz perguntas, compara apontamentos e deixa uma resposta útil para quem vier a seguir.",
                "Encontraste uma lacuna? Deixa-a aqui.",
                "Partilha um recurso, uma correção ou uma ideia de colaboração com contexto suficiente para ser útil.",
            ),
            "es_ES": (
                "Mantén unas cuantas pestañas abiertas.",
                "Destinos editoriales de FACODI",
                "Encuentra el próximo hilo útil que explorar",
                "Explora los cursos publicados y sigue el hilo hasta los recursos de aprendizaje.",
                "Trae esa pregunta todavía desordenada",
                "Pregunta, compara apuntes y deja una respuesta útil para quien venga después.",
                "¿Has encontrado un vacío? Déjalo aquí.",
                "Comparte un recurso, una corrección o una idea de colaboración con suficiente contexto para que resulte útil.",
            ),
            "fr_FR": (
                "Gardez quelques onglets ouverts.",
                "Destinations éditoriales de FACODI",
                "Trouvez la prochaine piste utile à explorer",
                "Parcourez les cours publiés et suivez le fil jusqu’aux ressources d’apprentissage.",
                "Apportez la question encore brouillonne",
                "Posez vos questions, comparez vos notes et laissez une réponse utile à la personne suivante.",
                "Vous avez repéré un manque ? Déposez-le ici.",
                "Partagez une ressource, une correction ou une idée de collaboration avec assez de contexte pour qu’elle soit utile.",
            ),
        }
        for lang, expected_terms in expected_by_lang.items():
            with self.subTest(language=lang):
                arch = routes.with_context(lang=lang).arch_db
                for expected in expected_terms:
                    self.assertIn(expected, arch)
