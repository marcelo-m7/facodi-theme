"""Remove the retired interactive hero visual from Website-specific copies.

Website Builder may keep COW ir.ui.view copies of the FACODI hero. Remove the
retired canvas layer from those copies while preserving editor-owned hero copy,
CTAs and study-board content.
"""

import logging

from lxml import etree

from odoo import SUPERUSER_ID, api


_logger = logging.getLogger(__name__)
_SUPPORTED_LANGS = ("pt_PT", "es_ES", "fr_FR")
_HERO_KEY = "theme_facodi.s_facodi_hero"
_RETIRED_LAYER_CLASS = "facodi-dither-veil"
_RETIRED_HERO_CLASS = "facodi-hero-dithered"


def _classes(node):
    return node.get("class", "").split()


def _parse_arch(arch):
    parser = etree.XMLParser(remove_blank_text=False)
    return etree.fromstring(arch.encode(), parser)


def _stored_value(translations, lang):
    return translations.get(f"_{lang}", translations.get(lang))


def _clean_arch(arch):
    try:
        root = _parse_arch(arch)
    except (etree.XMLSyntaxError, ValueError, AttributeError):
        return arch, False

    changed = False
    for hero in root.iter():
        classes = _classes(hero)
        if "facodi-hero" not in classes:
            continue

        if _RETIRED_HERO_CLASS in classes:
            hero.set(
                "class",
                " ".join(name for name in classes if name != _RETIRED_HERO_CLASS),
            )
            changed = True

        retired_layers = [
            node
            for node in hero.iterdescendants()
            if _RETIRED_LAYER_CLASS in _classes(node)
        ]
        for layer in retired_layers:
            parent = layer.getparent()
            if parent is not None:
                parent.remove(layer)
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
                "Skipped retired hero visual cleanup for %s because term structure differs",
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

    cleaned = 0
    for view in views:
        stored = field._get_stored_translations(view) or {}
        source_arch = _stored_value(stored, "en_US") or view.with_context(lang="en_US").arch_db
        if not source_arch:
            continue

        cleaned_source, source_changed = _clean_arch(source_arch)
        translated_targets = {}
        translation_changed = False
        for lang in _SUPPORTED_LANGS:
            old_arch = _stored_value(stored, lang)
            if not old_arch:
                continue
            cleaned_arch, changed = _clean_arch(old_arch)
            translated_targets[lang] = cleaned_arch
            translation_changed |= changed

        if not source_changed and not translation_changed:
            continue

        if source_changed:
            view.with_context(lang="en_US").arch = cleaned_source

        if translated_targets:
            updates = _translation_updates(field, cleaned_source, translated_targets)
            if updates:
                view.update_field_translations("arch_db", updates)

        cleaned += 1

    if cleaned:
        _logger.info("Removed retired hero visual from %s FACODI Website hero view(s)", cleaned)
