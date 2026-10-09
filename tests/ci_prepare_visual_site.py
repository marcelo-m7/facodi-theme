"""Prepare disposable Odoo 19 Website to render FACODI for screenshot tests.

Execute ONLY in CI's temporary database via odoo shell stdin; never production.
This is intentionally not an Odoo module migration or manifest data file.
"""
from pathlib import Path
import re

root = Path("/mnt/facodi-addons")
website = env["website"].sudo().browse(1).exists()
if not website:
    raise RuntimeError("Disposable Website 1 missing")

module = env["ir.module.module"].sudo().search([("name", "=", "theme_facodi")], limit=1)
if not module or module.state != "installed":
    raise RuntimeError("theme_facodi must be installed before visual testing")
website.theme_id = module
module._theme_get_stream_themes().with_context(load_all_views=True, apply_new_theme=True)._theme_load(website)

home = env["ir.ui.view"].sudo().search(
    [("key", "=", "website.homepage"), ("website_id", "in", [False, website.id])],
    limit=1,
)
if not home:
    raise RuntimeError("Cannot locate homepage view")
home.write({
    "arch_db": """<t name="Homepage" t-name="website.homepage">
      <t t-call="website.layout" pageName.f="homepage">
        <t t-call="theme_facodi.new_page_template_sections_facodi_home"/>
      </t>
    </t>"""
})

fixtures = {
    "/about": ("website.facodi_about", "About FACODI", "about_facodi"),
    "/partnerships": ("website.facodi_partnerships", "Partnerships", "partnerships"),
}
for url, (key, name, filename) in fixtures.items():
    text = (root / "theme_facodi/data/website_snapshots" / (filename + ".xml")).read_text()
    text = re.sub(r"^\s*<\?xml[^>]*\?>", "", text, count=1).strip()
    text = re.sub(r"^\s*<!--.*?-->", "", text, count=1, flags=re.DOTALL).strip()
    View = env["ir.ui.view"].sudo()
    Page = env["website.page"].sudo()
    existing = Page.search([("url", "=", url), ("website_id", "=", website.id)], limit=1)
    if existing:
        raise RuntimeError(f"Fixture would overwrite existing page: {url}")
    view = View.create({"name": name, "key": key, "type": "qweb",
                        "arch_db": text, "website_id": website.id, "active": True})
    Page.create({"name": name, "url": url, "view_id": view.id,
                 "website_id": website.id, "is_published": True, "active": True})
    print(f"Visual fixture created: {url}")
env.cr.commit()
print("FACODI theme and visual fixture pages activated in disposable database")
