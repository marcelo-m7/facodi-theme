# Validation — 2026-09-05

## Environment and scope

Started from main `404072b` (live FACODI identity). Validation uses disposable
PostgreSQL 16 and Odoo 19.0 Community (19.0-20260817), with design-themes pinned at
`a1818df4ade65406c0cacae8b1ea676e6f70095f`. Local browser runtime uses port 8079;
the existing development runtime on 8069 and Odoo Online were not modified.

## Automated evidence

- Theme-only clean install and upgrade: passed.
- Native Odoo i18n contract: passed with English as QWeb source and catalogues for `pt_PT`, `es_ES` and `fr_FR`.
- Runtime translation tests activate the three translated languages in a disposable Website, keep English as the default language, load the PO catalogues through `ir.module.module._update_translations()` and apply the theme through the standard Odoo theme lifecycle.
- Standard localized Website routes `/pt`, `/es` and `/fr` return translated FACODI shell copy; `/` remains English.
- Website-specific copies of the Hero and Learning Journey snippets retain translations after theme application, including copy that sits alongside decorative icons and card layout markup.
- The multilingual suite passes both on clean installation and after `-u theme_facodi`; the successful Odoo run reports zero failures and zero errors.
- Independent Learning clean install and upgrade: passed.
- Both addons clean install: passed; final combined upgrade **33 tests**, zero failures/errors (8 theme + 25 Learning) in the earlier integration matrix.
- Compiled frontend stylesheets fetched over HTTP; no Sass error CSS. Native default color combination uses Paper and Ink. The stock inline course gradient becomes Ink/Blue while editorial images remain intact.
- Contract script: passed; QWeb, manifests, snippets, no runtime database IDs or Enterprise dependency.
- Native page picker: all **10 compositions** render three editable FACODI sections.
- A page created through `website.new_page`, edited and reloaded through the native theme lifecycle retains its editorial HTML.
- Database created from old main, containing a manual page, transcript, result and approved mapping: upgrade preserved those records and their values.

Reproduction in a Community environment with the documented addons paths:

```sh
bash tests/test_module_contract.sh
bash tests/test_i18n_contract.sh
odoo -d facodi_test -i theme_facodi --without-demo=True --workers=0 --test-tags /theme_facodi --stop-after-init
odoo -d facodi_test -u theme_facodi --without-demo=True --workers=0 --test-tags /theme_facodi --stop-after-init
```

The CI translation test deliberately exercises the standard Odoo flow rather
than a FACODI-specific language implementation. It activates `pt_PT`, `es_ES`
and `fr_FR`, loads the module translations, makes English the Website default,
and reapplies the theme so translations stored on `theme.ir.ui.view` are
propagated to the Website-specific `ir.ui.view` copies.

## Browser evidence

**45 route/viewport checks**, widths 1280, 768 and 390, without horizontal
overflow or server errors: ten starter pages, catalog, course, lesson, contact
and login. Also checked authenticated Portal, standard student enrollment,
quiz submission/completion and progress, dropdown and mobile navigation.

Website Builder was opened through the native preview; an About heading was
edited, saved and checked after page reload. Native page creation remains an
editorial action; installation does not publish starter pages automatically.

- [Homepage desktop](validation/final-home-desktop.png)
- [Homepage mobile](validation/final-home-mobile.png)
- [Course with FACODI default cover](validation/final-course-1280.png)
- [Saved Builder page](validation/builder-saved-about.png)
- [Standard quiz completion](validation/final-quiz-completed.png)

Screenshots use disposable demonstration content, not a copy of production.
The quiz screenshot predates the final default-cover palette correction; quiz
behavior was not changed. Automated CSS tests and the course screenshot cover
that correction. Manual keyboard/focus inspection is not a formal WCAG audit.

## Internationalization boundary

The addon ships translation catalogues; it does not force language activation
or the default language in every database where the reusable theme is
installed. FACODI deployment must enable/publish English, `pt_PT`, `es_ES` and
`fr_FR` with standard Website configuration and select English as the default.

Odoo 19 keeps `theme.ir.ui.view.name` as a non-translatable technical field.
Accordingly, New Page composition names remain English instead of introducing a
parallel custom translation mechanism. Visible template copy, translatable
attributes and Website Builder snippet strings use native Odoo i18n.

## Live-site boundary

Read-only inspection found Odoo Online Enterprise with `theme_default`, not
these Community addons. Preserve the live editorial pages during any future
migration. The live contribution form targets a Studio model; this theme uses
the standard contact route and does not silently recreate that business model.
Odoo Online deployment and bulk editorial migration are not part of these PRs.
CI install/upgrade runs are attached to the PR; this report does not substitute
local test results for GitHub Actions results.
