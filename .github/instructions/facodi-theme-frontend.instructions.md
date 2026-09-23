---
name: "FACODI Odoo Theme Frontend"
description: "Use when changing the FACODI Odoo Website frontend, QWeb templates, Website Builder snippets, SCSS, theme assets, header, footer, or eLearning presentation in theme_facodi."
applyTo: "addons/facodi-theme/theme_facodi/**"
---
# FACODI Theme Frontend

- `facodi-theme` is an independently owned submodule. Make and validate changes here first; after its commit is published, update the `addons/facodi-theme` gitlink in the deploy repository.
- Read the [theme README](../../README.md), [architecture](../../docs/architecture.md), and [validation guide](../../docs/validation.md) before changing a cross-cutting frontend surface.

## Ownership Boundaries

- Keep `theme_facodi` presentation-only. Website Builder owns pages, menus, translations, logos, favicons, and editor state; Portal owns identity controls; `website_slides` owns courses, lessons, enrolment, progress, and routes.
- Do not add controllers, authentication, parallel course/page models, or ORM searches in QWeb. Keep catalogue presentation data in the existing read-only batch resolver.
- Preserve standard Odoo selectors, URLs, and JavaScript hooks on inherited eLearning views. Never make provider HTTP requests or persist derived thumbnails from theme code.

## QWeb and Builder

- Prefer focused QWeb inheritance and standard `website.*` and `portal.*` building blocks. Keep snippet XML IDs stable, put each reusable snippet in its own `views/snippets/s_facodi_*.xml` file, and reuse snippets in page compositions instead of copying markup.
- The header deliberately replaces the outer `//header`: Website Builder customizations may remove an inner `<nav>`. Do not target `//header//nav`, create a parallel mobile menu, or replace the standard mobile header call.
- Use native Odoo translations: English QWeb is the source and `i18n/*.po` supplies supported locales. Do not add per-language template branches or a JavaScript translation store.

## Styles and Assets

- Scope FACODI design tokens and component styling under `.facodi-site`; retain Website Builder control of global colors and heading styles.
- Put palette variables in `primary_variables.scss`, Bootstrap geometry overrides in `bootstrap_overridden.scss`, and register them through `data/ir_asset.xml`. Preserve the frontend asset order in `__manifest__.py`.
- Retain responsive layouts, visible `:focus-visible` states, and `prefers-reduced-motion` handling. Use the existing FACODI palette and local font stacks; do not add remote font requests.

## Validation

Run checks from `addons/facodi-theme`, choosing the narrowest relevant contract first:

```sh
bash tests/test_module_contract.sh
bash tests/test_homepage_dashboard_contract.sh
bash tests/test_foundation_v2_contract.sh
bash tests/test_i18n_contract.sh
bash tests/test_elearning_catalog_style_contract.sh
```

- For QWeb, header, resolver, asset-compilation, clean-install, or upgrade changes, run the repository CI gate as described in the [validation guide](../../docs/validation.md) before advancing the deploy gitlink.