# FACODI Website Foundation v2 Design

## Objective

Evolve `theme_facodi` into a richer, reusable Odoo 19 Community Website/eLearning presentation foundation while preserving Odoo standard ownership of Website, Website Builder, Portal, translations and `website_slides` learning content.

## Architectural boundary

`theme_facodi` owns presentation only: theme identity, selectable Website chrome, reusable snippets, page compositions, Website/eLearning styling, translation catalogues and presentation defaults. It must not become a parallel CMS or learning domain module.

Structured academic content remains owned by standard `website_slides` records and, when enrichment/ingestion is required, by `facodi_learning`. Theme QWeb must not query business data directly with `request.env` or `sudo()`.

## Standard-first rules

- Target Odoo 19 Community.
- Prefer `website`, `website_slides`, Portal, Website Builder, QWeb, native assets, `website.snippet.filter`, theme utilities and native i18n.
- Keep English as the canonical QWeb source language.
- Supply Portuguese (Portugal), Spanish and French through native Odoo PO catalogues.
- Do not implement custom per-language QWeb branches.
- Do not import arbitrary `website.page` editorial records from the theme.
- Preserve Website Builder/COW customizations on existing databases.
- Every reusable FACODI block must have a stable XML ID and Website Builder registry entry.
- Dynamic snippets must preserve Odoo's required structural contracts, including `.s_dynamic_snippet_container`, `.s_dynamic_snippet_content` and `.dynamic_snippet_template` when using the standard dynamic-snippet plugin.

## Website foundation

The reusable block library should cover:

1. Hero / primary value proposition.
2. Dynamic published-course showcase backed by `website.snippet.filter` and `slide.channel`.
3. Learning journey / how it works.
4. Learning principles / differentiators.
5. Academic areas and pathways presentation blocks using editorial content, with links into standard eLearning/search routes rather than duplicated course data.
6. Institutional / manifesto blocks.
7. Community and contribution blocks.
8. Partner / ecosystem presentation blocks.
9. Roadmap / project-status blocks.
10. FAQ and course-catalogue CTAs.

Page-picker compositions should combine these blocks for Home, About, Manifesto, Community, Contribution, Pathways, Partners, Roadmap and general editorial pages without creating fixed Website pages in module data.

## Visual system

Continue the FACODI palette and typography already established in the theme. Expand reusable presentation primitives for cards, badges, section headings, buttons, navigation states, forms, alerts and eLearning surfaces while respecting Website Builder color combinations and editor-selected content.

Customization must be scoped under the active FACODI theme and avoid global rules that make other Website color combinations or native Odoo states unreadable.

## eLearning

Keep `website_slides` as the functional foundation. Theme changes may style channel covers, cards, enrollment/join actions, navigation and content hierarchy, but must not replace standard course, slide, enrollment or completion mechanics.

## Accessibility and responsive behavior

- Semantic heading order and landmarks.
- Keyboard-visible focus states.
- Meaningful link/button labels.
- Decorative icons excluded from accessibility output where appropriate.
- Responsive layouts without horizontal overflow.
- Reduced-motion support for custom transitions.

## Internationalization

All new source copy is English. Every new user-facing source string introduced by this phase must be represented in `theme_facodi.pot` and translated in `pt.po`, `es.po` and `fr.po`. Translation references must continue to target theme records so Odoo can copy them correctly when the theme is applied.

## Compatibility and testing

Every increment must use TDD and preserve the existing CI matrix:

- repository architecture contract;
- dynamic homepage/dashboard contract;
- native i18n contract;
- XML validity;
- clean Odoo 19 installation;
- theme tests;
- module upgrade on the same database and filestore.

Production incidents found in Website Builder must become regression tests before fixes are merged.

## Delivery strategy

Land the foundation in small reviewed PRs rather than one monolithic change. Production-critical compatibility fixes are merged and deployed first. Enrichment then proceeds in independent slices: reusable snippets, visual primitives, translations, eLearning refinements and page compositions. After a theme merge is green, update the exact `facodi-theme` gitlink in `facodi-deploy`, run the canonical Coolify runtime acceptance, and merge the deployment pin only when that CI is green.
