"""Reconcile only the known stale FACODI course-showcase navigation."""

import copy
import logging
from collections import defaultdict

from lxml import etree

from odoo import SUPERUSER_ID, api


_logger = logging.getLogger(__name__)

_SNIPPET_NAMES = {
    "s_facodi_course_showcase",
    "theme_facodi.s_facodi_course_showcase",
}
_LEGACY_HREFS = [
    "/",
    "/slides",
    "/website/search",
    "/web/login",
    "/contactus",
]
_SUPPORTED_LANGS = ("pt_PT", "es_ES", "fr_FR")
_CANONICAL_VIEW_XMLID = "theme_facodi.s_facodi_course_showcase"


def _has_class(node, class_name):
    return class_name in node.get("class", "").split()


def _parse_arch(arch):
    parser = etree.XMLParser(remove_blank_text=False)
    return etree.fromstring(arch.encode(), parser)


def _side_navs(root):
    return [
        node
        for node in root.iter()
        if node.tag == "aside" and _has_class(node, "facodi-side-nav")
    ]


def _canonical_side_nav(arch):
    root = _parse_arch(arch)
    nodes = _side_navs(root)
    if len(nodes) != 1:
        raise RuntimeError(
            "FACODI canonical course-showcase template must contain exactly one side navigation"
        )
    return nodes[0]


def _is_exact_legacy_nav(node):
    children = [child for child in node if isinstance(child.tag, str)]
    if [child.tag for child in children] != ["p", "a", "a", "a", "a", "a"]:
        return False
    return [child.get("href") for child in children[1:]] == _LEGACY_HREFS


def _replacement_side_nav(legacy, canonical):
    replacement = copy.deepcopy(canonical)

    canonical_classes = replacement.get("class", "").split()
    for class_name in legacy.get("class", "").split():
        if class_name not in canonical_classes:
            canonical_classes.append(class_name)
    if canonical_classes:
        replacement.set("class", " ".join(canonical_classes))

    for name, value in legacy.attrib.items():
        if name == "id" or name == "style" or name.startswith("data-"):
            replacement.set(name, value)

    replacement.tail = legacy.tail
    return replacement


def _repair_arch(arch, canonical_arch):
    try:
        root = _parse_arch(arch)
    except (etree.XMLSyntaxError, ValueError, AttributeError):
        return arch, False

    canonical_nav = _canonical_side_nav(canonical_arch)
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
        candidates = [
            node
            for node in _side_navs(snippet)
            if _is_exact_legacy_nav(node)
        ]
        for legacy_nav in candidates:
            parent = legacy_nav.getparent()
            if parent is None:
                continue
            parent.replace(
                legacy_nav,
                _replacement_side_nav(legacy_nav, canonical_nav),
            )
            changed = True

    if not changed:
        return arch, False
    return etree.tostring(root, encoding="unicode"), True


def _stored_value(translations, lang):
    return translations.get(f"_{lang}", translations.get(lang))


def _translation_updates(field, source_arch, translated_archs):
    source_terms = field.get_trans_terms(source_arch)
    compatible = {}
    for lang, arch in translated_archs.items():
        if len(field.get_trans_terms(arch)) != len(source_terms):
            _logger.warning(
                "Skipped FACODI navigation translation repair for %s because term structure differs",
                lang,
            )
            continue
        compatible[lang] = arch

    dictionary = field.get_translation_dictionary(source_arch, compatible)
    updates = defaultdict(dict)
    for source_term, translated_terms in dictionary.items():
        for lang, translated_term in translated_terms.items():
            updates[lang][source_term] = translated_term
    return dict(updates)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    View = env["ir.ui.view"].with_context(active_test=False)
    field = View._fields["arch_db"]
    canonical = env.ref(_CANONICAL_VIEW_XMLID)
    canonical_stored = field._get_stored_translations(canonical) or {}

    canonical_by_lang = {
        "en_US": _stored_value(canonical_stored, "en_US")
        or canonical.with_context(lang="en_US").arch,
    }
    for lang in _SUPPORTED_LANGS:
        value = _stored_value(canonical_stored, lang)
        if value:
            canonical_by_lang[lang] = value

    views = View.with_context(lang="en_US").search(
        [
            ("website_id", "!=", False),
            ("arch_db", "ilike", "s_facodi_course_showcase"),
        ]
    )

    repaired_views = 0
    repaired_translations = 0
    for view in views:
        stored = field._get_stored_translations(view) or {}
        source_arch = _stored_value(stored, "en_US")
        if not source_arch:
            continue

        repaired_source, source_changed = _repair_arch(
            source_arch,
            canonical_by_lang["en_US"],
        )
        translated_targets = {}
        translation_changed = False
        for lang in _SUPPORTED_LANGS:
            old_arch = _stored_value(stored, lang)
            canonical_arch = canonical_by_lang.get(lang)
            if not old_arch or not canonical_arch:
                continue
            repaired_arch, changed = _repair_arch(old_arch, canonical_arch)
            translated_targets[lang] = repaired_arch
            translation_changed |= changed

        if not source_changed and not translation_changed:
            continue

        if source_changed:
            view.with_context(lang="en_US").arch = repaired_source

        if translated_targets:
            updates = _translation_updates(field, repaired_source, translated_targets)
            if updates:
                view.update_field_translations("arch_db", updates)
                repaired_translations += len(updates)

        repaired_views += 1

    if repaired_views:
        _logger.info(
            "Reconciled stale FACODI course-showcase navigation in %s Website view(s), %s translated variant(s)",
            repaired_views,
            repaired_translations,
        )
