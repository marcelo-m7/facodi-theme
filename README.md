# FACODI Theme

`facodi-theme` provides the Odoo 19 Community website theme addon **`website_facodi`**.

The repository is deliberately presentation-only. It applies the FACODI visual language through standard Odoo Website/eLearning theme mechanisms and does not contain FACODI learning-domain logic.

## Why the addon is named `website_facodi`

The Git repository remains `facodi-theme`, but the technical Odoo addon uses the `website_` prefix to follow Odoo 19 website-theme conventions.

```text
facodi-theme/               Git repository
└── website_facodi/         installable Odoo addon
```

## Standard-first implementation

- Depends on standard `website_slides`; no dependency on `facodi_learning`.
- Extends the Website Builder color palette instead of introducing an independent design system runtime.
- Loads primary theme variables through `web._assets_primary_variables`.
- Loads frontend styling through `web.assets_frontend`.
- Inherits `website.layout`; no copied Odoo page/header/footer templates.
- Keeps standard Website navigation, authentication, forms, eLearning routes, course membership and progress behavior.
- Adds no JavaScript because the current visual requirements do not need custom frontend behavior.
- Uses standard/system font fallbacks; no redistributable font binaries are committed.

## FACODI identity

The initial palette is derived from the existing FACODI web identity:

- Primary: `#6a4bff`
- Secondary: `#5dc7ff`
- Light surface: `#f7f6ff`
- Body text: `#1f1e42`
- Heading text: `#111035`

Project-owned logo and favicon SVG assets are stored under `website_facodi/static/src/img/`.

The theme intentionally does **not** replace the standard Website logo record. Administrators keep using Odoo's normal Website/Company branding controls; the bundled logo is available to provisioning/content code without taking ownership away from standard configuration.

## Installation

Add the repository root to `addons_path`, update the Apps list and install **FACODI Website Theme**.

```bash
odoo -d facodi -i website_facodi --stop-after-init
```

The addon can be installed with or without `facodi_learning`.

## Verification

GitHub Actions starts PostgreSQL 16 and installs `website_facodi` against the official `odoo:19.0` image on a clean database. The CI also forces Odoo to generate frontend assets and verifies that:

- the public homepage renders;
- the standard `/slides` eLearning catalog still renders;
- the FACODI layout class is present after QWeb inheritance;
- SCSS assets compile without errors.

## Monorepo contract

`marcelo-m7/facodi-monorepo` consumes this repository as a Git submodule at:

```text
addons/facodi-theme
```

The monorepo pins an exact commit and builds an immutable Odoo image. A change here does not deploy itself until the monorepo intentionally advances the submodule pointer.

## License

LGPL-3.0, aligned with the addon manifest.
