"""Seed legacy editor-owned editorial routes before the redirect migration."""

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

for index, (url_from, _url_to) in enumerate(REDIRECTS, start=1):
    key = f"theme_facodi.ci_legacy_redirect_{index}"
    Page.search([("key", "=", key)]).unlink()
    Menu.search([
        ("website_id", "=", website.id),
        ("name", "=", f"CI legacy redirect {index}"),
    ]).unlink()

    arch = f"""
<t t-name="{key}">
    <t t-call="website.layout">
        <div id="wrap">
            <main class="container py-5">
                <h1>Legacy redirect fixture {index}</h1>
                <p>{url_from}</p>
            </main>
        </div>
    </t>
</t>
""".strip()

    page = Page.create({
        "name": f"CI legacy redirect {index}",
        "key": key,
        "type": "qweb",
        "url": url_from,
        "website_id": website.id,
        "is_published": True,
        "arch": arch,
    })
    assert page.is_published
    assert page.url == url_from

    menu = Menu.create({
        "name": f"CI legacy redirect {index}",
        "url": url_from,
        "parent_id": website.menu_id.id,
        "website_id": website.id,
        "sequence": 900 + index,
    })
    assert menu.url == url_from

env.cr.commit()
