"""Verify upgrade repair of persisted pre-contract FACODI course showcases."""

from lxml import etree

FIXTURE_KEY = "theme_facodi.ci_legacy_course_showcase"

view = env["ir.ui.view"].with_context(active_test=False).search(
    [("key", "=", FIXTURE_KEY)], limit=1
)
assert view, "legacy course showcase CI fixture is missing after upgrade"
assert "Preserve this editor content" in view.arch_db, "upgrade must preserve editor content"

root = etree.fromstring(view.arch_db.encode())
snippets = root.xpath(".//*[@data-snippet='s_facodi_course_showcase']")
assert len(snippets) == 1, "expected one persisted FACODI course showcase"
snippet = snippets[0]
containers = snippet.xpath(
    ".//*[contains(concat(' ', normalize-space(@class), ' '), ' s_dynamic_snippet_container ')]"
)
contents = snippet.xpath(
    ".//*[contains(concat(' ', normalize-space(@class), ' '), ' s_dynamic_snippet_content ')]"
)
assert containers, "upgrade must restore Odoo's s_dynamic_snippet_container contract"
assert contents, "upgrade must restore Odoo's s_dynamic_snippet_content contract"
assert contents[0].xpath(
    ".//*[contains(concat(' ', normalize-space(@class), ' '), ' dynamic_snippet_template ')]"
), "dynamic render target must remain inside the repaired content container"
