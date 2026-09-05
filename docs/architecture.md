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
| `website.scss` | FACODI shell, header, footer, focus behavior |
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
- native primary QWeb page compositions registered declaratively;
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

The nine FACODI blocks are standard editable snippets. Their initial copy is
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

## Native New Page templates

Ten compositions are declared under the `facodi` picker group, using fully qualified
`theme_facodi.s_facodi_*` names. No manifest-driven generator is run.
`page_templates.xml` registers the FACODI picker group and primary
`new_page_template_sections_facodi_*` QWeb compositions. These call the theme snippets directly through native `t-snippet-call`; they are not `website.page` records.

The Odoo 19 `_generate_primary_page_templates` implementation formats two `%s`
placeholders with `snippet_key.split('.')`, a list, for qualified snippet names.
A fresh install reproduced `TypeError: not enough arguments for format string`.
Until upstream converts that list to a tuple, the small declarative composition
views use the same native section keys and call the theme snippets directly.
The generator also cannot resolve theme template records as ordinary view parents
before activation; direct calls avoid empty generated wrapper views. No core patch, ORM override or controller
is introduced. The regression suite exercises `/website/get_new_page_templates`,
renders all compositions, creates a standard page with their HTML and verifies
that theme reloading preserves saved editorial changes.

Theme activation copies presentation templates into website-specific views;
created pages own their rendered section HTML independently. Native menu recursion
now comes from `website.submenu`, retaining active state, visibility, external
window targets, dropdowns and mega menus under standard Website behavior.

## Presentation layers

Palette → CSS tokens → lead/actions/section/grid/panel primitives → components →
editable snippets → native page compositions. Standard Bootstrap forms, alerts and
pagination receive shared radii while preserving semantic colors and behavior.
The header and footer retain the existing FACODI design. Focus uses an ink outline
and white outer ring to remain visible on both light and dark surfaces. Color
combinations and editorial course backgrounds remain under standard editor control.

Historical specs and plans dated before this finalization are superseded wherever
they conflict with this architecture, especially the initial purple prototype,
partial OS-driven dark styling and a three-snippet-only scope.

The existing-theme upgrade also reproduced an invalid-parent error in
`_generate_primary_snippet_templates`: theme XML IDs identify `theme.ir.ui.view`
records, but this generator interprets their IDs as ordinary `ir.ui.view` IDs.
Removing the generator call and duplicated manifest composition declarations fixes
both installation and active-theme upgrades while retaining the standard picker.
The theme provides starting compositions, not automatic editorial page publication.

The website values palette is a one-item native preset list, making FACODI the
active default rather than leaving Odoo's default preset selected. The sole
upstream purple literal in SCSS is an exact selector for the stock persisted
course gradient: only that default becomes Ink → Blue. Other editorial gradients
and cover images are preserved. No course data is rewritten.
