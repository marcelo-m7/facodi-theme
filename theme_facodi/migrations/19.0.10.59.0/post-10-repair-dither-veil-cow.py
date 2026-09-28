"""Repair Website-specific FACODI hero copies so Dither Veil can run.

Website Builder creates COW ir.ui.view copies. Older/experimental copies may
retain a placeholder Dither node without the canvas/source contract expected by
facodi_dither_veil.js. Repair only the Dither layer and preserve editor-owned
hero copy, CTAs and study-board content.
"""

import logging

from lxml import etree

from odoo import SUPERUSER_ID, api


_logger = logging.getLogger(__name__)
_SUPPORTED_LANGS = ("pt_PT", "es_ES", "fr_FR")
_HERO_KEY = "theme_facodi.s_facodi_hero"


def _classes(node):
    return node.get("class", "").split()


def _parse_arch(arch):
    parser = etree.XMLParser(remove_blank_text=False)
    return etree.fromstring(arch.encode(), parser)


def _stored_value(translations, lang):
    return translations.get(f"_{lang}", translations.get(lang))


def _canonical_veil():
    veil = etree.Element(
        "div",
        {
            "class": "facodi-dither-veil",
            "data-facodi-dither-veil": "1",
            "data-src": "/theme_facodi/static/src/img/banner.png",
            "data-pixel-size": "5",
            "data-reveal-radius": "175",
            "data-linger": "1050",
            "data-ink-color": "#142846",
            "data-paper-color": "#F9FAFB",
            "data-rim-color": "#37BED2",
            "aria-hidden": "true",
        },
    )
    etree.SubElement(veil, "canvas", {"class": "facodi-dither-veil__canvas"})
    return veil


def _repair_arch(arch):
    try:
        root = _parse_arch(arch)
    except (etree.XMLSyntaxError, ValueError, AttributeError):
        return arch, False

    heroes = [
        node
        for node in root.iter()
        if "facodi-hero" in _classes(node)
    ]
    changed = False
    for hero in heroes:
        hero_classes = _classes(hero)
        if "facodi-hero-dithered" in hero_classes:
            hero.set(
                "class",
                " ".join(name for name in hero_classes if name != "facodi-hero-dithered"),
            )
            changed = True

        boards = [
            node
            for node in hero.iterdescendants()
            if "facodi-hero-study-board" in _classes(node)
        ]
        if not boards:
            continue
        board = boards[0]

        veils = [
            node
            for node in hero.iterdescendants()
            if "facodi-dither-veil" in _classes(node)
        ]
        canonical = None
        for veil in veils:
            parent = veil.getparent()
            valid = (
                parent is board
                and veil.get("data-facodi-dither-veil") == "1"
                and veil.get("data-src")
                and any(
                    "facodi-dither-veil__canvas" in _classes(child)
                    for child in veil.iterdescendants()
                )
            )
            if valid and canonical is None:
                canonical = veil
                continue
            parent.remove(veil)
            changed = True

        if canonical is None:
            board.insert(0, _canonical_veil())
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
                "Skipped FACODI Dither Veil translation repair for %s because term structure differs",
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
    views = View.with_context(lang="en_US").search(
        [("key", "=", _HERO_KEY), ("website_id", "!=", False)]
    )

    repaired = 0
    for view in views:
        stored = field._get_stored_translations(view) or {}
        source_arch = _stored_value(stored, "en_US") or view.with_context(lang="en_US").arch_db
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
            view.with_context(lang="en_US").arch = repaired_source

        if translated_targets:
            updates = _translation_updates(field, repaired_source, translated_targets)
            if updates:
                view.update_field_translations("arch_db", updates)

        repaired += 1

    if repaired:
        _logger.info("Repaired Dither Veil contract in %s FACODI Website hero view(s)", repaired)
