# Validation — 2026-09-05

## Environment and scope

Started from main `404072b` (live FACODI identity). Validation uses disposable
PostgreSQL 16 and Odoo 19.0 Community (19.0-20260817), with design-themes pinned at
`a1818df4ade65406c0cacae8b1ea676e6f70095f`. Local browser runtime uses port 8079;
the existing development runtime on 8069 and Odoo Online were not modified.

## Automated evidence

- Theme-only clean install and upgrade: passed; latest suite **8 tests**.
- Independent Learning clean install and upgrade: passed.
- Both addons clean install: passed; final combined upgrade **33 tests**, zero failures/errors (8 theme + 25 Learning).
- Compiled frontend stylesheets fetched over HTTP; no Sass error CSS. Native default color combination uses Paper and Ink. The stock inline course gradient becomes Ink/Blue while editorial images remain intact.
- Contract script: passed; QWeb, manifests, snippets, no runtime database IDs or Enterprise dependency.
- Native page picker: all **10 compositions** render three editable FACODI sections.
- A page created through `website.new_page`, edited and reloaded through the native theme lifecycle retains its editorial HTML.
- Database created from old main, containing a manual page, transcript, result and approved mapping: upgrade preserved those records and their values.

Reproduction in a Community environment with the documented addons paths:

```sh
bash tests/test_module_contract.sh
odoo -d facodi_test -i theme_facodi --without-demo=True --workers=0 --test-tags /theme_facodi --stop-after-init
odoo -d facodi_test -u theme_facodi --without-demo=True --workers=0 --test-tags /theme_facodi --stop-after-init
```

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

## Live-site boundary

Read-only inspection found Odoo Online Enterprise with `theme_default`, not
these Community addons. Preserve the live editorial pages during any future
migration. The live contribution form targets a Studio model; this theme uses
the standard contact route and does not silently recreate that business model.
Odoo Online deployment and bulk editorial migration are not part of these PRs.
CI install/upgrade runs are attached to the PR; this report does not substitute
local test results for GitHub Actions results.
