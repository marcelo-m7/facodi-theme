"""Verify permanent editorial redirects and canonical menu reconciliation."""

REDIRECTS = (
    ("/facodi", "/"),
    ("/manifesto", "/sobre"),
    ("/comunidade", "/sobre"),
    ("/parceiros", "/sobre"),
    ("/roadmap", "/sobre#how-it-works"),
    ("/como-contribuir", "/contribuir/recurso"),
    ("/contribuir", "/contribuir/recurso"),
)

website = env["website"].get_current_website()
Page = env["website.page"].with_context(active_test=False)
Menu = env["website.menu"].with_context(active_test=False)
Rewrite = env["website.rewrite"].with_context(active_test=False)

for index, (url_from, url_to) in enumerate(REDIRECTS, start=1):
    page = Page.search([
        ("website_id", "=", website.id),
        ("key", "=", f"theme_facodi.ci_legacy_redirect_{index}"),
    ], limit=1)
    assert page, f"missing legacy page fixture for {url_from}"
    assert not page.is_published, f"{url_from} must be unpublished before 301 fallback"

    menu = Menu.search([
        ("website_id", "=", website.id),
        ("name", "=", f"CI legacy redirect {index}"),
    ], limit=1)
    assert menu, f"missing legacy menu fixture for {url_from}"
    assert menu.url == url_to, f"{url_from} menu must use canonical target {url_to}"

    rewrites = Rewrite.search([
        ("website_id", "=", False),
        ("url_from", "=", url_from),
    ])
    assert len(rewrites) == 1, f"{url_from} must have exactly one website.rewrite"
    rewrite = rewrites[0]
    assert rewrite.active
    assert rewrite.redirect_type == "301"
    assert rewrite.url_to == url_to

assert not Rewrite.search([
    ("website_id", "=", website.id),
    ("url_from", "=", "/roadmaps"),
]), "curriculum /roadmaps must never be redirected"

env.cr.commit()
