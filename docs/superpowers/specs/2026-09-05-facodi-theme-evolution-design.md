> Historical document: superseded where inconsistent with [current architecture](../../architecture.md) and the 2026-09-05 finalization plan.

# FACODI Theme — Evolution Design

Date: 2026-09-05  
Target: Odoo 19 Community  
Repository: `marcelo-m7/facodi-theme`  
Target technical addon: `theme_facodi`

## Status

This specification defines the approved evolution of the initial `website_facodi` implementation. It does not erase the original design document; it supersedes it for the next implementation cycle.

The design was derived from three references with an explicit priority order:

1. `https://edu-open2.odoo.com` — priority reference for the current FACODI visual identity and recognizable user experience;
2. `Open2Tech/facodi@feat/facodi-addon-v1` — selective source of UX, information-architecture and section-composition ideas;
3. `odoo/design-themes` branch `19.0` — technical authority for Odoo theme structure, Website Builder integration, assets, theme lifecycle and configurator patterns.

When these references conflict, the priority order above is authoritative.

## Purpose

`theme_facodi` is the presentation addon for FACODI across Odoo Website and Odoo eLearning. It establishes the visual system, reusable Website Builder composition primitives and presentation-level adaptations of standard Odoo pages without becoming a second CMS or LMS.

The theme must preserve standard Odoo behavior and remain independently installable with the required Odoo Community Website/eLearning theme dependencies. It contains no ingestion, AI, curriculum-mapping, semantic-analysis or deployment business logic.

## Core design principles

1. **Odoo standard first.** Configure or inherit standard Website/eLearning behavior before introducing FACODI-specific templates.
2. **Website Builder remains authoritative.** Editors continue to use standard Odoo editing, snippets, color combinations, menus, header/footer configuration and page lifecycle.
3. **Theme, not application fork.** The addon changes presentation and composition, not standard Odoo domain models or route semantics.
4. **No copied standard application templates.** Use stable QWeb inheritance points and CSS hooks instead of replacing complete Odoo views unless no narrower extension point exists.
5. **No business-data queries in presentation templates.** QWeb must not perform ad-hoc `sudo().search(...)` calls to assemble dynamic course data.
6. **Independent from FACODI learning logic.** `theme_facodi` does not depend on `facodi_learning`, `facodi_content` or another FACODI business addon.
7. **Minimal JavaScript.** Use standard Odoo/Bootstrap behavior; add JavaScript only when a theme/editor capability cannot be implemented with standard Odoo mechanisms.
8. **Upgrade resilience.** Prefer Odoo theme variables, `theme.utils`, configurator data, snippets and targeted inheritance over DOM replacement.
9. **One visual system.** The theme extends Odoo's palette and component system instead of creating a parallel design system that bypasses Website Builder controls.

## Naming and module boundary

The repository remains `facodi-theme` while the Odoo technical addon becomes `theme_facodi`.

This change aligns the module with the naming and lifecycle conventions used in `odoo/design-themes`. The previous `website_facodi` name is considered the initial implementation, not a permanent compatibility contract.

The repository must expose exactly one installable Odoo theme addon after the migration: `theme_facodi`.

Before deployment, implementation must verify whether any durable database already has `website_facodi` installed. If one does, the implementation plan must include a one-time controlled module-name migration. A permanent compatibility addon or two competing installable FACODI themes are explicitly out of scope.

## Dependencies and upstream theme source

The target addon baseline is:

```python
'depends': [
    'theme_common',
    'website_slides',
]
```

`theme_common` is provided by `odoo/design-themes`, not by the core `odoo/odoo` repository. Therefore, the build/runtime environment must expose a pinned Odoo 19-compatible `odoo/design-themes` source on the Odoo addons path.

The FACODI theme repository must not copy or vendor `theme_common`. The monorepo/build layer should pin the upstream `odoo/design-themes` revision as an external dependency so builds remain reproducible.

`website_slides` remains the canonical eLearning implementation.

No dependency on `facodi_learning`, `facodi_content`, AI providers, external APIs, Website Sale, Blog, Forum or Events is required for the baseline theme.

## Visual identity

The current `edu-open2` website is the visual authority.

The existing FACODI theme implementation provides the approved starting palette:

- FACODI Purple: `#6a4bff`
- FACODI Blue: `#5dc7ff`
- FACODI Surface: `#f7f6ff`
- White: `#ffffff`
- FACODI Ink: `#1f1e42`
- Heading Ink: `#111035`

These values are implementation baselines, not a substitute for visual comparison with `edu-open2`. During implementation acceptance, the rendered theme must be compared with the current website; if token-level differences are found, the current website wins and the theme tokens should be adjusted to reproduce it. This does not authorize a redesign toward the older Open2 lime/black identity.

Colors must be expressed through Odoo's theme palette and color-combination system rather than only through custom CSS classes. Standard section colors, buttons, links, menus, footer, headings and backgrounds must remain coherent inside Website Builder.

Typography should preserve the current FACODI character while preferring Odoo theme-font configuration and web-safe/system fallbacks. No font binaries are committed to the repository.

## Target addon structure

```text
theme_facodi/
├── __init__.py
├── __manifest__.py
├── data/
│   ├── generate_primary_template.xml
│   └── ir_asset.xml
├── models/
│   ├── __init__.py
│   └── theme_facodi.py
├── views/
│   ├── customizations.xml
│   ├── new_page_template.xml
│   ├── snippets.xml
│   └── website_slides.xml
├── static/
│   ├── description/
│   └── src/
│       ├── img/
│       ├── snippets/
│       └── scss/
│           ├── primary_variables.scss
│           ├── bootstrap_overridden.scss
│           ├── components.scss
│           ├── website.scss
│           ├── snippets.scss
│           └── website_slides.scss
└── tests/
```

Files with no real responsibility should not be created merely to match this tree, but unrelated responsibilities must not be collapsed into a monolithic stylesheet or catch-all XML file.

## Asset strategy

`primary_variables.scss` owns Odoo Website Builder/theme variables only: palette maps, website-value palettes, theme colors, typography selections and theme-level defaults.

Primary variables are registered using the Odoo theme asset mechanism in `data/ir_asset.xml` with the `web._assets_primary_variables` bundle.

Frontend SCSS is split by responsibility:

- `bootstrap_overridden.scss` — semantic Bootstrap variable adaptations that genuinely belong at variable level;
- `components.scss` — small reusable FACODI presentation primitives;
- `website.scss` — global public Website refinements;
- `snippets.scss` — FACODI-specific Website Builder snippet presentation;
- `website_slides.scss` — targeted `website_slides` presentation refinements.

A single large all-purpose frontend stylesheet is rejected.

## Theme lifecycle

The addon should use the standard lifecycle patterns present in `odoo/design-themes`:

- `_generate_primary_snippet_templates` during module data setup when required by the theme structure;
- `theme.utils` hooks only for activation/post-copy behavior that cannot be represented declaratively;
- Odoo asset records for primary variables and optional theme assets;
- manifest theme preview/configurator metadata where it improves the standard Website configuration experience.

Lifecycle hooks must not create FACODI learning/business records.

## Header and footer

The theme must not replace the complete standard `<header>` or `<footer>` merely to obtain FACODI styling.

Preferred order:

1. select the closest standard Odoo header/footer template through `$o-website-values-palettes`;
2. configure logo height, typography, link style and supported theme values;
3. style stable standard classes;
4. use small QWeb inheritance patches only for FACODI-specific presentation that cannot be achieved through configuration.

This preserves standard behavior for menus, mobile navigation, language selection, configurable logo, portal/login entries and Website Builder controls.

## Homepage and Website Builder composition

The theme must not hard-replace `website.homepage` with a large static FACODI application shell.

The homepage is composed through standard Odoo snippets wherever possible and a small set of FACODI-specific snippets where identity or semantics justify them.

Approved conceptual sections are:

- FACODI Hero;
- Learning Journey;
- Course Discovery presentation;
- Open Learning / manifesto callout;
- How FACODI Works;
- Community CTA;
- Institutional / SEA-EU block;
- general FACODI CTA.

Before creating any custom snippet, implementation must check whether a standard Odoo snippet can be configured and styled to produce the required result. FACODI snippets extend the Website Builder; they do not form a parallel builder.

The manifest may use `configurator_snippets`, `theme_customizations` and related standard mechanisms to define a coherent default homepage composition without making the page non-editable.

## Dynamic course content

The theme must not query `slide.channel` directly from homepage QWeb using `request.env` or `sudo()`.

Course discovery should use standard Odoo eLearning surfaces and standard dynamic-snippet/data mechanisms where available. If a FACODI-specific course-discovery snippet is necessary, its data acquisition must use the appropriate Odoo Website/dynamic-snippet extension point rather than an ORM query embedded in presentation markup.

This preserves access semantics, caching behavior and upgrade resilience.

## eLearning contract

`website_slides` remains the source of truth for learner-facing eLearning behavior.

The theme may visually adapt:

- `/slides` catalog;
- `slide.channel` course pages;
- `slide.slide` lesson/content pages;
- standard learner progress/profile surfaces exposed by `website_slides`;
- standard empty, navigation and content states directly associated with eLearning.

The theme must not introduce duplicate course, lesson, membership, progress or content models and must not create parallel routes for standard eLearning features.

QWeb changes to `website_slides` must be narrowly inherited and justified by a requirement that cannot be met through SCSS or supported theme configuration alone.

## Pages and editorial content

Theme code provides reusable visual composition, not permanent ownership of all website copy.

The expected public information architecture may include:

- Home;
- Courses / learning paths;
- About;
- Community;
- Manifesto;
- How it works.

These remain standard Odoo Website pages editable through Website Builder. The theme may provide new-page templates or default compositions, but editors remain able to modify content without changing addon code.

Institutional SEA-EU presentation is website content rendered with theme primitives; it is not a business rule embedded in the addon.

## Selective reuse from the Open2 proposal

The Open2 proposal is a design reference, not an implementation base to copy wholesale.

Approved ideas to reinterpret using the current FACODI identity include:

- the learning journey concept `Descobrir → Aprender → Contribuir`;
- stronger course-discovery presentation;
- community-oriented calls to action;
- institutional recognition blocks;
- learning-feature cards and staged information hierarchy.

Explicitly rejected from direct reuse:

- lime/black as the new primary identity;
- complete header replacement;
- complete homepage replacement;
- ad-hoc ORM searches inside QWeb;
- a monolithic frontend stylesheet;
- theme dependency on FACODI business addons.

## Standard-first decision rule

For every planned theme change:

```text
Does standard Odoo already provide the capability?
├── yes → configure or style the standard capability
└── no
    ├── is there a stable Odoo template/snippet extension point?
    │   ├── yes → inherit/extend it narrowly
    │   └── no → create a focused FACODI component
    └── never duplicate a complete standard application surface by default
```

This rule is part of the acceptance criteria.

## Accessibility and responsive behavior

The evolved theme must preserve or improve standard Odoo accessibility.

Requirements:

- keyboard-accessible navigation and controls;
- visible focus states;
- semantic headings and landmark structure;
- sufficient foreground/background contrast across FACODI color combinations;
- no interaction that depends solely on hover;
- responsive behavior across standard Odoo/Bootstrap breakpoints;
- respect for reduced-motion preferences for any future motion effects.

## Testing strategy

Testing must cover module integrity and preservation of standard Odoo surfaces.

Minimum automated coverage:

1. install `theme_facodi` on a clean Odoo 19/PostgreSQL database with the pinned `theme_common` dependency available;
2. compile relevant frontend/theme assets;
3. confirm `/` renders successfully after theme application;
4. confirm `/slides` renders successfully;
5. confirm a standard course page remains valid when fixture/test data is available;
6. verify the FACODI palette and selected theme values are registered;
7. verify standard Odoo favicon/logo behavior is not overridden with hard-coded theme URLs;
8. verify Website Builder/theme integration records load without XML or asset errors.

Where practical, browser-level coverage should validate representative desktop/mobile rendering and insertion of FACODI snippets in Website Builder. Visual regression tooling may be added later but is not a prerequisite for the first evolved release.

## Migration and compatibility

The implementation is an evolution of the current repository rather than a requirement to preserve the internal structure of `website_facodi`.

The implementation plan must explicitly account for:

- renaming the addon directory and manifest identity to `theme_facodi`;
- updating CI installation targets;
- updating monorepo assumptions and documentation that reference `website_facodi`;
- adding/pinning the upstream `odoo/design-themes` dependency needed for `theme_common` in the build environment;
- detecting whether a durable database has the old module installed before deployment;
- performing a controlled one-time module migration when necessary instead of shipping two FACODI themes.

Standard Odoo Website content created by editors must not be deleted as part of the theme migration.

## Monorepo contract

`facodi-monorepo` continues to consume this repository as the FACODI theme source and pins an exact commit into immutable application images.

The monorepo/build layer is also responsible for making a pinned Odoo 19-compatible `odoo/design-themes` dependency available on the addon path for `theme_common`.

This repository remains responsible only for FACODI theme code, tests and documentation. Deployment infrastructure remains outside it.

## Explicitly out of scope

- ingestion and AI pipelines;
- curriculum mapping and semantic analysis;
- FACODI learning-domain models;
- custom authentication flows;
- deployment/build orchestration inside the theme addon;
- PostgreSQL management;
- a bespoke frontend SPA;
- copied forks of complete Odoo Website/eLearning templates;
- permanent compatibility support for both `website_facodi` and `theme_facodi`;
- redesigning FACODI around the Open2 lime/black palette.

## Acceptance criteria

The evolved theme is accepted when all of the following are true:

1. the installable addon follows Odoo 19 design-theme conventions under `theme_facodi`;
2. the rendered identity follows the current `edu-open2` visual reference, using the current purple/blue FACODI tokens as the implementation baseline and reconciling token differences in favor of the live reference;
3. standard Website Builder editing remains functional and authoritative;
4. header/footer use standard Odoo mechanisms wherever possible;
5. homepage composition is editable and snippet-based rather than a hard-coded application shell;
6. `website_slides` remains the authoritative eLearning implementation;
7. no FACODI business addon is required to install the baseline theme;
8. no ad-hoc `sudo().search(...)` exists in theme QWeb for course discovery;
9. assets are separated by responsibility and integrated through standard Odoo theme asset mechanisms;
10. the required `theme_common` source is pinned reproducibly in the build environment rather than copied into this repository;
11. clean-install and key-route regression tests pass on Odoo 19;
12. existing editor-created Website content is preserved through the evolution;
13. the implementation remains small enough to track upstream Odoo theme patterns without creating a parallel frontend framework.
