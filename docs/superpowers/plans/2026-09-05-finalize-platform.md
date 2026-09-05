# FACODI Theme finalization plan

Goal: Preserve the real FACODI identity while completing reusable Website + eLearning presentation.
Architecture: tokens -> primitives -> components -> snippets -> native new-page templates. No business models, controllers, database IDs or theme-learning dependency.
Spec: user execution briefing, 2026-09-05; palette Ink #142846, Cyan #37BED2, Blue #3979C8, Mint #A7E8BE, Sun #EFFF00, Paper #F9FAFB.

## Task 1: Native shell and accessible components
- [x] Add render regression tests for nested menus/new-window/active/Portal; replace handmade submenu tree with website.submenu.
- [x] Consolidate tokens and shared lead/actions/section/grid/card primitives; harmonize standard buttons, forms, alerts, pagination and eLearning without copying Odoo templates.
- [x] Fix inaccessible focus contrast, responsive overflow and partial automatic dark-mode overrides. Preserve Website Builder color combinations and editorial cover images.
- [x] Remove empty QWeb file and obsolete CSS; run source contract and Odoo asset tests.

## Task 2: Builder library and native page compositions
- [x] Retain Hero/Journey/Institutional; add only useful editorial intro, features, community/contribution CTA, roadmap, FAQ and course CTA blocks. Use semantic headings, editable text and no fake metrics/testimonials/partners.
- [x] Register native new_page_templates using fully qualified FACODI snippets for home/about/manifesto/how/community/pathways/contribution/roadmap/partners/editorial; standard /slides and /contactus remain canonical routes.
- [x] Test actual rendered template creation, snippet registry and persistence of editor changes across regeneration/upgrade. No website.page XML data dump.
- [x] Document component inventory and page composition map.

## Task 3: Verification and release
- [x] Clean install/theme activation, compiled CSS, HTTP / /slides /web/login /contactus /my; add CI upgrade run.
- [x] Browser desktop/tablet/mobile and Builder save/reload, screenshots and real eLearning fixtures in disposable DB.
- [x] Review entire diff, update README/architecture, archive superseded specs; coherent commits and separate PR.
