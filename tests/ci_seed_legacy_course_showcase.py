"""Seed a persisted pre-contract FACODI course showcase for upgrade CI."""

FIXTURE_KEY = "theme_facodi.ci_legacy_course_showcase"

website = env["website"].get_current_website()
View = env["ir.ui.view"].with_context(active_test=False)
View.search([("key", "=", FIXTURE_KEY)]).unlink()

legacy_arch = """
<t t-name="theme_facodi.ci_legacy_course_showcase">
    <div id="wrap">
        <section class="s_facodi_course_showcase s_dynamic_snippet s_dynamic o_cc o_cc1"
                 data-snippet="s_facodi_course_showcase"
                 data-template-key="theme_facodi.dynamic_filter_template_slide_channel_facodi_course_card"
                 data-filter-id="1">
            <div class="facodi-dashboard">
                <div class="facodi-dashboard-main">
                    <p class="facodi-ci-editorial-marker">Preserve this editor content</p>
                    <div class="dynamic_snippet_template facodi-course-grid"/>
                    <div class="missing_option_warning alert alert-info d-none mt-3">
                        Legacy warning
                    </div>
                </div>
            </div>
        </section>
    </div>
</t>
""".strip()

view = View.create(
    {
        "name": "FACODI legacy dynamic snippet CI fixture",
        "key": FIXTURE_KEY,
        "type": "qweb",
        "website_id": website.id,
        "arch_db": legacy_arch,
    }
)
assert "s_dynamic_snippet_container" not in view.arch_db
assert "s_dynamic_snippet_content" not in view.arch_db
env.cr.commit()
