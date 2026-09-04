# FACODI Theme — Design

Date: 2026-09-04
Target: Odoo 19 Community
Repository: `marcelo-m7/facodi-theme`
Technical addon: `website_facodi`

## Purpose

FACODI Theme is the presentation-only addon for the FACODI visual identity across Odoo Website and eLearning. It is independently installable and contains no analysis, curriculum-mapping or other learning-domain business logic.

## Odoo 19 naming decision

The repository name stays `facodi-theme`, while the technical addon is `website_facodi`. The earlier draft name `facodi_theme` was replaced to follow Odoo's website-theme/module naming convention and make the module's responsibility explicit.

## Standard-first principles

1. Use Odoo Website Builder/theme variables before custom CSS.
2. Load palette variables through `web._assets_primary_variables` and frontend styles through `web.assets_frontend`.
3. Inherit `website.layout` rather than copying standard header/footer/page templates.
4. Preserve the dynamic classes Odoo puts on `#wrapwrap`; FACODI adds its class to the existing `t-attf-class`.
5. Keep standard Website logo/company branding configurable by administrators.
6. Keep standard `website_slides` routes, membership, permissions, progress and content rendering authoritative.
7. Use no JavaScript unless a future presentation requirement cannot be satisfied by standard Odoo/Bootstrap behavior.
8. No dependency on `facodi_learning`.

## Initial visual system

The initial palette follows the existing FACODI web identity: primary `#6a4bff`, secondary `#5dc7ff`, light surface `#f7f6ff`, body text `#1f1e42`, heading text `#111035`. It is registered as an Odoo color palette so standard components remain coherent with Website Builder.

Typography uses system-font fallbacks. No font binary is committed. Project-owned SVG logo/favicon assets are included.

## Asset architecture

```text
website_facodi/static/src/scss/
├── primary_variables.scss  Odoo Website Builder palette
├── theme.scss              global FACODI visual refinements
└── elearning.scss          standard website_slides visual refinements
```

## View architecture

`views/website_layout.xml` inherits `website.layout`, adds the `facodi-site` styling hook to the standard dynamic `#wrapwrap` class, and supplies theme-color/favicon metadata. Standard navigation/header/footer templates remain untouched.

The initial eLearning customization is CSS-only because standard `website_slides` markup already exposes suitable stable classes; duplicating or replacing QWeb templates would increase upgrade risk without adding functional value.

## Testing

CI installs `website_facodi` with its standard dependencies on a clean Odoo 19/PostgreSQL 16 database, compiles frontend asset bundles and uses an Odoo `HttpCase` to verify `/`, `/slides`, and the inherited FACODI layout hook.

## Monorepo contract

The repository root exposes exactly one installable Odoo addon directory, `website_facodi`. `facodi-monorepo` consumes the repository at `addons/facodi-theme` and pins an exact commit in each immutable application image.

## Out of scope

- FACODI learning/analysis models
- curriculum mapping
- external AI/provider integration
- custom authentication or navigation business logic
- deployment infrastructure
- Docker image publishing
- PostgreSQL management
- copied standard Website/eLearning templates
