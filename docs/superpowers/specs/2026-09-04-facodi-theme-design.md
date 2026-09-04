# FACODI Theme — Evolved Odoo 19 Design

Date: 2026-09-04  
Target: Odoo 19 Community  
Repository: `marcelo-m7/facodi-theme`  
Target technical addon: `theme_facodi`

## Status

This specification supersedes the initial `website_facodi` design. It captures the approved evolution of the FACODI theme after comparing three references:

1. the current FACODI website at `https://edu-open2.odoo.com` as the priority reference for visual identity and recognizable user experience;
2. `Open2Tech/facodi@feat/facodi-addon-v1` as a selective source of UX and content-composition ideas;
3. `odoo/design-themes` branch `19.0` as the technical authority for theme structure, Website Builder integration, assets, theme lifecycle and configuration patterns.

When these references conflict, the priority order above is authoritative.

## Purpose

`theme_facodi` is the presentation addon for FACODI across Odoo Website and Odoo eLearning. It establishes the visual system, reusable Website Builder composition primitives and presentation-level adaptations of standard Odoo pages without becoming a second CMS or LMS.

The theme must preserve standard Odoo behavior and remain independently installable with Odoo Community Website/eLearning. It contains no ingestion, AI, curriculum-mapping, semantic-analysis or deployment business logic.

## Core design principles

1. **Odoo standard first.** Configure or inherit standard Website/eLearning behavior before introducing FACODI-specific templates.
2. **Website Builder remains authoritative.** Editors must continue to use standard Odoo editing, snippets, color combinations, menus, header/footer configuration and page lifecycle.
3. **Theme, not application fork.** The addon changes presentation and composition, not standard Odoo domain models or route semantics.
4. **No copied standard application templates.** Use stable QWeb inheritance points and CSS hooks instead of replacing entire Odoo views unless no narrower extension point exists.
5. **No business-data queries in presentation templates.** QWeb must not perform ad-hoc `sudo().search(...)` calls to assemble dynamic course data.
6. **Independent from FACODI learning logic.** `theme_facodi` does not depend on `facodi_learning` or another FACODI business addon.
7. **Minimal JavaScript.** Use standard Odoo/Bootstrap behavior. Add JS only when a theme/editor capability cannot be implemented with standard Odoo mechanisms.
8. **Upgrade resilience.** Prefer Odoo theme variables, `theme.utils`, configurator data, snippets and targeted inheritance over DOM replacement.

## Naming and module boundary

The repository remains `facodi-theme` while the Odoo technical addon becomes `theme_facodi`.

This change intentionally aligns the module with the naming and lifecycle conventions used by Odoo design themes. The previous `website_facodi` name is considered an initial pre-evolution implementation rather than a permanent compatibility contract.

Implementation must verify whether any durable environment already has `website_facodi` installed before the rename is deployed. If it does, the implementation plan must include a one-time controlled module-name migration. A permanent compatibility addon or duplicate installable theme is out of scope.

The repository should expose one primary installable theme addon: `theme_facodi`.

## Dependencies

The target baseline is deliberately small:

```python
'depends': [
    'theme_common',
    'website_slides',
]
```

`theme_common` provides the shared theme foundation expected by Odoo design themes. `website_slides` supplies the canonical eLearning catalog, channels, slides, progress and learner-facing routes.

No dependency on `facodi_learning`, `facodi_content`, AI providers, external APIs, website sale, blog, forum or events is required for the baseline theme.

## Visual identity

The current `edu-open2` FACODI identity takes precedence over the lime/black identity from the older Open2 proposal.

The baseline FACODI palette remains:

- FACODI Purple: `#6a4bff`
- FACODI Blue: `#5dc7ff`
- FACODI Surface: `#f7f6ff`
- White: `#ffffff`
- FACODI Ink: `#1f1e42`
- Heading Ink: `#111035`

These colors must be expressed through Odoo's theme palette and color-combination system rather than only through custom CSS classes. Standard section colors, buttons, links, menus, footer, headings and backgrounds must therefore remain coherent inside the Website Builder.

Typography should preserve the current FACODI visual character while preferring Odoo theme-font configuration and web-safe/system fallbacks. No font binaries are committed to the repository.

## Odoo theme architecture

The target addon structure is:

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

This structure may be reduced where a file has no real responsibility, but implementation must not collapse unrelated presentation responsibilities into one monolithic stylesheet.

## Asset strategy

`primary_variables.scss` owns Odoo Website Builder/theme variables only: palette maps, website-value palettes, theme colors, typography selections and compatible theme-level defaults.

Primary variables are registered using the Odoo theme asset mechanism in `data/ir_asset.xml` with the `web._assets_primary_variables` bundle.

Frontend SCSS is split by responsibility:

- `bootstrap_overridden.scss`: semantic Bootstrap variable adaptations that genuinely belong at variable level;
- `components.scss`: small reusable FACODI presentation primitives;
- `website.scss`: global public Website refinements;
- `snippets.scss`: FACODI-specific Website Builder snippet presentation;
- `website_slides.scss`: targeted `website_slides` presentation refinements.

A single large all-purpose frontend stylesheet is explicitly rejected.

## Theme lifecycle

The addon should use the standard theme lifecycle patterns present in `odoo/design-themes`:

- `_generate_primary_snippet_templates` during module data setup where required;
- `theme.utils` hooks only for theme activation/post-copy behavior that cannot be represented declaratively;
- Odoo asset records for theme-specific primary variables and optional assets;
- theme preview/configurator metadata in the manifest where it improves standard Website configuration.

Lifecycle hooks must not create business records unrelated to theme configuration.

## Header and footer

The theme must not replace the complete standard `<header>` or `<footer>` merely to obtain FACODI styling.

Preferred order:

1. select the closest standard Odoo header/footer template through `$o-website-values-palettes`;
2. configure logo height, fonts, link style and related supported theme values;
3. apply styling to stable standard classes;
4. use small QWeb inheritance patches only for FACODI-specific presentation that cannot be achieved through configuration.

This preserves Odoo behavior for menus, mobile navigation, language selection, configurable logo, portal/login entries and Website Builder controls.

## Homepage and Website Builder composition

The theme does not hard-replace `website.homepage` with a large static FACODI application shell.

Instead, the visual composition inspired by the current site and the Open2 proposal is represented through standard snippets where possible and a small set of FACODI snippets where identity or semantics justify them.

Approved conceptual sections are:

- FACODI Hero;
- Learning Journey;
- Course Discovery presentation;
- Open Learning / manifesto callout;
- How FACODI Works;
- Community CTA;
- Institutional / SEA-EU block;
- general FACODI CTA.

Before creating any custom snippet, implementation must check whether a standard Odoo snippet can be configured and styled to produce the required result. FACODI snippets are an extension layer, not a parallel Website Builder.

The manifest may use `configurator_snippets`, `theme_customizations` and related standard mechanisms to define a coherent default homepage composition without making the page non-editable.

## Dynamic course content

The theme must not query `slide.channel` directly from homepage QWeb using `request.env`/`sudo()`.

Course discovery should use standard Odoo eLearning surfaces and standard dynamic-snippet/data mechanisms where available. If a FACODI-specific course-discovery snippet becomes necessary, its data acquisition must use the appropriate Odoo Website/dynamic-snippet extension point rather than an ad-hoc ORM query embedded in presentation markup.

This keeps access semantics, caching behavior and future Odoo upgrades manageable.

## eLearning contract

`website_slides` remains the source of truth for learner-facing eLearning behavior.

The theme may visually adapt:

- `/slides` catalog;
- `slide.channel` course pages;
- `slide.slide` lesson/content pages;
- standard learner progress/profile surfaces exposed by `website_slides`;
- standard empty, navigation and content states directly associated with eLearning.

The theme must not introduce duplicate course, lesson, membership, progress or content models and must not create parallel routes for standard eLearning features.

QWeb changes to `website_slides` should be narrowly inherited and justified by a requirement that cannot be met through SCSS alone.

## Pages and editorial content

Theme code provides reusable visual composition, not permanent editorial ownership of all website text.

The expected public information architecture may include:

- Home;
- Courses / learning paths;
- About;
- Community;
- Manifesto;
- How it works.

These pages remain standard Odoo Website pages editable through Website Builder. The theme may provide new-page templates or default compositions, but editors remain able to modify page content without changing addon code.

Institutional SEA-EU presentation is a content concern rendered using theme primitives; it is not hard-coded as a business rule.

## Selective reuse from the Open2 proposal

The Open2 proposal is a design reference, not an implementation base to copy wholesale.

Approved ideas to reinterpret in the current FACODI identity include:

- the learning journey concept `Descobrir → Aprender → Contribuir`;
- stronger course-discovery presentation;
- community-oriented calls to action;
- institutional recognition blocks;
- clear learning-feature cards and staged information hierarchy.

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
    └── never duplicate a whole standard application surface by default
```

This rule is part of the acceptance criteria, not merely implementation advice.

## Accessibility and responsive behavior

The evolved theme must preserve or improve standard Odoo accessibility rather than regress it.

Requirements:

- keyboard-accessible navigation and controls;
- visible focus states;
- semantic headings and landmark structure;
- sufficient foreground/background contrast for FACODI color combinations;
- no interaction that depends solely on hover;
- responsive behavior across standard Odoo/Bootstrap breakpoints;
- respect for reduced-motion preferences for any future motion effects.

## Testing strategy

Testing must cover both module integrity and preservation of standard Odoo surfaces.

Minimum automated coverage:

1. install `theme_facodi` on a clean Odoo 19/PostgreSQL database with required dependencies;
2. compile the relevant frontend/theme assets;
3. confirm `/` renders successfully after theme application;
4. confirm `/slides` renders successfully;
5. confirm a standard course page remains valid when fixture/test data is available;
6. verify the FACODI theme palette/selected theme values are registered;
7. verify standard Odoo favicon/logo behavior is not hard-coded over by the theme;
8. verify core Website Builder/theme integration records can be loaded without XML/asset errors.

Where practical, browser-level coverage should validate representative desktop/mobile rendering and Website Builder insertion of FACODI snippets. Visual regression tooling may be added later but is not a prerequisite for the first evolved release.

## Migration and compatibility

The implementation is an evolution of the current repository rather than a requirement to preserve the internal structure of `website_facodi`.

The implementation plan must explicitly account for:

- renaming the addon directory and manifest identity to `theme_facodi`;
- updating CI installation targets;
- updating monorepo assumptions and submodule documentation where they reference `website_facodi`;
- detecting whether an existing durable database has the old module installed before deployment;
- executing a controlled one-time module migration if necessary rather than shipping two competing FACODI themes.

Standard Odoo Website content already created by editors must not be deleted as part of theme migration.

## Monorepo contract

`facodi-monorepo` continues to consume this repository as the theme source under its theme submodule path and pins an exact commit into immutable application images.

The implementation must keep repository/build integration straightforward: the theme repo contains theme code and its tests/documentation; deployment infrastructure remains outside this repository.

## Explicitly out of scope

- ingestion and AI pipelines;
- curriculum mapping and semantic analysis;
- FACODI learning-domain models;
- custom authentication flows;
- deployment/build orchestration;
- PostgreSQL management;
- a bespoke frontend SPA;
- copied forks of complete Odoo Website/eLearning templates;
- permanent compatibility support for both `website_facodi` and `theme_facodi`;
- redesigning FACODI around the Open2 lime/black palette.

## Acceptance criteria

The evolved theme is accepted when all of the following are true:

1. the installable addon follows Odoo 19 design-theme conventions under `theme_facodi`;
2. the recognizable `edu-open2` FACODI purple/blue identity remains dominant;
3. standard Website Builder editing remains functional and authoritative;
4. header/footer use standard Odoo mechanisms wherever possible;
5. homepage composition is editable and snippet-based rather than a hard-coded application shell;
6. `website_slides` remains the authoritative eLearning implementation;
7. no FACODI business addon is required to install the baseline theme;
8. no ad-hoc `sudo().search(...)` exists in theme QWeb for course discovery;
9. assets are separated by responsibility and integrated through Odoo theme asset mechanisms;
10. clean-install and key-route regression tests pass on Odoo 19;
11. existing editor-created Website content is preserved through the evolution;
12. the implementation remains small enough to track upstream Odoo theme patterns without creating a parallel frontend framework.
