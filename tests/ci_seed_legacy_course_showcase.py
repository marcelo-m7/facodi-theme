"""Seed persisted legacy FACODI course-showcase state for upgrade CI."""

FIXTURE_KEY = "theme_facodi.ci_legacy_course_showcase"
CUSTOM_NAV_KEY = "theme_facodi.ci_legacy_course_showcase_custom_nav"

website = env["website"].get_current_website()
View = env["ir.ui.view"].with_context(active_test=False)
View.search([("key", "in", [FIXTURE_KEY, CUSTOM_NAV_KEY])]).unlink()

for code in ("pt_PT", "es_ES", "fr_FR"):
    env["res.lang"]._activate_lang(code)


def legacy_arch(*, marker, saved_href="/web/login", custom=False):
    nav_title = "My custom learning journey" if custom else "My learning journey"
    saved = "My saved space" if custom else "Saved"
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
                    <a class="is-active" href="/">Overview</a>
                    <a href="/slides">Courses</a>
                    <a href="/website/search">Discover</a>
                    <a href="{saved_href}">{saved}</a>
                    <a href="/contactus">Community</a>
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


view = View.create({
    "name": "FACODI legacy dynamic snippet CI fixture",
    "key": FIXTURE_KEY,
    "type": "qweb",
    "website_id": website.id,
    "arch_db": legacy_arch(marker="Preserve this editor content"),
})
view.update_field_translations(
    "arch_db",
    {
        "pt_PT": {
            "My learning journey": "O meu percurso de aprendizagem",
            "Overview": "Visão geral",
            "Courses": "Cursos",
            "Discover": "Descobrir",
            "Saved": "Guardados",
            "Community": "Comunidade",
            "Preserve this editor content": "Preservar este conteúdo do editor",
            "Legacy warning": "Aviso legado",
        },
        "es_ES": {
            "My learning journey": "Mi recorrido de aprendizaje",
            "Overview": "Resumen",
            "Courses": "Cursos",
            "Discover": "Descubrir",
            "Saved": "Guardados",
            "Community": "Comunidad",
            "Preserve this editor content": "Conservar este contenido del editor",
            "Legacy warning": "Aviso heredado",
        },
        "fr_FR": {
            "My learning journey": "Mon parcours d'apprentissage",
            "Overview": "Vue d'ensemble",
            "Courses": "Cours",
            "Discover": "Découvrir",
            "Saved": "Enregistrés",
            "Community": "Communauté",
            "Preserve this editor content": "Conserver ce contenu de l'éditeur",
            "Legacy warning": "Avertissement hérité",
        },
    },
)

expected_markers = {
    "en_US": "Preserve this editor content",
    "pt_PT": "Preservar este conteúdo do editor",
    "es_ES": "Conservar este contenido del editor",
    "fr_FR": "Conserver ce contenu de l'éditeur",
}
for lang, marker in expected_markers.items():
    assert marker in view.with_context(lang=lang).arch

assert "s_dynamic_snippet_container" not in view.with_context(lang="en_US").arch_db
assert "s_dynamic_snippet_content" not in view.with_context(lang="en_US").arch_db
assert 'href="/web/login"' in view.with_context(lang="en_US").arch_db

custom_arch = legacy_arch(
    marker="Keep this custom navigation untouched",
    saved_href="/my/saved",
    custom=True,
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
