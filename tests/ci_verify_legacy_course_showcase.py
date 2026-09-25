"""Verify upgrade repair of persisted FACODI course-showcase state."""

import hashlib
import json
from lxml import etree

FIXTURE_KEY = "theme_facodi.ci_legacy_course_showcase"
CUSTOM_NAV_KEY = "theme_facodi.ci_legacy_course_showcase_custom_nav"
SNAPSHOT_KEY = "theme_facodi.ci_legacy_course_showcase_digest"

EXPECTED_MARKERS = {
    "en_US": "Preserve this editor content",
    "pt_PT": "Preservar este conteúdo do editor",
    "es_ES": "Conservar este contenido del editor",
    "fr_FR": "Conserver ce contenu de l'éditeur",
}
EXPECTED_HREFS = ["/roadmaps", "/unidades-curriculares", "/slides", "/contribuir/recurso"]


def has_class(node, class_name):
    return class_name in node.get("class", "").split()


def first_side_nav(arch):
    root = etree.fromstring(arch.encode())
    nodes = [node for node in root.iter() if node.tag == "aside" and has_class(node, "facodi-side-nav")]
    assert len(nodes) == 1, "expected exactly one FACODI side navigation"
    return nodes[0]


def normalized_text(node):
    return " ".join(" ".join(node.itertext()).split())


View = env["ir.ui.view"].with_context(active_test=False)
view = View.search([("key", "=", FIXTURE_KEY)], limit=1)
assert view, "legacy course showcase CI fixture is missing after upgrade"

stored_debug = view._fields["arch_db"]._get_stored_translations(view) or {}
print("FACODI_FIXTURE_DEBUG", {
    "id": view.id,
    "key": view.key,
    "website_id": view.website_id.id,
    "arch_updated": view.arch_updated,
    "arch_prev": view.arch_prev,
    "stored_languages": sorted(stored_debug),
    "stored_values": stored_debug,
})
for debug_lang in ("en_US", "pt_PT", "es_ES", "fr_FR"):
    print(
        "FACODI_FIXTURE_LANG_DEBUG",
        debug_lang,
        view.with_context(lang=debug_lang).arch,
    )

canonical = env.ref("theme_facodi.s_facodi_course_showcase")
for lang, marker in EXPECTED_MARKERS.items():
    arch = view.with_context(lang=lang).arch
    assert marker in arch, f"{lang}: upgrade must preserve editor content"
    side_nav = first_side_nav(arch)
    hrefs = side_nav.xpath("./a/@href")
    assert hrefs == EXPECTED_HREFS, f"{lang}: expected canonical FACODI navigation, got {hrefs}"
    assert "/web/login" not in hrefs
    assert "/website/search" not in hrefs

    canonical_side_nav = first_side_nav(canonical.with_context(lang=lang).arch)
    assert normalized_text(side_nav) == normalized_text(canonical_side_nav), (
        f"{lang}: persisted navigation must use current translated canonical labels"
    )

root = etree.fromstring(view.with_context(lang="en_US").arch.encode())
snippets = root.xpath(".//*[@data-snippet='s_facodi_course_showcase']")
assert len(snippets) == 1, "expected one persisted FACODI course showcase"
snippet = snippets[0]
containers = snippet.xpath(".//*[contains(concat(' ', normalize-space(@class), ' '), ' s_dynamic_snippet_container ')]")
contents = snippet.xpath(".//*[contains(concat(' ', normalize-space(@class), ' '), ' s_dynamic_snippet_content ')]")
assert containers, "upgrade must restore Odoo's s_dynamic_snippet_container contract"
assert contents, "upgrade must restore Odoo's s_dynamic_snippet_content contract"
assert contents[0].xpath(".//*[contains(concat(' ', normalize-space(@class), ' '), ' dynamic_snippet_template ')]"), (
    "dynamic render target must remain inside the repaired content container"
)

custom_view = View.search([("key", "=", CUSTOM_NAV_KEY)], limit=1)
assert custom_view, "custom navigation CI fixture is missing after upgrade"
custom_arch = custom_view.with_context(lang="en_US").arch
custom_side_nav = first_side_nav(custom_arch)
assert custom_side_nav.xpath("./a/@href") == ["/", "/slides", "/website/search", "/my/saved", "/contactus"], (
    "near-match custom navigation must remain untouched"
)
assert "Keep this custom navigation untouched" in custom_arch

snapshot = env["ir.config_parameter"].sudo().get_param(SNAPSHOT_KEY)
if snapshot:
    stored = view._fields["arch_db"]._get_stored_translations(view) or {}
    digest = hashlib.sha256(json.dumps(stored, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    assert digest == snapshot, "second theme upgrade must leave translated Website view unchanged"
