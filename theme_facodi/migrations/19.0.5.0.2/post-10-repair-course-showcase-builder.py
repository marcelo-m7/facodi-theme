"""Repair persisted legacy FACODI course showcases for Odoo 19 Website Builder."""

import logging

from lxml import etree

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

_SNIPPET_NAMES = (
    "s_facodi_course_showcase",
    "theme_facodi.s_facodi_course_showcase",
)


def _has_class(node, class_name):
    return class_name in node.get("class", "").split()


def _add_classes(node, *class_names):
    classes = node.get("class", "").split()
    changed = False
    for class_name in class_names:
        if class_name not in classes:
            classes.append(class_name)
            changed = True
    if changed:
        node.set("class", " ".join(classes))
    return changed


def _descendants_with_class(node, class_name):
    return [element for element in node.iterdescendants() if _has_class(element, class_name)]


def _repair_snippet(snippet):
    changed = False

    containers = _descendants_with_class(snippet, "s_dynamic_snippet_container")
    if not containers:
        legacy_containers = [
            child for child in snippet
            if _has_class(child, "facodi-dashboard")
        ]
        if legacy_containers:
            changed |= _add_classes(
                legacy_containers[0],
                "s_dynamic_snippet_container",
                "facodi-dynamic-shell",
            )

    contents = _descendants_with_class(snippet, "s_dynamic_snippet_content")
    if not contents:
        legacy_contents = _descendants_with_class(snippet, "facodi-dashboard-main")
        if legacy_contents:
            changed |= _add_classes(
                legacy_contents[0],
                "s_dynamic_snippet_content",
                "facodi-dynamic-content",
                "oe_unremovable",
                "oe_unmovable",
                "o_not_editable",
            )

    return changed


def _repair_arch(arch):
    parser = etree.XMLParser(remove_blank_text=False)
    try:
        root = etree.fromstring(arch.encode(), parser)
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
        changed |= _repair_snippet(snippet)

    if not changed:
        return arch, False
    return etree.tostring(root, encoding="unicode"), True


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    View = env["ir.ui.view"].with_context(active_test=False, lang=None)
    views = View.search([("arch_db", "ilike", "s_facodi_course_showcase")])

    repaired_count = 0
    for view in views:
        repaired_arch, changed = _repair_arch(view.arch_db)
        if not changed:
            continue
        view.write({"arch_db": repaired_arch})
        repaired_count += 1

    if repaired_count:
        _logger.info(
            "Repaired Odoo dynamic-snippet builder contract in %s FACODI view(s)",
            repaired_count,
        )
