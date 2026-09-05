# FACODI Theme Architecture

## Architectural boundary

`theme_facodi` is a presentation-only Odoo 19 Community addon.

```text
Odoo 19 Community
├── website + Website Builder
├── portal
├── website_slides
└── theme_common (pinned from odoo/design-themes)
          │
          ▼
     theme_facodi
     ├── live FACODI palette
     ├── dynamic header and footer
     ├── editable FACODI snippets
     └── eLearning presentation
```

Website owns pages and menus, Portal owns identity navigation, and eLearning
owns courses and progress. The theme supplies no parallel controller, model or
business workflow.

## Live-source evidence

The visual authority is the FACODI website at `edu-open2.odoo.com`, database
`edu-open2`, website id 2. Inspection on 2026-09-05 established this source
state:

| Odoo record | Role in the live site |
|---|---|
| installed module `theme_default` | standard base theme |
| attachment 431, `facodi-online.css` | FACODI visual rules |
| view 2477, `codoo.facodi_online.header` | dynamic header |
| view 2478, `codoo.facodi_online.footer` | FACODI footer |
| view 2479, `codoo.facodi_online.assets` | database stylesheet link |
| attachments 423, 424 and 775 | Website Builder palette and values |

These ids document provenance only. The addon never reads or references them at
runtime. The CSS attachment is decomposed into focused SCSS and the QWeb views
are represented with module-owned XML ids.

```text
edu-open2 database artifacts
          │ extract visual intent
          ▼
theme_facodi source files
          │ standard theme lifecycle
          ▼
any clean Odoo 19 Community website
```

The database URL `/web/content/431`, duplicate YouTube hook and editorial page
records are not copied. They are respectively a deployment artifact, behavior
outside the theme boundary and site content.

## Source ownership

| File | Responsibility |
|---|---|
| `primary_variables.scss` | exact live palette and Website Builder combinations |
| `bootstrap_overridden.scss` | geometric Bootstrap radii |
| `components.scss` | wordmark, buttons, cards and reusable primitives |
| `website.scss` | FACODI shell, header, footer, focus and color-scheme behavior |
| `snippets.scss` | editable hero, journey and institutional compositions |
| `website_slides.scss` | presentation of stable standard eLearning selectors |
| `customizations.xml` | layout hook, dynamic header/footer and Portal templates |
| `snippets.xml` | Builder registration and editable snippet markup |

Frontend SCSS uses CSS custom properties under `.facodi-site`. This keeps the
live cyan, blue, mint and sun accents available without coupling frontend
bundles to theme-primary Sass compilation internals.

## Odoo theme lifecycle

The addon follows Odoo design-theme conventions:

- technical module name `theme_facodi`;
- `theme_common` sourced from official `odoo/design-themes`;
- primary variables registered in `web._assets_primary_variables`;
- Bootstrap overrides registered in `web._assets_frontend_helpers`;
- `_generate_primary_snippet_templates` executed during installation;
- theme QWeb copied into website-specific views when the theme is activated.

The build currently pins `odoo/design-themes` commit:

```text
a1818df4ade65406c0cacae8b1ea676e6f70095f
```

## Header and footer

The live layout cannot be reproduced by palette changes alone. The addon
therefore replaces only the standard `header` and `#footer` extension points.
It does not hard-code `website.menu` ids:

- top-level and child items come from `website.menu_id.child_id`;
- URLs use standard menu helpers;
- sign-in and account navigation call standard Portal templates;
- mobile collapse uses Bootstrap behavior already shipped by Website;
- footer navigation is derived from the same current Website menu.

No JavaScript is added for navigation.

## Website Builder and editorial content

The three FACODI blocks are standard editable snippets. Their initial copy is
translatable and their links use `/slides`, `/contactus` and `/web/login`, all
standard routes available from declared dependencies.

The theme intentionally creates no `website.page` records. Existing FACODI
pages such as Homepage, About, Manifesto, Community and Roadmap remain database
content and can evolve independently of theme releases.

Configured Website logos and favicons remain authoritative. Bundled SVG files
are previews or optional assets and are never injected over Website settings.

## eLearning

`website_slides` remains authoritative for the catalog, channel, lesson,
membership and progress surfaces. Rules are scoped through
`body.o_wslides_body .facodi-site` and target stable standard classes. There are
no duplicate routes or QWeb data queries.

## Upgrade discipline

For future changes, use this order:

1. configure a standard Website/Bootstrap theme value;
2. style a stable standard class;
3. inherit a focused QWeb extension point;
4. add a reusable FACODI snippet only when standard snippets are insufficient.

Changes to visual tokens require source-contract assertions. Changes to
rendered layout require `HttpCase` coverage on a clean database. Every release
must compile assets and exercise both `/` and `/slides` in Odoo 19 Community.
