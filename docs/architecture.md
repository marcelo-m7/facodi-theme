# FACODI Theme Architecture

## Architectural boundary

`theme_facodi` is a presentation-only Odoo 19 Community theme addon.

```text
Odoo 19 Community
├── website + Website Builder
├── portal
├── website_slides
└── theme_common (pinned from odoo/design-themes)
          │
          ▼
     theme_facodi
     ├── FACODI palette and visual tokens
     ├── selectable native header composition
     ├── FACODI footer
     ├── reusable editable snippets
     ├── native New Page compositions
     └── eLearning presentation
```

Website owns pages, menus, logos, favicons and Website Builder state. Portal owns
identity navigation. `website_slides` owns courses, lessons, enrolment and learner
progress. The theme does not add parallel controllers, authentication logic or
business-data models.

## Live-source evidence

The visual authority is the FACODI website at `edu-open2.odoo.com`, database
`edu-open2`, website id 2. Inspection on 2026-09-05 established this source
state:

| Odoo record | Role in the live site |
|---|---|
| installed module `theme_default` | standard base theme |
| attachment 431, `facodi-online.css` | FACODI visual rules |
| view 2477, `codoo.facodi_online.header` | dynamic header evidence |
| view 2478, `codoo.facodi_online.footer` | FACODI footer evidence |
| view 2479, `codoo.facodi_online.assets` | database stylesheet link |
| attachments 423, 424 and 775 | Website Builder palette and values |

These ids document provenance only. The addon never reads or references them at
runtime. The database CSS and QWeb artifacts were translated into maintainable
SCSS and module-owned templates.

```text
edu-open2 database artifacts
          │ extract visual intent
          ▼
theme_facodi source files
          │ standard Odoo theme lifecycle
          ▼
any clean Odoo 19 Community website
```

The database URL `/web/content/431`, duplicate behavior hooks and editorial page
records are deliberately absent from the reusable theme.

## Source ownership

| File | Responsibility |
|---|---|
| `static/src/scss/primary_variables.scss` | FACODI palette and Website Builder combinations |
| `static/src/scss/bootstrap_overridden.scss` | geometric Bootstrap radii |
| `static/src/scss/components.scss` | wordmark, buttons, cards and reusable primitives |
| `static/src/scss/website.scss` | FACODI shell, header/footer styling and focus behavior |
| `static/src/scss/snippets.scss` | FACODI editable blocks and compositions |
| `static/src/scss/website_slides.scss` | presentation of standard eLearning surfaces |
| `views/header.xml` | selectable FACODI desktop header composition plus native mobile header call |
| `static/src/builder/header.xml` | FACODI entry in the native Website header picker |
| `models/theme_models.py` | `theme.utils` registration and post-copy activation hook |
| `views/customizations.xml` | FACODI shell metadata and footer |
| `views/snippets/s_facodi_*.xml` | one stable source file per reusable FACODI snippet |
| `views/snippets/snippets.xml` | Website Builder snippet registry |
| `views/page_templates.xml` | ten native New Page compositions |

Frontend SCSS uses CSS custom properties under `.facodi-site`. This keeps the
FACODI accents available without coupling frontend bundles to database-specific
assets.

## Odoo theme lifecycle

The addon follows Odoo design-theme conventions:

- technical module name `theme_facodi`;
- `theme_common` sourced from official `odoo/design-themes`;
- primary variables registered in `web._assets_primary_variables`;
- Bootstrap overrides registered in `web._assets_frontend_helpers`;
- Website Builder extensions registered through `html_builder.assets`;
- theme QWeb copied into website-specific views by the standard theme lifecycle;
- `_theme_facodi_post_copy()` activates the FACODI header template on theme copy.

The build pins `odoo/design-themes` commit:

```text
a1818df4ade65406c0cacae8b1ea676e6f70095f
```

## Native header ownership

The FACODI header is a native selectable Website header variant, not a replacement
for the complete outer Odoo header.

`theme_facodi.template_header_facodi` inherits `website.layout` and replaces only
`//header//nav`, the same focused extension point used by standard Odoo header
templates. It keeps the outer `<header>` and adds only the `facodi-header` class.
The template is registered through `theme.utils._header_templates`, while
`static/src/builder/header.xml` extends `website.HeaderTemplateOption` so editors
can select FACODI from the normal header picker.

Desktop composition uses standard primitives:

- `website.navbar` owns the navbar shell;
- `website.placeholder_header_brand` owns the configured Website logo/brand;
- `website.navbar_nav` owns the navigation wrapper;
- menu items come from `website.menu_id.child_id`;
- `website.submenu` owns nested menus, active state, external targets and mega-menu behavior;
- `portal.placeholder_user_sign_in` owns public sign-in;
- `portal.user_dropdown` owns authenticated account navigation.

The FACODI desktop navbar is hidden below the standard `lg` breakpoint. Mobile
navigation is delegated to `website.template_header_mobile`, preserving Odoo's
mobile menu, Website Builder behavior and integrations from other addons. No
custom JavaScript navigation system is introduced.

The footer remains a focused FACODI presentation override of `#footer`, using the
current Website menu records and standard routes.

## Website Builder and reusable snippets

The nine FACODI blocks are standard editable snippets with stable XML ids:

- `s_facodi_hero`;
- `s_facodi_learning_journey`;
- `s_facodi_institutional`;
- `s_facodi_intro`;
- `s_facodi_features`;
- `s_facodi_community`;
- `s_facodi_roadmap`;
- `s_facodi_faq`;
- `s_facodi_course_cta`.

Each block has one source file under `views/snippets/` and one registry entry in
`views/snippets/snippets.xml`. Keeping the XML ids stable preserves page
compositions and Odoo translation identity while removing the former monolithic
`views/snippets.xml` file.

Default links use standard routes available from declared dependencies, notably
`/slides` and `/contactus`. The theme intentionally creates no editorial
`website.page` records.

Configured Website logos and favicons remain authoritative. Bundled SVG files are
preview assets and are never forced over Website settings.

## Native New Page templates

Ten compositions are declared under the FACODI picker group using fully qualified
`theme_facodi.s_facodi_*` names. They reuse the same nine snippet templates rather
than duplicating section markup.

`page_templates.xml` registers the FACODI picker group and native
`new_page_template_sections_facodi_*` QWeb compositions. These are starting
compositions, not automatically published `website.page` records.

Odoo 19's primary-template generator currently has edge cases with qualified theme
snippet identifiers before theme activation. The implementation therefore keeps the
composition layer declarative and calls the registered theme snippets directly. No
core patch, ORM override or custom controller is introduced. Regression tests render
all compositions, exercise `/website/get_new_page_templates`, create a standard page
and verify that theme reload preserves saved editorial content.

## Internationalization

English is the canonical QWeb source language. Portuguese (`pt_PT`), Spanish
(`es_ES`) and French (`fr_FR`) are shipped through native Odoo PO catalogues. Theme
translations are propagated to website-specific view copies by the standard theme
lifecycle; no JavaScript language store or parallel language selector exists.

## eLearning

`website_slides` remains authoritative for catalog, channel, lesson, membership and
progress surfaces. Theme rules target standard presentation classes only. There are
no duplicate eLearning routes or QWeb business-data queries.

## Upgrade discipline

For future changes, use this order:

1. configure a standard Website/Bootstrap theme value;
2. style a stable standard class;
3. inherit a focused QWeb extension point;
4. add a reusable FACODI snippet only when standard snippets are insufficient.

Visual-token changes require source-contract assertions. Rendered-layout changes
require `HttpCase` coverage on a clean database. Every release must compile assets
and exercise clean install and module upgrade in Odoo 19 Community.

Historical specs and plans dated before this finalization are superseded wherever
they conflict with this architecture, especially complete-header replacement,
partial OS-driven dark styling and the earlier monolithic snippet layout.
