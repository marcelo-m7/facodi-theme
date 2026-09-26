from odoo import SUPERUSER_ID, api

REDIRECTS = (
    ("/facodi", "/"),
    ("/manifesto", "/sobre"),
    ("/comunidade", "/sobre"),
    ("/parceiros", "/sobre"),
    ("/roadmap", "/sobre#how-it-works"),
    ("/como-contribuir", "/contribuir/recurso"),
    ("/contribuir", "/contribuir/recurso"),
)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    Page = env["website.page"].with_context(active_test=False)
    Menu = env["website.menu"].with_context(active_test=False)
    Rewrite = env["website.rewrite"].with_context(active_test=False)

    for website in env["website"].search([]):
        for sequence, (url_from, url_to) in enumerate(REDIRECTS, start=1):
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

            rewrite = Rewrite.search([
                ("website_id", "=", website.id),
                ("url_from", "=", url_from),
            ], limit=1)
            values = {
                "name": f"FACODI permanent redirect {url_from}",
                "website_id": website.id,
                "url_from": url_from,
                "url_to": url_to,
                "redirect_type": "301",
                "active": True,
                "sequence": sequence * 10,
            }
            if rewrite:
                rewrite.write(values)
            else:
                Rewrite.create(values)
