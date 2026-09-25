"""Seed persisted legacy FACODI course-showcase state for upgrade CI."""

FIXTURE_KEY = "theme_facodi.ci_legacy_course_showcase"
CUSTOM_NAV_KEY = "theme_facodi.ci_legacy_course_showcase_custom_nav"

website = env["website"].get_current_website()
View = env["ir.ui.view"].with_context(active_test=False)
View.search([("key", "in", [FIXTURE_KEY, CUSTOM_NAV_KEY])]).unlink()

for code in ("pt_PT", "es_ES", "fr_FR"):
    env["res.lang"]._activate_lang(code)


def legacy_arch(*, nav_title, overview, courses, discover, saved, community, marker, saved_href="/web/login"):
    return f"""
<t t-name="{FIXTURE_KEY}">
    <div id="wrap">
        <section class="s_facodi_course_showcase s_dynamic_snippet s_dynamic o_cc o_cc1"
                 data-snippet="s_facodi_course_showcase"
                 data-template-key="theme_facodi.dynamic_filter_template_slide_channel_facodi_course_card"
                 data-filter-id="1">
            <div class="facodi-dashboard">
                <aside class="facodi-side-nav" aria-label="Learning navigation">
                    <p>{nav_title}</p>
                    <a class="is-active" href="/">{overview}</a>
                    <a href="/slides">{courses}</a>
                    <a href="/website/search">{discover}</a>
                    <a href="{saved_href}">{saved}</a>
                    <a href="/contactus">{community}</a>
                </aside>
                <div class="facodi-dashboard-main">
                    <p class="facodi-ci-editorial-marker">{marker}</p>
                    <div class="dynamic_snippet_template facodi-course-grid"/>
                    <div class="missing_option_warning alert alert-info d-none mt-3">Legacy warning</div>
                </div>
            </div>
        </section>
    </div>
</t>
""".strip()


translations = {
    "en_US": legacy_arch(nav_title="My learning journey", overview="Overview", courses="Courses", discover="Discover", saved="Saved", community="Community", marker="Preserve this editor content"),
    "pt_PT": legacy_arch(nav_title="O meu percurso de aprendizagem", overview="Visão geral", courses="Cursos", discover="Descobrir", saved="Guardados", community="Comunidade", marker="Preservar este conteúdo do editor"),
    "es_ES": legacy_arch(nav_title="Mi recorrido de aprendizaje", overview="Resumen", courses="Cursos", discover="Descubrir", saved="Guardados", community="Comunidad", marker="Conservar este contenido del editor"),
    "fr_FR": legacy_arch(nav_title="Mon parcours d'apprentissage", overview="Vue d'ensemble", courses="Cours", discover="Découvrir", saved="Enregistrés", community="Communauté", marker="Conserver ce contenu de l'éditeur"),
}

view = View.create({
    "name": "FACODI legacy dynamic snippet CI fixture",
    "key": FIXTURE_KEY,
    "type": "qweb",
    "website_id": website.id,
    "arch_db": translations["en_US"],
})
for lang in ("pt_PT", "es_ES", "fr_FR"):
    view.with_context(lang=lang).arch = translations[lang]

assert "s_dynamic_snippet_container" not in view.with_context(lang="en_US").arch_db
assert "s_dynamic_snippet_content" not in view.with_context(lang="en_US").arch_db
assert 'href="/web/login"' in view.with_context(lang="en_US").arch_db

custom_arch = legacy_arch(
    nav_title="My custom learning journey",
    overview="Overview",
    courses="Courses",
    discover="Discover",
    saved="My saved space",
    community="Community",
    marker="Keep this custom navigation untouched",
    saved_href="/my/saved",
).replace(FIXTURE_KEY, CUSTOM_NAV_KEY)

custom_view = View.create({
    "name": "FACODI custom navigation CI fixture",
    "key": CUSTOM_NAV_KEY,
    "type": "qweb",
    "website_id": website.id,
    "arch_db": custom_arch,
})
assert 'href="/my/saved"' in custom_view.arch_db
env.cr.commit()
