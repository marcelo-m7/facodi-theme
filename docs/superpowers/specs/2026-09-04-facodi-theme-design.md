# FACODI Theme — Design

Date: 2026-09-04
Target: Odoo 19 Community
Repository: `marcelo-m7/facodi-theme`

## Purpose

`facodi-theme` is the presentation-only Odoo addon responsible for FACODI visual identity across the public website and eLearning experience. It must not contain video-analysis, curriculum-mapping or other FACODI business logic.

The addon must be independently installable on an Odoo 19 Community database with the standard Website/eLearning applications.

## Architectural principles

1. Use Odoo's standard Website/theme mechanisms rather than replacing the Website application.
2. Keep branding, SCSS, templates, snippets and website-specific presentation concerns in this repository only.
3. Do not duplicate business models owned by Odoo or other FACODI addons.
4. Avoid hard-coded environment/domain values in templates.
5. Prefer inheritance of standard Odoo/QWeb views and reusable SCSS variables/components to copying full standard templates.
6. Preserve accessibility, responsive behavior and translation support.
7. The theme may visually enhance `website_slides`, but it must not require `facodi_learning`.

## Odoo module

Technical module name:

`facodi_theme`

Initial dependencies:

- `website`
- `website_slides`

The module must not depend on `facodi_learning`.

## Scope

The first complete repository provides a coherent FACODI theme foundation for:

- global typography
- color palette and semantic design tokens
- header/navigation
- footer
- buttons and links
- cards
- website sections
- forms
- alerts/badges
- eLearning course cards
- eLearning content/lesson presentation
- responsive layout adjustments
- FACODI reusable website snippets where standard blocks are insufficient

The implementation should allow the visual layer to evolve without changing learning-domain logic.

## Asset architecture

SCSS is organized by responsibility rather than as one large stylesheet:

```text
static/src/scss/
├── _variables.scss
├── _typography.scss
├── _components.scss
├── _website.scss
├── _elearning.scss
└── theme.scss
```

Static assets such as icons and project-owned images live under `static/src/img/`.

No external font binary is committed unless licensing and redistribution are explicitly approved. Prefer web-safe/system typography or runtime-loaded/licensed assets configured separately.

## View architecture

QWeb/XML templates are grouped by responsibility:

```text
views/
├── website_templates.xml
├── website_layout.xml
├── elearning_templates.xml
└── snippets.xml
```

Theme inheritance should target stable standard template extension points. Full replacement of an upstream template is avoided unless inheritance cannot achieve the required result.

## Design tokens

FACODI identity is expressed through semantic variables rather than repeated literal styling values.

Token groups include:

- primary/secondary/accent surfaces
- text and muted text
- borders
- background surfaces
- success/warning/error/info semantics
- border radius
- spacing conventions
- typography scale
- container behavior

Odoo/Bootstrap primitives should be reused where practical so standard components remain visually coherent.

## Website behavior

The theme must not introduce business actions through JavaScript merely for styling. JavaScript is included only when required for presentation behavior that cannot be implemented through standard Odoo/Bootstrap behavior.

Any JavaScript added must be small, progressive-enhancement oriented and covered by an explicit reason in documentation.

## eLearning integration

The theme may inherit standard `website_slides` templates to improve:

- course catalog presentation
- course hero/header
- lesson/content cards
- progress indicators
- navigation hierarchy
- mobile readability

It must not change content ownership, course membership logic, access control, completion rules or analysis behavior.

## Translation and accessibility

- User-facing strings are translatable through normal Odoo mechanisms.
- Interactive controls preserve accessible labels/focus behavior.
- Visual contrast should be sufficient for primary text and actionable elements.
- Templates use semantic HTML where possible.
- Responsive behavior must be tested at mobile and desktop widths.

## Testing and verification

The repository must verify at minimum:

- module installs on a clean Odoo 19 Community database with Website/eLearning dependencies
- XML/QWeb templates load without errors
- assets compile successfully
- no dependency on `facodi_learning`
- public website route renders after installation
- standard eLearning pages still render after theme installation

CI must not depend on production data or external secrets.

## Repository structure

```text
facodi-theme/
├── facodi_theme/
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── views/
│   ├── data/
│   ├── static/src/scss/
│   ├── static/src/img/
│   ├── static/src/js/
│   └── tests/
├── .github/workflows/
│   └── ci.yml
├── docs/
│   └── architecture.md
├── .gitignore
├── LICENSE
└── README.md
```

## Public contract with `facodi-monorepo`

The repository root contains exactly one installable Odoo addon directory named `facodi_theme` plus repository-level documentation/CI files.

`facodi-monorepo` consumes this repository as a Git submodule under:

`addons/facodi-theme`

The monorepo pins an exact commit. Updating this repository does not update a running environment until the monorepo intentionally advances its submodule pointer and builds a new immutable image.

## Out of scope

- video analysis
- AI/provider integration
- curriculum mapping
- deployment infrastructure
- Docker image publishing
- PostgreSQL management
- replacement of Odoo Website/eLearning business models

These boundaries keep theme changes visually focused and allow FACODI learning functionality to evolve independently.
