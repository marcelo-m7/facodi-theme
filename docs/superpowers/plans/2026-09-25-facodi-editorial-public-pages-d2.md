# FACODI D2 Editorial & Public Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend Campus Paper into FACODI's remaining public/editorial surfaces with reusable Website Builder components, native Odoo Blog/Contact integration, and a controlled production recomposition.

**Architecture:** `theme_facodi` remains presentation-only. D2 adds a focused editorial component stylesheet and reusable snippets, narrowly inherits native `website_blog` and `website.contactus` templates, and leaves actual editor-managed pages in the database. The owner repository is verified first; an exact theme SHA is then exercised in a disposable `facodi-deploy` runtime before production code promotion and live Website Builder recomposition.

**Tech Stack:** Odoo 19 Community, QWeb, Website Builder, `website_blog`, `website_form`, SCSS/CSS custom properties, native PO/POT i18n, Python/Odoo tests, Bash contracts, Git submodules, Docker Compose, Playwright/Chrome browser acceptance, Odoo MCP for controlled live recomposition.

**Spec:** `docs/superpowers/specs/2026-09-25-facodi-editorial-public-pages-d2-design.md`

## Global Constraints

- Target release: `theme_facodi 19.0.9.0.0`.
- Add `website_blog` as the only new explicit addon dependency; no Enterprise dependency.
- `theme_facodi` owns presentation, snippets and native template inheritance only.
- Website Builder/database content remains authoritative for About, Contribution, Manifesto, Partners and legal pages.
- `website_blog` remains authoritative for posts, tags, dates, authors, pagination, search and routes.
- `website.contactus` and native `website_form` submission remain authoritative for Contact.
- Do not import fixed editorial `website.page` records from the theme.
- Do not rewrite legal copy.
- Do not hard-code phone numbers, email addresses, physical addresses, partner lists, testimonials, subscriber counts, project metrics or other mutable live claims.
- English is canonical QWeb source; theme-owned copy must be in POT + PT/ES/FR.
- No Google Fonts, remote fonts, Tailwind runtime, Material Symbols or Stitch JavaScript.
- Preserve Website Builder editing, duplication, removal, ordering and upgrade persistence.
- Hard responsive gate: no page-level horizontal overflow at 320 px.
- Respect `prefers-reduced-motion`, keyboard focus and semantic heading/form behavior.
- Do not touch `facodi-learning` unless a real integration defect proves that theme-only ownership is insufficient.
- Do not merge `facodi-deploy/main` until the exact owner SHA passes disposable runtime/browser acceptance.

## File Structure

### Reusable D2 layer

- Create: `theme_facodi/static/src/scss/editorial_interfaces.scss` — project-story, principles, timeline, contribution board, bulletin hero, editorial quote, contact sheet and policy document.
- Create:
  - `theme_facodi/views/snippets/components/s_facodi_project_story.xml`
  - `theme_facodi/views/snippets/components/s_facodi_principles_ledger.xml`
  - `theme_facodi/views/snippets/components/s_facodi_process_timeline.xml`
  - `theme_facodi/views/snippets/components/s_facodi_contribution_board.xml`
  - `theme_facodi/views/snippets/components/s_facodi_bulletin_hero.xml`
  - `theme_facodi/views/snippets/components/s_facodi_editorial_quote.xml`
  - `theme_facodi/views/snippets/components/s_facodi_contact_sheet.xml`
  - `theme_facodi/views/snippets/components/s_facodi_policy_document.xml`
- Modify: `theme_facodi/views/snippets/snippets.xml`
- Modify: `theme_facodi/views/page_templates.xml`
- Modify: `theme_facodi/__manifest__.py`

### Native public applications

- Create: `theme_facodi/views/website_blog.xml` — narrow inheritance of Odoo 19 Blog index/posts/article templates.
- Create: `theme_facodi/static/src/scss/website_blog.scss`.
- Create: `theme_facodi/views/website_public.xml` — narrow Contact inheritance only; legal pages remain class/snippet driven.
- Create: `theme_facodi/static/src/scss/website_public.scss`.
- Modify: `theme_facodi/__manifest__.py`.

### Tests and docs

- Create: `tests/test_editorial_interfaces_contract.sh`.
- Create: `tests/test_blog_contract.sh`.
- Create: `tests/test_public_pages_contract.sh`.
- Modify: `tests/test_module_contract.sh`.
- Modify: `tests/test_i18n_contract.sh`.
- Modify: `tests/test_mobile_interaction_contract.sh`.
- Modify: `theme_facodi/tests/test_website.py`.
- Modify: `.github/workflows/ci.yml`.
- Modify: `README.md`, `docs/validation.md`.
- Modify POT/PO catalogues when new source strings are introduced.

### Deployment / live composition

- `facodi-deploy`: integration branch updates only `addons/facodi-theme` to the exact green D2 SHA plus D2 browser assertions.
- Production Website pages are recomposed through Odoo MCP only after the new theme code is available on production.
- No live page arch/content is committed back into `facodi-theme`.

## Review Focus

1. **Existing About/Contribution page has editor-authored blocks not represented by the new composition** — live recomposition must preserve meaningful content or explicitly map it before replacing layout; Task 8 backs up/read-compares current page arch before mutation.
2. **Blog post has no cover, author, subtitle or tags** — D2 article/card styling must collapse cleanly without empty fake metadata; Task 4 creates posts with sparse and rich metadata and checks both.
3. **Contact page has been customized in Website Builder** — inheritance must target stable `website.contactus` hooks and preserve `#contactus_form`, action `/website/form/`, native field names and validation; Task 5 tests the actual rendered form.
4. **Legal page contains a long URL/table/code block at 320 px** — policy shell must wrap/scroll internally and never widen the document; Tasks 1, 5 and 7 pin source/browser overflow behavior.
5. **Translated editorial heading is substantially longer in PT/ES/FR** — snippets, timeline labels, cards and blog/contact hero copy must wrap without overlap; Tasks 1, 6 and 7 exercise long-text/i18n/mobile contracts.

---

### Task 1: Build the reusable D2 editorial component library

**Repository:** `marcelo-m7/facodi-theme`

**Files:**
- Create: `theme_facodi/static/src/scss/editorial_interfaces.scss`
- Create the eight component XML files listed in File Structure.
- Create: `tests/test_editorial_interfaces_contract.sh`
- Modify: `theme_facodi/views/snippets/snippets.xml`
- Modify: `theme_facodi/__manifest__.py`
- Modify: `tests/test_module_contract.sh`
- Modify: `tests/test_mobile_interaction_contract.sh`

**Interfaces:**
- Consumes: existing Campus Paper tokens/primitives and component conventions.
- Produces stable component classes:
  - `.facodi-project-story`
  - `.facodi-principles-ledger`
  - `.facodi-process-timeline`
  - `.facodi-contribution-board`
  - `.facodi-bulletin-hero`
  - `.facodi-editorial-quote`
  - `.facodi-contact-sheet`
  - `.facodi-policy-document`

- [ ] **Step 1: Write the failing D2 component contract**

Create `tests/test_editorial_interfaces_contract.sh` that fails until all eight XML snippets and eight SCSS selectors exist.

Also assert:

- all eight snippets are registered in the FACODI snippet group;
- `editorial_interfaces.scss` contains `min-width: 0`, `overflow-wrap: anywhere`, `@media (max-width: 767.98px)`, `:focus-visible`, and `prefers-reduced-motion`;
- no component XML contains phone-number-like placeholders, fake email addresses, fake street addresses, testimonial labels, subscriber counts or hard-coded partner logos;
- no component XML uses `request.env`, `.search(`, `.browse(` or `.sudo(`;
- no XML in `theme_facodi` imports `model="website.page"`.

- [ ] **Step 2: Run RED**

~~~bash
bash tests/test_editorial_interfaces_contract.sh
~~~

Expected: FAIL because D2 component files do not exist.

- [ ] **Step 3: Implement the eight snippets**

Each snippet is editable Website Builder content and uses only theme-owned starter copy.

Pinned structure:

- project story: kicker + title + prose + optional metadata/note + CTA;
- principles ledger: three editable principle cards;
- process timeline: four ordered editable steps;
- contribution board: three editable contribution paths with real default routes only (`/contribuir/recurso`, `/contactus`);
- bulletin hero: title/lead only, no metrics;
- editorial quote: blockquote + optional attribution field;
- contact sheet: two-column wrapper with contextual panel and a clearly marked editable/native-form slot; it must not implement a second form;
- policy document: prose wrapper + optional in-page anchor list shell, no legal copy.

- [ ] **Step 4: Implement D2 SCSS**

Use the existing semantic tokens and hard-shadow vocabulary.

Pinned responsive behavior:

- principles/contribution grids: 3 columns desktop → 2 tablet → 1 mobile;
- project story/contact sheet: two columns desktop → one column <= 767.98 px;
- policy/article prose max reading width around 50rem;
- long links use `overflow-wrap: anywhere`;
- tables/code are internally scrollable;
- decorative transforms are disabled under reduced motion.

- [ ] **Step 5: Load assets/snippets and bump release**

In `theme_facodi/__manifest__.py`:

- set version to `19.0.9.0.0`;
- add `website_blog` to `depends`;
- load all eight snippet XML files;
- load `editorial_interfaces.scss` after `paper_primitives.scss` and before page-specific editorial styles.

Update `tests/test_module_contract.sh` for the new release, dependency, snippet set and asset.

- [ ] **Step 6: Run GREEN**

~~~bash
bash tests/test_editorial_interfaces_contract.sh
bash tests/test_module_contract.sh
bash tests/test_mobile_interaction_contract.sh
~~~

Expected: PASS.

- [ ] **Step 7: Commit**

~~~bash
git add theme_facodi/__manifest__.py theme_facodi/views/snippets   theme_facodi/static/src/scss/editorial_interfaces.scss   tests/test_editorial_interfaces_contract.sh tests/test_module_contract.sh   tests/test_mobile_interaction_contract.sh
git commit -m "feat(theme): add D2 editorial component library"
~~~

---

### Task 2: Recompose the page-picker templates for About, How, Contribution, Manifesto and Partners

**Repository:** `marcelo-m7/facodi-theme`

**Files:**
- Modify: `theme_facodi/views/page_templates.xml`
- Modify: `tests/test_editorial_interfaces_contract.sh`
- Modify: `theme_facodi/tests/test_website.py`

**Interfaces:**
- Consumes: Task 1 component XML IDs.
- Produces builder compositions:
  - `new_page_template_sections_facodi_about`
  - `new_page_template_sections_facodi_how`
  - `new_page_template_sections_facodi_contribution`
  - `new_page_template_sections_facodi_manifesto`
  - `new_page_template_sections_facodi_partners`
  - existing community/editorial compositions updated where useful.

- [ ] **Step 1: Write failing composition assertions**

Require exact composition contents:

**About**
- intro;
- project story;
- principles ledger;
- process timeline;
- institutional;
- editorial routes;
- CTA sheet.

**How**
- intro;
- process timeline;
- FAQ;
- editorial routes.

**Contribution**
- intro;
- contribution board;
- process timeline;
- community;
- CTA sheet;
- editorial routes.

**Manifesto**
- intro;
- principles ledger;
- editorial quote;
- institutional;
- editorial routes.

**Partners**
- intro;
- ecosystem;
- paper/editorial content;
- community;
- editorial routes.

Assert all `t-snippet-call` keys resolve to registered theme snippets/components and that no fixed page records are created.

- [ ] **Step 2: Run RED**

~~~bash
bash tests/test_editorial_interfaces_contract.sh
~~~

Expected: FAIL because current compositions do not use D2 components.

- [ ] **Step 3: Update page-picker compositions**

Modify only template compositions; do not create canonical URL/page records.

Keep existing XML IDs stable so saved builder selections/automation do not break.

- [ ] **Step 4: Add Odoo render assertions**

In `test_website.py`, render the D2 composition views and assert the new semantic classes are present.

Add a negative assertion that creating/upgrading the theme does not create a new `website.page` whose URL matches `/sobre`, `/contribuir`, `/manifesto` or `/parceiros`.

- [ ] **Step 5: Extend persisted-editor upgrade gate**

Add a CI seed/verify pair for one disposable editor-owned page that contains a D2 component and a unique editor-authored marker.

On upgrade to `19.0.9.0.0`, assert:

- the page still exists;
- the unique editor marker remains;
- the D2 snippet call/markup remains;
- the theme did not overwrite the page with the page-picker template.

- [ ] **Step 6: Run GREEN**

Run D2 static contracts and exact-head Odoo CI legacy install/upgrade.

- [ ] **Step 7: Commit**

~~~bash
git add theme_facodi/views/page_templates.xml theme_facodi/tests/test_website.py   tests/test_editorial_interfaces_contract.sh tests/ci_*editorial*
git commit -m "feat(theme): compose D2 editorial page templates"
~~~

---

### Task 3: Add the native Odoo Blog / Campus Bulletin presentation

**Repository:** `marcelo-m7/facodi-theme`

**Files:**
- Create: `theme_facodi/views/website_blog.xml`
- Create: `theme_facodi/static/src/scss/website_blog.scss`
- Create: `tests/test_blog_contract.sh`
- Modify: `theme_facodi/__manifest__.py`
- Modify: `theme_facodi/tests/test_website.py`

**Interfaces:**
- Consumes stable Odoo 19 native templates:
  - `website_blog.blog_post_short`
  - `website_blog.posts_loop`
  - `website_blog.blog_post_complete`
  - `website_blog.blog_post_content`
- Produces hooks:
  - `.facodi-blog-index`
  - `.facodi-bulletin-hero`
  - `.facodi-bulletin-card`
  - `.facodi-blog-article`
  - `.facodi-blog-prose`

- [ ] **Step 1: Write failing native-blog contract**

`tests/test_blog_contract.sh` must require:

- the four native inherit IDs above;
- no replacement of blog routes/models;
- no direct ORM in QWeb;
- no static author/date/tag/post counts;
- CSS scoped under native `o_wblog_*` + FACODI hooks;
- no generic forced `background-image: ... !important` on blog covers.

- [ ] **Step 2: Run RED**

~~~bash
bash tests/test_blog_contract.sh
~~~

Expected: FAIL because D2 Blog inheritance/style files do not exist.

- [ ] **Step 3: Add narrow QWeb hooks**

In `website_blog.xml`:

- add `facodi-blog-index` to `#o_wblog_index_content`;
- add `facodi-bulletin-hero` to the existing top blog region instead of replacing native blog/editor droppable areas;
- add `facodi-bulletin-card` to native `article.o_wblog_post` through its dynamic class attribute;
- add `facodi-blog-article` to `#o_wblog_post_main`;
- add `facodi-blog-prose` to `.o_wblog_post_content_field`;
- preserve native post cover, search, tags, date, author, pager, comments/share/read-next options.

- [ ] **Step 4: Implement Blog SCSS**

Index cards:

- paper border/hard shadow;
- responsive image;
- metadata remains legible;
- sparse cards collapse without empty slots.

Article:

- max reading width;
- heading/list/link/blockquote/pre/table rules;
- media responsive;
- no graph grid behind prose;
- custom cover style not overridden.

- [ ] **Step 5: Add rendered Odoo tests**

Create two real blog posts in `test_website.py`:

1. sparse published post: title + content only;
2. rich published post: subtitle + tag + cover properties + author/date.

Assert:

- blog index returns 200;
- both post links remain native;
- D2 card hooks render;
- article returns 200;
- article title/body/native metadata survive;
- sparse post does not receive fabricated metadata;
- custom cover properties remain distinct after render.

- [ ] **Step 6: Run GREEN**

~~~bash
bash tests/test_blog_contract.sh
bash tests/test_editorial_interfaces_contract.sh
~~~

Then require exact-head Odoo Theme CI green.

- [ ] **Step 7: Commit**

~~~bash
git add theme_facodi/views/website_blog.xml   theme_facodi/static/src/scss/website_blog.scss   tests/test_blog_contract.sh theme_facodi/tests/test_website.py   theme_facodi/__manifest__.py
git commit -m "feat(blog): add FACODI Campus Bulletin presentation"
~~~

---

### Task 4: Style native Contact without replacing the Odoo form

**Repository:** `marcelo-m7/facodi-theme`

**Files:**
- Create: `theme_facodi/views/website_public.xml`
- Create: `theme_facodi/static/src/scss/website_public.scss`
- Create: `tests/test_public_pages_contract.sh`
- Modify: `theme_facodi/__manifest__.py`
- Modify: `theme_facodi/tests/test_website.py`

**Interfaces:**
- Consumes: native `website.contactus`.
- Produces:
  - `.facodi-contact-page`
  - `.facodi-contact-form-sheet`
  - `.facodi-contact-context`.

- [ ] **Step 1: Write failing Contact contract**

Require `website_public.xml` to inherit `website.contactus` and only add classes/wrappers around stable native nodes.

Static assertions must require the source view still contains, through upstream/native contract assumptions:

- `#contactus_form`;
- action `/website/form/`;
- field names `name`, `phone`, `email_from`, `company`, `subject`, `description`;
- `.s_website_form_send`;
- native success behavior.

Fail if D2 XML adds a second `<form>`.

- [ ] **Step 2: Run RED**

~~~bash
bash tests/test_public_pages_contract.sh
~~~

Expected: FAIL because Contact inheritance does not exist.

- [ ] **Step 3: Add Contact inheritance**

Use stable base hooks in Odoo 19:

- add `facodi-contact-page` to `#wrap`;
- add `facodi-contact-form-sheet` to `.s_website_form`;
- add a semantic class to the existing contextual/company column rather than replacing company/contact data.

Do not replace input fields or form action.

- [ ] **Step 4: Implement Contact styling**

Use the D2 contact-sheet vocabulary:

- form/context become 5/7 or 4/8 desktop;
- full width mobile;
- native validation/error styles remain visible;
- native fields retain 44 px practical target height;
- no contact values are inserted by SCSS/QWeb.

- [ ] **Step 5: Add rendered Contact regression**

In `test_website.py`:

- `/contactus` returns 200;
- D2 contact class is present;
- exactly one `#contactus_form` exists;
- its action remains `/website/form/`;
- every required native field name remains;
- submit control remains `.s_website_form_send`.

- [ ] **Step 6: Run GREEN**

Run public contract and exact-head Odoo CI.

- [ ] **Step 7: Commit**

~~~bash
git add theme_facodi/views/website_public.xml   theme_facodi/static/src/scss/website_public.scss   tests/test_public_pages_contract.sh theme_facodi/tests/test_website.py   theme_facodi/__manifest__.py
git commit -m "feat(public): style native FACODI contact surface"
~~~

---

### Task 5: Add legal/policy readability and generic editorial long-form rules

**Repository:** `marcelo-m7/facodi-theme`

**Files:**
- Modify: `theme_facodi/static/src/scss/website_public.scss`
- Modify: `theme_facodi/views/snippets/components/s_facodi_policy_document.xml`
- Modify: `tests/test_public_pages_contract.sh`
- Modify: `tests/test_mobile_interaction_contract.sh`

**Interfaces:**
- Consumes: `.facodi-policy-document`.
- Produces safe long-form behavior for editor-owned policy pages.

- [ ] **Step 1: Add failing long-form contract**

Require policy SCSS to handle:

- `h1/h2/h3`;
- lists;
- links/long URLs with `overflow-wrap: anywhere`;
- `pre` / `code` with contained overflow;
- `table` through an internally scrollable wrapper or native responsive table class;
- images/iframes/video with `max-width: 100%`;
- one-column 320 px layout.

Assert the policy snippet contains no actual privacy/cookie/terms text.

- [ ] **Step 2: Run RED**

~~~bash
bash tests/test_public_pages_contract.sh
bash tests/test_mobile_interaction_contract.sh
~~~

- [ ] **Step 3: Implement policy/readability styles**

Keep decoration restrained:

- warm paper;
- ink border;
- no rotated notes over prose;
- max reading width;
- clear link/focus styles.

- [ ] **Step 4: Run GREEN**

Static contracts pass.

- [ ] **Step 5: Commit**

~~~bash
git add theme_facodi/static/src/scss/website_public.scss   theme_facodi/views/snippets/components/s_facodi_policy_document.xml   tests/test_public_pages_contract.sh tests/test_mobile_interaction_contract.sh
git commit -m "feat(public): add D2 policy readability shell"
~~~

---

### Task 6: Complete D2 i18n, accessibility, docs and owner-repository verification

**Repository:** `marcelo-m7/facodi-theme`

**Files:**
- Modify: `theme_facodi/i18n/theme_facodi.pot`
- Modify: `theme_facodi/i18n/pt.po`
- Modify: `theme_facodi/i18n/es.po`
- Modify: `theme_facodi/i18n/fr.po`
- Modify: `tests/test_i18n_contract.sh`
- Modify: `tests/test_mobile_interaction_contract.sh`
- Modify: `.github/workflows/ci.yml`
- Modify: `README.md`
- Modify: `docs/validation.md`

**Interfaces:**
- Produces exact green `theme_facodi 19.0.9.0.0` SHA for deployment integration.

- [ ] **Step 1: Enumerate only new D2 source strings**

Generate/inspect the exact msgids introduced by the eight snippets and any native-template editorial labels.

Every new msgid must have:

- POT entry;
- PT entry;
- ES entry;
- FR entry;
- the correct `theme.ir.ui.view` occurrence for each D2 view that uses it.

- [ ] **Step 2: Add i18n RED assertions first**

Extend `test_i18n_contract.sh` with a `D2_EDITORIAL_MSGIDS` array and view-occurrence checks.

Run:

~~~bash
bash tests/test_i18n_contract.sh
~~~

Expected: FAIL until catalogues are updated.

- [ ] **Step 3: Update POT/PT/ES/FR**

Keep English canonical; do not add `en.po` or language-specific QWeb branches.

- [ ] **Step 4: Add final accessibility/mobile checks**

Contracts must pin:

- long D2 titles wrap;
- editorial cards/timeline/contact collapse to one column;
- blog/policy media cannot widen the page;
- D2 hover/transform transitions are disabled under reduced motion;
- focus-visible rules exist for cards/links/forms.

- [ ] **Step 5: Update documentation and CI release guard**

README / validation document:

- D2 ownership boundaries;
- `website_blog` dependency;
- Website Builder persistence guarantee;
- no-fake-contact/metrics policy;
- 320 px hard gate;
- live recomposition/deployment sequence.

CI requires `19.0.9.0.0` and runs all three D2 static contracts.

- [ ] **Step 6: Run the complete owner-repository gate**

~~~bash
bash tests/test_module_contract.sh
bash tests/test_campus_paper_contract.sh
bash tests/test_global_shell_contract.sh
bash tests/test_homepage_dashboard_contract.sh
bash tests/test_foundation_v2_contract.sh
bash tests/test_curriculum_style_contract.sh
bash tests/test_learning_interfaces_contract.sh
bash tests/test_editorial_interfaces_contract.sh
bash tests/test_blog_contract.sh
bash tests/test_public_pages_contract.sh
bash tests/test_i18n_contract.sh
bash tests/test_elearning_catalog_style_contract.sh
bash tests/test_mobile_interaction_contract.sh
~~~

Require exact-head Odoo 19 Theme CI success including legacy install, upgrade, asset compilation and Website Builder persistence.

- [ ] **Step 7: Commit**

~~~bash
git add theme_facodi/i18n tests .github/workflows/ci.yml README.md docs/validation.md
git commit -m "test(theme): release D2 editorial public surfaces"
~~~

---

### Task 7: Open, review and merge the D2 owner-repository PR

**Repository:** `marcelo-m7/facodi-theme`

**Files:** no new implementation files expected.

**Interfaces:**
- Consumes: exact green Task 6 SHA.
- Produces: one merged `facodi-theme/main` SHA at `19.0.9.0.0`.

- [ ] **Step 1: Synchronize current main**

If `main` advanced during D2, carry every compatible current-main fix into the D2 branch and create an ancestry synchronization commit before opening/merging the PR.

Do not discard concurrent homepage/D1 migration/compatibility work.

- [ ] **Step 2: Open non-draft PR**

PR body must list:

- D2 component library;
- Blog native ownership;
- Contact native ownership;
- legal-content boundary;
- i18n;
- Website Builder persistence;
- exact-head CI run.

- [ ] **Step 3: Resolve review findings with regression tests**

For every valid finding:

1. add/adjust test;
2. implement fix;
3. rerun exact-head CI;
4. reply and resolve thread.

- [ ] **Step 4: Merge exact green head**

Use `expected_head_sha` and squash merge.

- [ ] **Step 5: Require post-merge main CI GREEN**

Record the merged SHA for Task 8.

---

### Task 8: Prove D2 in a disposable integrated runtime before production

**Repository:** `marcelo-m7/facodi-deploy` on a new integration branch from current main.

**Files:**
- Modify gitlink: `addons/facodi-theme` → exact merged D2 SHA.
- Extend/create D2 browser acceptance fixtures/assertions.
- Do not merge production yet.

**Interfaces:**
- Consumes exact merged D2 theme SHA.
- Produces browser screenshots and overflow evidence.

- [ ] **Step 1: Pin only the D2 theme gitlink**

Keep all other current production gitlinks unchanged.

Assert no other submodule pin changes.

- [ ] **Step 2: Build disposable editorial fixtures**

The disposable runtime may create test-only records/pages because its database is ephemeral.

Create:

- About page from D2 About composition;
- Contribution page from D2 Contribution composition;
- one rich blog post;
- one sparse blog post;
- Contact uses native `/contactus`;
- one policy test page containing a long URL, table and `pre` block wrapped in `.facodi-policy-document`.

Do not use fictional fixtures as production claims; they exist only in the disposable CI database.

- [ ] **Step 3: Extend Playwright D2 matrix**

Check:

- About: 1440×1200, 1024×1366, 390×844, 320×700;
- Contribution: 1440×1200, 390×844, 320×700;
- Blog index: 1440×1200, 390×844, 320×700;
- rich blog article: 1440×1200, 390×844;
- sparse article: 390×844;
- Contact: 1440×1200, 390×844, 320×700;
- Policy: 1440×1200, 390×844, 320×700.

Every page fails when `document.documentElement.scrollWidth > window.innerWidth + 1`.

Contact also asserts exactly one native form, expected field names and submit button.

Blog asserts native title/date/link content plus D2 hooks.

- [ ] **Step 4: Run the complete disposable runtime gate**

Require repository/Compose/migration/Odoo HTTP/Chrome browser acceptance GREEN and upload `facodi-d2-browser-acceptance` screenshots.

- [ ] **Step 5: Stop before production merge**

Present exact deploy head, D2 theme SHA, CI run and screenshot artifact.

Production promotion requires the already-established deployment gate.

---

### Task 9: Promote D2 code, then perform controlled live Website recomposition

**Repositories / systems:** `facodi-deploy`, production Odoo FACODI.

**Interfaces:**
- Consumes: explicit production promotion approval + exact green Task 8 deployment candidate.
- Produces: D2 code available on production, then editor-owned pages recomposed safely.

**Important sequencing ruling:** new D2 snippet/view XML IDs cannot be used safely by the production Website database before the new theme code is deployed. Therefore disposable page composition is proven before promotion, but the actual production Website Builder recomposition happens immediately **after** the D2 code deployment is healthy. This preserves the spec's separation between code release and live content mutation while avoiding references to not-yet-installed views.

- [ ] **Step 1: Merge exact green deployment PR**

Guard with expected head SHA.

- [ ] **Step 2: Require post-merge CI and service recovery**

Verify the canonical routes return after the Coolify rebuild before any page mutation.

- [ ] **Step 3: Back up live target pages before editing**

Through Odoo MCP, read and preserve outside git:

- page ID / URL;
- owning view ID;
- current `arch_db`/equivalent editor markup;
- name/title;
- language translations where the connector exposes them.

Targets initially:

- About;
- Contribution;
- any explicit Manifesto/Partners page selected for D2;
- legal pages only if they are being wrapped/styled structurally.

Never rewrite Blog posts or Contact form markup in this step.

- [ ] **Step 4: Recompose About**

Map meaningful current content into the approved D2 sequence:

- intro;
- project story;
- principles;
- how-it-works timeline with `#how-it-works`;
- institutional context;
- next routes;
- CTA.

Preserve existing factual content rather than replacing it with generic starter text.

- [ ] **Step 5: Recompose Contribution**

Use:

- intro;
- contribution board;
- proposal → review → publication timeline;
- existing moderation/boundary copy;
- community;
- real `/contribuir/recurso` and Contact CTAs.

- [ ] **Step 6: Wrap legal content without rewriting it**

Only add/retain the `facodi-policy-document` structural class/shell around existing legal markup when safe.

Do not alter legal paragraphs, dates or obligations.

- [ ] **Step 7: Verify PT/ES/FR and public routes**

Check:

- About;
- Contribution;
- Blog index;
- one blog post;
- Contact;
- Privacy;
- Cookies;
- Terms;
- relevant PT/ES/FR variants.

Verify no placeholder phone/email/address was introduced.

- [ ] **Step 8: Report exact production evidence**

Report:

- theme merge SHA;
- deploy merge SHA;
- post-merge CI;
- public route recovery;
- pages recomposed;
- backup evidence location/reference;
- translations checked;
- any page deliberately left unchanged and why.

## Final D2 Verification

D2 is complete only when:

- `theme_facodi 19.0.9.0.0` is merged and green;
- all eight D2 components exist in Website Builder;
- About/How/Contribution/Manifesto/Partners page-picker compositions use D2 primitives without importing fixed pages;
- native Blog index/article behavior is preserved and visually integrated;
- native Contact form has exactly one real form and unchanged native fields/action;
- policy/legal content is not rewritten;
- POT + PT/ES/FR are green;
- Website Builder edits persist through upgrade;
- disposable browser acceptance passes About, Contribution, Blog, Contact and Policy at required widths including 320 px;
- production code promotion is green;
- live editorial recomposition preserves meaningful existing content and has a backup;
- no fake contact data, metrics, partner claims or testimonials are introduced.
