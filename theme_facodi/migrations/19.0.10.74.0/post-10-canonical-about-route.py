"""Canonicalise the editor-owned FACODI About route to /about.

The Website page itself remains editor-owned. This migration only reconciles the
persisted route, menus and permanent redirects so upgrades cannot restore the
legacy Portuguese slug as the canonical URL.
"""

from odoo import SUPERUSER_ID, api


REDIRECTS = (
    ("/facodi", "/"),
    ("/sobre", "/about"),
    ("/manifesto", "/about"),
    ("/comunidade", "/about"),
    ("/parceiros", "/about"),
    ("/roadmap", "/about#how-it-works"),
    ("/como-contribuir", "/contribuir/recurso"),
    ("/contribuir", "/contribuir/recurso"),
)

_REWRITE_XMLIDS = {
    "/facodi": "theme_facodi.redirect_legacy_facodi_home",
    "/sobre": "theme_facodi.redirect_legacy_sobre",
    "/manifesto": "theme_facodi.redirect_legacy_manifesto",
    "/comunidade": "theme_facodi.redirect_legacy_community",
    "/parceiros": "theme_facodi.redirect_legacy_partners",
    "/roadmap": "theme_facodi.redirect_legacy_project_roadmap",
    "/como-contribuir": "theme_facodi.redirect_legacy_how_to_contribute",
    "/contribuir": "theme_facodi.redirect_legacy_contribution",
}


def _normalise_rewrite(env, Rewrite, sequence, url_from, url_to):
    preferred = env.ref(_REWRITE_XMLIDS[url_from], raise_if_not_found=False)
    matches = Rewrite.search([
        ("website_id", "=", False),
        ("url_from", "=", url_from),
    ])
    rewrite = preferred if preferred and preferred in matches else matches[:1]
    values = {
        "name": f"FACODI permanent redirect {url_from}",
        "website_id": False,
        "url_from": url_from,
        "url_to": url_to,
        "redirect_type": "301",
        "active": True,
        "sequence": sequence * 10,
    }
    if rewrite:
        rewrite.write(values)
    else:
        rewrite = Rewrite.create(values)

    duplicates = matches - rewrite
    if duplicates:
        duplicates.unlink()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    Page = env["website.page"].with_context(active_test=False)
    Menu = env["website.menu"].with_context(active_test=False)
    Rewrite = env["website.rewrite"].with_context(active_test=False)

    for sequence, (url_from, url_to) in enumerate(REDIRECTS, start=1):
        _normalise_rewrite(env, Rewrite, sequence, url_from, url_to)

    for website in env["website"].search([]):
        # Older FACODI redirect migrations may already have rewritten menu
        # sources to the previous canonical About destination. Collapse those
        # persisted targets too so chained upgrades end at the current IA.
        legacy_target_menus = Menu.search([
            ("website_id", "=", website.id),
            ("url", "in", ["/sobre", "/sobre#how-it-works"]),
        ])
        for menu in legacy_target_menus:
            menu.url = (
                "/about#how-it-works"
                if menu.url == "/sobre#how-it-works"
                else "/about"
            )

        about_pages = Page.search([
            ("website_id", "in", [False, website.id]),
            ("url", "=", "/about"),
        ])
        legacy_about_pages = Page.search([
            ("website_id", "in", [False, website.id]),
            ("url", "=", "/sobre"),
        ])

        if not about_pages and legacy_about_pages:
            canonical_page = legacy_about_pages[:1]
            canonical_page.write({"url": "/about"})
            legacy_about_pages = legacy_about_pages - canonical_page

        published_legacy_about = legacy_about_pages.filtered(lambda page: page.is_published)
        if published_legacy_about:
            published_legacy_about.write({"is_published": False})

        for url_from, url_to in REDIRECTS:
            if url_from != "/sobre":
                pages = Page.search([
                    ("website_id", "in", [False, website.id]),
                    ("url", "=", url_from),
                ])
                published_pages = pages.filtered(lambda page: page.is_published)
                if published_pages:
                    published_pages.write({"is_published": False})

            menus = Menu.search([
                ("website_id", "=", website.id),
                ("url", "=", url_from),
            ])
            if menus:
                menus.write({"url": url_to})
