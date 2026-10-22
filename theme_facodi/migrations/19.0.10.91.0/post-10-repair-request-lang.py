"""Repair Odoo 19 translation-editor QWeb failures without losing translations.

In Odoo 19, `request.lang` is not defined in the public asset rendering
environment (ir.ui.view.render_public_asset). Some older editor-owned FACODI
views, including language-specific versions of Course Showcase, still contain
`request.lang.code` even after the theme-owned source moved to native
translated text.

A normal ORM write of arch_db would risk resetting an editor-owned page or
flattening localized HTML. Patch only the unsupported expression inside each
JSONB translation value, leaving all content and locale keys untouched.

Idempotent: the WHERE clause matches only remaining deprecated expressions.
"""
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

SOURCE_EXPRESSION = "request.lang.code"
REPLACEMENT_EXPRESSION = "env.lang"


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Only theme-owned templates and persisted website-specific copies.
    # Preserve every arch_db JSONB language variant without writing a source
    # language through ORM, which could invalidate hand-edited translations.
    cr.execute(
        """
        SELECT id, key
          FROM ir_ui_view
         WHERE (key LIKE 'theme_facodi.%%' OR website_id IS NOT NULL)
           AND arch_db::text LIKE %s
         ORDER BY id
        """,
        ("%" + SOURCE_EXPRESSION + "%",),
    )
    affected = cr.fetchall()
    if not affected:
        return

    cr.execute(
        """
        UPDATE ir_ui_view AS v
           SET arch_db = (
               SELECT jsonb_object_agg(
                          locale,
                          replace(source_html, %s, %s)
                      )
                 FROM jsonb_each_text(v.arch_db)
                      AS entries(locale, source_html)
           )
         WHERE (v.key LIKE 'theme_facodi.%%' OR v.website_id IS NOT NULL)
           AND v.arch_db::text LIKE %s
        """,
        (
            SOURCE_EXPRESSION,
            REPLACEMENT_EXPRESSION,
            "%" + SOURCE_EXPRESSION + "%",
        ),
    )
    if cr.rowcount != len(affected):
        raise RuntimeError(
            "FACODI QWeb language repair changed an unexpected number of views "
            "(expected %s, got %s)" % (len(affected), cr.rowcount)
        )

    cr.execute(
        """
        SELECT count(*)
          FROM ir_ui_view
         WHERE (key LIKE 'theme_facodi.%%' OR website_id IS NOT NULL)
           AND arch_db::text LIKE %s
        """,
        ("%" + SOURCE_EXPRESSION + "%",),
    )
    if cr.fetchone()[0]:
        raise RuntimeError("FACODI QWeb language repair left unsupported expressions")

    env.invalidate_all()
    _logger.info(
        "FACODI Odoo 19 translation editor: repaired %s views containing "
        "request.lang.code, preserving locale-specific arch_db",
        len(affected),
    )
