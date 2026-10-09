"""Apply the verified FACODI navigation/editorial snapshot in an Odoo shell.

Usage:
    odoo shell -d facodi
    >>> exec(open('/mnt/addons/theme_facodi/scripts/apply_navigation_editorial.py').read())

Do not use from an ordinary Python process: this script expects the Odoo 'env'.
Snapshot first and review target website. Idempotent upserts, no deletion.
"""
import json
from pathlib import Path

payload = json.loads((Path(globals().get("__file__", "/mnt/addons/theme_facodi/scripts/apply_navigation_editorial.py")).resolve().parents[1] / "data" / "facodi_navigation_editorial.json").read_text(encoding="utf-8"))
website = env["website"].search([("domain", "ilike", "facodi.com")], limit=1)
if not website:
    websites = env["website"].search([])
    if len(websites) == 1:
        website = websites
    else:
        raise RuntimeError("Ambiguous FACODI website: choose website before applying.")
Menu = env["website.menu"]
Page = env["website.page"]
View = env["ir.ui.view"]

root = Menu.search([("website_id", "=", website.id), ("parent_id", "=", False)], limit=1)
if not root:
    raise RuntimeError("Missing website top-level menu; refusing to create an unbound tree.")

def upsert_menu(name, url, parent, sequence, aliases=()):
    domain = [("parent_id", "=", parent.id), ("website_id", "=", website.id)]
    candidates = Menu.search(domain)
    item = candidates.filtered(lambda m: m.name in (name, *aliases) or (url != "#" and m.url == url))[:1]
    vals = {"name": name, "url": url, "parent_id": parent.id, "website_id": website.id, "sequence": sequence, "is_visible": True}
    if item:
        item.write(vals)
    else:
        item = Menu.create(vals)
    return item

for item in payload["menus"]:
    aliases = ("Explore",) if item["name"] == "Learn" else ()
    # Explore may already exist; match exact name first rather than renaming it.
    if item["name"] == "Learn":
        match = Menu.search([("parent_id", "=", root.id), ("name", "=", "Learn")], limit=1)
        if match:
            match.write({"sequence": item["sequence"], "url": "#"})
            parent = match
        else:
            parent = upsert_menu(item["name"], item["url"], root, item["sequence"], aliases=aliases)
    else:
        parent = upsert_menu(item["name"], item["url"], root, item["sequence"])
    for n, (child_name, child_url) in enumerate(item.get("children", []), start=1):
        upsert_menu(child_name, child_url, parent, n * 10, aliases=("Project overview",) if child_name == "The Project" else ("UAlg & FACODI",) if child_name == "Partnerships" else ("Learning resources",) if child_name == "Resources" else ())

about = Menu.search([("parent_id", "=", root.id), ("name", "=", "About")], limit=1)
for url in payload["hidden_header_urls"]:
    Menu.search([("parent_id", "=", about.id), ("url", "=", url)]).unlink()  # website.menu only; never delete legal website.page

for item in payload["pages"]:
    view = View.search([("key", "=", item["view_key"]), ("website_id", "=", website.id)], limit=1)
    if not view:
        view = View.create({"name": item["name"], "key": item["view_key"], "type": "qweb", "mode": "primary", "website_id": website.id, "arch_db": item["arch_db"]})
    elif view.arch_db != item["arch_db"]:
        view.write({"arch_db": item["arch_db"]})
    page = Page.search([("url", "=", item["url"]), ("website_id", "=", website.id)], limit=1)
    if not page:
        Page.create({"name": item["name"], "url": item["url"], "view_id": view.id, "website_id": website.id, "is_published": True})
    elif page.view_id != view:
        raise RuntimeError("Existing page %s references another view; manual reconciliation required." % item["url"])

print("FACODI navigation snapshot applied for website:", website.name)
