"""Seed an editor-owned D2 page after the first theme upgrade."""

KEY = "theme_facodi.ci_d2_editorial_page"
MARKER = "D2 editor-owned preservation marker"

website = env["website"].get_current_website()
Page = env["website.page"].with_context(active_test=False)
Page.search([("key", "=", KEY)]).unlink()

arch = f"""
<t t-name="{KEY}">
    <t t-call="website.layout">
        <div id="wrap">
            <section class="facodi-project-story"
                     data-snippet="s_facodi_project_story"
                     data-name="FACODI Project Story">
                <div class="facodi-project-story__main">
                    <p class="facodi-ci-d2-editor-marker">{MARKER}</p>
                    <h2>Editor-owned D2 fixture</h2>
                </div>
            </section>
        </div>
    </t>
</t>
""".strip()

page = Page.create({
    "name": "FACODI D2 editor persistence fixture",
    "key": KEY,
    "type": "qweb",
    "url": "/d2-editorial-ci",
    "website_id": website.id,
    "is_published": True,
    "arch": arch,
})

assert MARKER in page.arch
assert "facodi-project-story" in page.arch
assert 'data-snippet="s_facodi_project_story"' in page.arch
env.cr.commit()
