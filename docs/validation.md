# Validation — 2026-09-05

## Environment and scope

Validation uses disposable PostgreSQL 16 and Odoo 19.0 Community
(`19.0-20260817`) with `odoo/design-themes` pinned at
`a1818df4ade65406c0cacae8b1ea676e6f70095f`. The public Odoo Online FACODI site
was used only as visual evidence and was not modified by this work.

Release under validation: `theme_facodi` `19.0.5.0.0`.

## Final automated evidence

The GitHub Actions run `33984540676` validated commit
`aa67c089940cbabbc41a6933b4956c66ac7e972f` successfully before the final
documentation-only edits. That run executed the repository contracts, a clean
Odoo installation and a module upgrade against the same database.

The Odoo output reports **17 addon tests**, with **0 failed** and **0 errors** on
both clean installation and upgrade.

Validated behavior includes:

- repository contract and native Odoo i18n contract;
- clean installation of `theme_facodi` with official Odoo 19 Community;
- upgrade with `-u theme_facodi` on the installed database;
- compilation and HTTP retrieval of frontend assets without Sass failure;
- native theme lifecycle and `_theme_facodi_post_copy()` execution;
- FACODI header registered as `theme.ir.ui.view` and copied into the Website;
- desktop FACODI navigation built from standard Website menu/Portal primitives;
- standard `website.template_header_mobile` retained for mobile navigation;
- nested and external Website menu behavior preserved through `website.submenu`;
- configured Website brand/logo and favicon ownership preserved;
- nine reusable FACODI snippets registered from independent source files;
- all ten native New Page compositions render their reusable snippets;
- a standard Website page can be created and edited without theme reload losing its editorial HTML;
- `/`, `/slides`, `/contactus` and `/web/login` render successfully;
- native Odoo translations for Portuguese (`pt_PT`), Spanish (`es_ES`) and French (`fr_FR`);
- localized routes `/pt`, `/es` and `/fr` render translated FACODI content while English remains the source/default language in the test Website.

The regression suite explicitly rejects a complete `<header>` replacement and
requires the FACODI desktop navbar to coexist with the standard mobile header.
It also rejects reintroduction of the former monolithic snippet file or duplicate
snippet XML ids.

## Reproduction

With Odoo core, the pinned design-themes checkout and this repository available
on `addons_path`:

```sh
bash tests/test_module_contract.sh
bash tests/test_i18n_contract.sh
odoo -d facodi_test \
  --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/opt/odoo-design-themes,/path/to/facodi-theme \
  -i theme_facodi --without-demo=True --workers=0 \
  --test-tags /theme_facodi --stop-after-init
odoo -d facodi_test \
  --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/opt/odoo-design-themes,/path/to/facodi-theme \
  -u theme_facodi --without-demo=True --workers=0 \
  --test-tags /theme_facodi --stop-after-init
```

## Header-specific verification

The rendered Website shell contains the FACODI desktop navbar while preserving
the Odoo outer header. The template delegates brand rendering to
`website.placeholder_header_brand`, navigation to `website.navbar_nav` and
`website.submenu`, and identity controls to standard Portal templates.

Desktop is hidden below `lg`; mobile rendering is delegated to
`website.template_header_mobile`. This is deliberately different from the former
FACODI implementation that replaced the full header and carried its own collapse
behavior.

## Snippet and page-composition verification

The nine FACODI blocks have stable XML ids and exactly one source definition each.
`views/snippets/snippets.xml` is registry-only. The old
`theme_facodi/views/snippets.xml` file is removed.

The native New Page picker exposes ten FACODI compositions. Each composition calls
the same reusable snippets, so changing a snippet implementation does not require
copying another version into every starter page definition.

Default reusable content does not link to undefined project-specific pages. Course
and contact actions use the standard `/slides` and `/contactus` routes.

## Internationalization boundary

The addon ships translation catalogues; it does not force language activation or
the default language in every database where the reusable theme is installed.
FACODI deployment must enable/publish English, `pt_PT`, `es_ES` and `fr_FR` using
standard Website language configuration and choose English as the default when
that is the desired production policy.

Odoo 19 keeps `theme.ir.ui.view.name` as a non-translatable technical label, so New
Page composition names remain English. Visible QWeb copy and Website Builder strings
use native Odoo i18n.

## Browser evidence retained from the previous finalization pass

The earlier isolated browser matrix covered widths 1280, 768 and 390 across the
starter compositions, catalog, course, lesson, contact, login, authenticated Portal,
enrolment, quiz completion and progress. It found no horizontal overflow or server
errors in that matrix. Website Builder editing and save/reload behavior were also
checked in the disposable environment.

Existing screenshots under `docs/validation/` remain supporting visual evidence;
they use disposable demonstration content and are not production snapshots. Manual
keyboard/focus inspection is supporting evidence, not a formal WCAG audit.

## Live-site and deployment boundary

The live Odoo Online instance uses database-owned Website content and is not the
runtime target of this Community addon repository. Editorial pages, production data
and any Studio-specific forms remain migration/deployment concerns outside
`theme_facodi`.

The deployment repository must pin the merged `facodi-theme` commit explicitly as a
git submodule. Updating that pin is a separate integration step so a deployment can
only consume a theme revision that has already passed its own Odoo 19 CI.
