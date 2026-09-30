"""Reconcile learner-facing learning-path terminology in persisted Website views.

FACODI keeps Website Builder copies instead of overwriting editor-owned pages on
theme upgrades.  Source XML therefore is not enough to rename visible
"Roadmaps" labels.  This migration only rewrites exact known UI strings in
existing FACODI Website views and their PT/ES/FR translations.  Routes and
structure remain unchanged.
"""

import logging

from lxml import etree

from odoo import SUPERUSER_ID, api


_logger = logging.getLogger(__name__)
_SUPPORTED_LANGS = ("pt_PT", "es_ES", "fr_FR")

_COPY = {
    "en_US": {
        "Roadmaps": "Learning paths",
        "Explore Roadmaps": "Explore learning paths",
        "Curricular Units": "Curricular units",
        (
            "Explore courses, Roadmaps and curricular units built from public "
            "learning resources, reviewed context and community contribution."
        ): (
            "Explore courses, learning paths and curricular units built from "
            "public learning resources, reviewed context and community contributions."
        ),
        (
            "Move between topics, courses, Roadmaps and academic context when "
            "a connection helps."
        ): (
            "Move between topics, courses, learning paths and academic context "
            "when a connection helps."
        ),
        (
            "Start with a course, Roadmap, curricular unit or one very concrete question."
        ): (
            "Start with a course, learning path, curricular unit or one very concrete question."
        ),
    },
    "pt_PT": {
        "Roadmaps": "Percursos de aprendizagem",
        "Explorar Roadmaps": "Explorar percursos de aprendizagem",
        "Unidades Curriculares": "Unidades curriculares",
        (
            "Explora cursos, Roadmaps e unidades curriculares construídos a partir "
            "de recursos de aprendizagem públicos, contexto revisto e contributo da comunidade."
        ): (
            "Explora cursos, percursos de aprendizagem e unidades curriculares que "
            "ligam recursos de aprendizagem públicos, contexto revisto e contributos da comunidade."
        ),
        (
            "Move-te entre temas, cursos, Roadmaps e contexto académico quando uma ligação ajudar."
        ): (
            "Move-te entre temas, cursos, percursos de aprendizagem e contexto académico "
            "quando uma ligação ajudar."
        ),
        (
            "Começa por um curso, Roadmap, unidade curricular ou uma pergunta muito concreta."
        ): (
            "Começa por um curso, percurso de aprendizagem, unidade curricular ou uma "
            "pergunta muito concreta."
        ),
    },
    "es_ES": {
        "Rutas": "Rutas de aprendizaje",
        "Explorar rutas": "Explorar rutas de aprendizaje",
        "Unidades Curriculares": "Unidades curriculares",
        (
            "Explora cursos, rutas y unidades curriculares construidos a partir de recursos "
            "públicos de aprendizaje, contexto revisado y contribución de la comunidad."
        ): (
            "Explora cursos, rutas de aprendizaje y unidades curriculares que conectan "
            "recursos públicos de aprendizaje, contexto revisado y contribuciones de la comunidad."
        ),
        (
            "Muévete entre temas, cursos, rutas y contexto académico cuando una conexión ayude."
        ): (
            "Muévete entre temas, cursos, rutas de aprendizaje y contexto académico "
            "cuando una conexión ayude."
        ),
        (
            "Empieza por un curso, Roadmap, unidad curricular o una pregunta muy concreta."
        ): (
            "Empieza por un curso, una ruta de aprendizaje, una unidad curricular o "
            "una pregunta muy concreta."
        ),
    },
    "fr_FR": {
        "Parcours": "Parcours d’apprentissage",
        "Explorer les parcours": "Explorer les parcours d’apprentissage",
        (
            "Explorez des cours, des parcours et des unités d’enseignement construits à partir "
            "de ressources d’apprentissage publiques, d’un contexte vérifié et de contributions "
            "de la communauté."
        ): (
            "Explorez des cours, des parcours d’apprentissage et des unités d’enseignement "
            "qui relient des ressources d’apprentissage publiques, un contexte vérifié et des "
            "contributions de la communauté."
        ),
        (
            "Passez entre thèmes, cours, parcours et contexte académique lorsqu’un lien est utile."
        ): (
            "Passez entre thèmes, cours, parcours d’apprentissage et contexte académique "
            "lorsqu’un lien est utile."
        ),
        (
            "Commencez par un cours, un Roadmap, une unité d’enseignement ou une question très concrète."
        ): (
            "Commencez par un cours, un parcours d’apprentissage, une unité d’enseignement "
            "ou une question très concrète."
        ),
    },
}


def _parse_arch(arch):
    return etree.fromstring(
        arch.encode(),
        etree.XMLParser(remove_blank_text=False),
    )


def _stored_value(translations, lang):
    return translations.get(f"_{lang}", translations.get(lang))


def _rewrite_arch(arch, lang):
    if not arch:
        return arch, False
    try:
        root = _parse_arch(arch)
    except (etree.XMLSyntaxError, ValueError, AttributeError):
        return arch, False

    replacements = _COPY[lang]
    changed = False
    for node in root.iter():
        if node.text in replacements:
            node.text = replacements[node.text]
            changed = True
        if node.tail in replacements:
            node.tail = replacements[node.tail]
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
                "Skipped FACODI learning-path terminology repair for %s because "
                "the translated view structure differs",
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

    # Include editor-owned page copies and persisted snippets, but touch only
    # exact known UI strings.  This preserves arbitrary editor text and hrefs.
    views = View.with_context(lang="en_US").search([
        ("website_id", "!=", False),
        "|",
        ("arch_db", "ilike", "Roadmap"),
        ("arch_db", "ilike", "Curricular Units"),
    ])

    repaired = 0
    translated = 0
    for view in views:
        stored = field._get_stored_translations(view) or {}
        source_arch = (
            _stored_value(stored, "en_US")
            or view.with_context(lang="en_US").arch_db
        )
        if not source_arch:
            continue

        repaired_source, source_changed = _rewrite_arch(source_arch, "en_US")
        translated_targets = {}
        translation_changed = False
        for lang in _SUPPORTED_LANGS:
            old_arch = _stored_value(stored, lang)
            if not old_arch:
                continue
            repaired_arch, changed = _rewrite_arch(old_arch, lang)
            translated_targets[lang] = repaired_arch
            translation_changed |= changed

        if not source_changed and not translation_changed:
            continue

        updates = {}
        if translated_targets:
            updates = _translation_updates(
                field,
                repaired_source,
                translated_targets,
            )

        if source_changed:
            view.with_context(lang="en_US").arch = repaired_source

        if updates:
            view.update_field_translations("arch_db", updates)
            translated += len(updates)

        repaired += 1

    if repaired:
        _logger.info(
            "Reconciled learner-facing learning-path terminology in %s FACODI "
            "Website view(s), with %s translated update set(s)",
            repaired,
            translated,
        )
