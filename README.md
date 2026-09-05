# FACODI Theme

`facodi-theme` provides the Odoo 19 Community addon **`theme_facodi`** for
FACODI Website and eLearning presentation.

The public Website at [edu-open2.odoo.com](https://edu-open2.odoo.com) is the
visual source of truth. Release `19.0.4.0.0` completes the reusable presentation library while preserving
the identity active in that Odoo instance.

## Verified visual identity

The live site uses Odoo `theme_default` plus Website Builder customizations.
Those database artifacts were inspected through the Odoo API and translated
into maintainable QWeb and SCSS; they are evidence, not runtime dependencies.

| Role | Color |
|---|---|
| Ink | `#142846` |
| Cyan | `#37BED2` |
| Blue | `#3979C8` |
| Mint | `#A7E8BE` |
| Sun | `#EFFF00` |
| Paper | `#F9FAFB` |

The visual language uses strong ink borders, offset shadows, geometric cards,
bright calls to action and responsive layouts. Font stacks prefer Space
Grotesk, Inter and JetBrains Mono when already available and fall back to
system fonts without making remote font requests.

## What the addon provides

- Website Builder palette and semantic color combinations;
- FACODI wordmark, buttons, cards and visual tokens;
- responsive dynamic header using standard `website.menu` records;
- standard Portal sign-in and user dropdown;
- dynamic footer using Website menu records and standard routes;
- nine editable FACODI snippets and ten native New Page compositions;
- presentation-only refinements for standard `website_slides` surfaces;
- accessible two-color focus indicators and reduced-motion behavior;
- optional preview, logo and favicon assets.

The addon **does not import Website pages**. It does not overwrite Homepage,
About, Manifesto, Community, Roadmap or other editorial content. It also does
not add controllers, course models, authentication logic or business-data
queries in QWeb.

## Standard-first ownership

- Website Builder owns pages, menus, translations, section editing, configured
  logos and favicons.
- `website_slides` owns `/slides`, courses, lessons, enrolment and learner
  progress.
- Portal owns sign-in and user navigation.
- `theme_facodi` owns only the presentation layer.

The former live database link `/web/content/431` is deliberately absent from
the addon. Its `facodi-online.css` contents are represented by versioned SCSS,
and no database-specific record id is required after installation.

## Runtime dependencies

The module depends only on:

- `theme_common`, from a pinned Odoo 19-compatible checkout of
  `odoo/design-themes`;
- `website_slides`, supplied by Odoo Community.

There is no dependency on Odoo Enterprise or on a FACODI business addon.

## Installation

Make Odoo core, the pinned `odoo/design-themes` checkout and this repository
available on `addons_path`:

```bash
odoo -d facodi \
  --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/opt/odoo-design-themes,/path/to/facodi-theme \
  -i theme_facodi \
  --stop-after-init
```

For an existing installation, deploy the new source and update the module:

```bash
odoo -d facodi \
  --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/opt/odoo-design-themes,/path/to/facodi-theme \
  -u theme_facodi \
  --stop-after-init
```

Activate or reapply the theme from Website settings after testing in a staging
database. Page content remains separate, but an intentionally customized local
header or footer should be reviewed before theme activation.

## Verification

Run the fast repository contract:

```bash
bash tests/test_module_contract.sh
```

GitHub Actions then uses PostgreSQL 16 and the official `odoo:19.0` image to:

- resolve pinned `odoo/design-themes` commit
  `a1818df4ade65406c0cacae8b1ea676e6f70095f`;
- install `theme_facodi` on a clean database;
- compile frontend and theme assets;
- run the addon `HttpCase` suite;
- verify native menus, `/`, `/slides`, `/contactus` and `/web/login`;
- render all ten native compositions and create a page with preserved editor content;
- rerun regression tests on module upgrade;
- confirm that the configured Website favicon is not replaced.

## Repository integration

`marcelo-m7/facodi-monorepo` can consume this repository as a pinned Git
submodule. Image composition and deployment remain responsibilities of the
monorepo; this repository contains only the installable presentation addon.

## License

LGPL-3.0.

## Builder library and page compositions

Choose **New → Page → FACODI** to create a page from a composition. The theme
registers templates; it creates no editorial pages automatically. Edit the
new page using standard Website Builder and save normally. Course and contact
links point to the canonical `/slides` and `/contactus` routes.

| Composition | Snippets |
|---|---|
| Home | Hero, Learning Journey, Course CTA |
| About | Editorial Intro, Institutional, Features |
| Manifesto | Editorial Intro, Institutional, Community |
| How | Editorial Intro, Learning Journey, FAQ |
| Community | Editorial Intro, Community, FAQ |
| Pathways | Editorial Intro, Learning Journey, Course CTA |
| Contribution | Editorial Intro, Features, Community |
| Roadmap | Editorial Intro, Roadmap, Community |
| Partners | Editorial Intro, Features, Community |
| Editorial | Editorial Intro, Features, Course CTA |

The nine blocks are Hero, Learning Journey, Institutional, Editorial Intro,
Features, Community/Contribution, Roadmap, FAQ and Course CTA. Compositions
provide editable starting copy, without invented partners, metrics or testimonials.
Publishers own final editorial text and URLs (including `/como-contribuir`).
FAQ uses native keyboard-accessible disclosure elements with no duplicate IDs.

Editorial course cover images remain visible. Website Builder color combinations
remain authoritative; the theme does not partially switch colors based on OS dark mode.
See [architecture](docs/architecture.md) for the native Odoo 19 generator workaround.

## Validation evidence

See [validation report](docs/validation.md) for the isolated Community install/upgrade matrix, browser checks and remaining deployment boundaries.
