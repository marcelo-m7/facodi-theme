"""Move persisted FACODI learning navigation to canonical English URLs.

This migration is intentionally scoped to persisted Website Builder copies of the
FACODI course-showcase navigation. It does not rewrite arbitrary editor-owned
links elsewhere on the Website.
"""

import logging

from lxml import etree

from odoo import SUPERUSER_ID, api


_logger = logging.getLogger(__name__)

_SNIPPET_NAMES = {
    "s_facodi_course_showcase",
    "theme_facodi.s_facodi_course_showcase",
}
_SUPPORTED_LANGS = ("pt_PT", "es_ES", "fr_FR")
_ROUTE_REWRITES = {
    "/slides": "/courses",
    "/unidades-curriculares": "/curricular-units",
}


def _has_class(node, class_name):
    return class_name in node.get("class", "").split()


def _parse_arch(arch):
    parser = etree.XMLParser(remove_blank_text=False)
    return etree.fromstring(arch.encode(), parser)


def _stored_value(translations, lang):
    return translations.get(f"_{lang}", translations.get(lang))


def _repair_arch(arch):
    try:
        root = _parse_arch(arch)
    except (etree.XMLSyntaxError, ValueError, AttributeError):
        return arch, False

    snippets = []
    if root.get("data-snippet") in _SNIPPET_NAMES:
        snippets.append(root)
    snippets.extend(
        node
        for node in root.iterdescendants()
        if node.get("data-snippet") in _SNIPPET_NAMES
    )

    changed = False
    for snippet in snippets:
        for nav in snippet.iterdescendants("nav"):
            if not _has_class(nav, "facodi-catalogue-tabs"):
                continue
            for link in nav.iterchildren("a"):
                href = link.get("href")
                replacement = _ROUTE_REWRITES.get(href)
                if not replacement:
                    continue
                link.set("href", replacement)
                changed = True

    if not changed:
        return arch, False
    return etree.tostring(root, encoding="unicode"), True


def _translation_updates(field, source_arch, translated_archs):
    source_terms = field.get_trans_terms(source_arch)
    compatible = {}
    for lang, arch in translated_archs.items():
        if len(field.get_trans_terms(arch)) != len(source_terms):
            _logger.warning(
                "Skipped FACODI canonical-route translation repair for %s because term structure differs",
                lang,
            )
            continue
        compatible[lang] = arch

    dictionary = field.get_translation_dictionary(source_arch, compatible)
    updates = {}
    for source_term, translated_terms in dictionary.items():
        for lang, translated_term in translated_terms.items():
            updates.setdefault(lang, {})[source_term] = translated_term
    return updates


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    View = env["ir.ui.view"].with_context(active_test=False)
    field = View._fields["arch_db"]

    views = View.with_context(lang="en_GB").search(
        [
            ("website_id", "!=", False),
            ("arch_db", "ilike", "s_facodi_course_showcase"),
        ]
    )

    repaired_views = 0
    repaired_translations = 0
    for view in views:
        stored = field._get_stored_translations(view) or {}
        source_arch = _stored_value(stored, "en_GB")
        if not source_arch:
            continue

        repaired_source, source_changed = _repair_arch(source_arch)
        translated_targets = {}
        translation_changed = False
        for lang in _SUPPORTED_LANGS:
            old_arch = _stored_value(stored, lang)
            if not old_arch:
                continue
            repaired_arch, changed = _repair_arch(old_arch)
            translated_targets[lang] = repaired_arch
            translation_changed |= changed

        if not source_changed and not translation_changed:
            continue

        if source_changed:
            view.with_context(lang="en_GB").arch = repaired_source

        if translated_targets:
            updates = _translation_updates(field, repaired_source, translated_targets)
            if updates:
                view.update_field_translations("arch_db", updates)
                repaired_translations += len(updates)

        repaired_views += 1

    if repaired_views:
        _logger.info(
            "Updated FACODI persisted learning routes in %s Website view(s), %s translated variant(s)",
            repaired_views,
            repaired_translations,
        )
