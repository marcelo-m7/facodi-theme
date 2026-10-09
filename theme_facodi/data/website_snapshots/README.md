# Odoo → code synchronization — 2026-10-09

This directory holds **read-only captures** of QWeb `ir.ui.view.arch_db` read from the production FACODI database. The files are **not** installed via `__manifest__.py`; adding these fragments directly to `data` would be unsafe and could create duplicate views/pages.

## Capture inventory

| File | Live `ir.ui.view` ID | XML key | Handling |
| --- | ---: | --- | --- |
| `facodi_footer.xml` | 5176 | `theme_facodi.facodi_footer` | Theme-owned; updated `views/customizations.xml` with multilingual curated navigation |
| `partnerships.xml` | 6144 | `website.facodi_partnerships` | Website page; database owns current publishing |
| `about_facodi.xml` | 2669 | `website.about-facodi` | Website page; database owns current publishing |
| `privacy_policy.xml` | 6140 | `website.facodi_privacy_policy` | Website page; database owns current publishing |
| `terms_of_use.xml` | 6141 | `website.facodi_terms_of_use` | Website page; database owns current publishing |
| `legal_notice.xml` | 6142 | `website.facodi_legal_notice` | Website page; database owns current publishing |
| `content_rights.xml` | 6143 | `website.facodi_content_rights` | Website page; database owns current publishing |

Translations are inline `request.lang.code` dictionaries in the captured QWeb. These are part of the source, not separate gettext catalogs. Do not replace them with plain EN text.

## Deployment gate

1. Back up the live database and export current `arch_db` of every view above before rebuilding or upgrading the theme.
2. Diff the fresh export against these snapshots and the relevant theme XML. Any divergence is a manual review gate. Do **not** overwrite the live instance automatically.
3. For `theme_facodi.facodi_footer`, compare the QWeb inside `views/customizations.xml` with the live website-specific copy. A module upgrade may re-render/re-copy the theme template.
4. For site pages, inspect `website.page`, `ir.ui.view`, `theme.ir.ui.view`, `ir.model.data` and update hooks to determine their actual ownership **before** registering XML records or changing `noupdate`.
5. Validate QWeb, PT/EN/FR/ES rendering, permissions, all navigation URLs, responsive layout and the public website in staging.
6. Only after staging tests pass and live contents have been reconciled, promote the source change and deploy with backup/rollback.

### Important drift observed during export

The production API returned footer view 5176 with the **old menu-driven footer** (only Accessibility and Cookie Policy under Policies), despite an earlier confirmed edit showing 21 links. The snapshot preserves what the API returned at export time; `views/customizations.xml` now tracks the intended 21-link multilingual footer. **Do not deploy it without reconciling this drift.**

Other considerations: SVG/PNG logos of Corvanis and University of Algarve are currently external assets referenced by the Partnerships page, not bundled licensed assets in the repository. Verify official asset URLs and permission, and prefer local versioned files. The snapshot is not proof of external image availability.

## Rule

Code-owned views belong in tracked module XML; website-owned records should be captured, diffed and managed via an explicit, idempotent migration that retains their `website.page` relations and translations. Never silently prefer GitHub over live edits.
