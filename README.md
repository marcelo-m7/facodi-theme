# FACODI Theme

`facodi-theme` provides the Odoo 19 Community theme addon **`theme_facodi`** for the FACODI Website and eLearning experience.

The repository is presentation-only. It preserves Odoo Website Builder and `website_slides` as the functional authorities and adds the FACODI visual system, editable FACODI snippets, narrow layout inheritance and eLearning presentation refinements.

## Runtime dependencies

The addon depends only on:

- `theme_common`, supplied by a pinned Odoo 19-compatible checkout of `odoo/design-themes`;
- `website_slides`, supplied by Odoo Community.

There is no dependency on `facodi_learning` or another FACODI business addon.

## Visual identity

The current `https://edu-open2.odoo.com` experience is the visual authority. The implementation baseline uses:

- Purple: `#6a4bff`
- Blue: `#5dc7ff`
- Surface: `#f7f6ff`
- Ink: `#1f1e42`
- Heading ink: `#111035`

The colors are integrated into Odoo theme palettes and color combinations so standard Website Builder sections and controls remain coherent.

## Standard-first behavior

- Website Builder owns editable pages, menus, snippets, color combinations, header/footer choices, logo and favicon.
- `website_slides` owns course catalog, channels, lessons, membership, progress and routes.
- The theme does not add parallel learning controllers or business models.
- QWeb contains no ad-hoc business-data queries.
- Standard header/footer templates are not copied or replaced wholesale.
- The bundled logo/favicon files are optional project assets; the theme does not force them over Website settings.
- Custom JavaScript is intentionally absent from the baseline theme.

## Website Builder snippets

The initial FACODI group provides editable blocks for:

- FACODI Hero;
- Learning Journey (`Descubra → Aprenda → Contribua`);
- Institutional presentation.

Standard Odoo snippets should be preferred whenever they already satisfy a page-composition need.

## Installation

Make Odoo core, the pinned `odoo/design-themes` checkout and this repository available on `addons_path`:

```bash
odoo -d facodi \
  --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/opt/odoo-design-themes,/path/to/facodi-theme \
  -i theme_facodi \
  --stop-after-init
```

The CI pins `odoo/design-themes` commit `a1818df4ade65406c0cacae8b1ea676e6f70095f` for the current implementation cycle.

## Verification

GitHub Actions uses PostgreSQL 16 and the official `odoo:19.0` image to:

- resolve the pinned `theme_common` source;
- install `theme_facodi` on a clean database;
- compile frontend/theme assets;
- run the addon `HttpCase` suite;
- verify `/` and `/slides` remain standard working surfaces;
- verify the standard Website favicon is not replaced by a hard-coded theme asset.

The repository contract can also be checked with:

```bash
bash tests/test_module_contract.sh
```

## Monorepo integration

`marcelo-m7/facodi-monorepo` consumes this repository as a pinned Git submodule at `addons/facodi-theme`. The monorepo is responsible for immutable image composition, deployment and for making the pinned `theme_common` dependency available at runtime.

## License

LGPL-3.0.
