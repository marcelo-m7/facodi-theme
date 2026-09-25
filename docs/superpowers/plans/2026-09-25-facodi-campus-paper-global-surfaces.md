# FACODI Campus Paper Global Surfaces Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Carry the approved FACODI Campus Paper visual system from the homepage into the global Website shell, Odoo eLearning, curriculum/Roadmap surfaces and reusable editorial snippets without changing business logic or deployment composition.

**Architecture:** This is Phase B of the approved visual-system specification. The work remains presentation-only inside facodi-theme: reuse the Campus Paper tokens and primitives shipped in 19.0.6.0.0, style standard Odoo hooks instead of replacing controllers/models, and consume the public CSS hooks already exposed by facodi-learning. No facodi-deploy or facodi-learning write belongs in this plan.

**Tech Stack:** Odoo 19 Community, QWeb, Website Builder, Portal, website_slides, SCSS/CSS custom properties, Bash contracts, Odoo HttpCase, native PO/POT catalogues, GitHub Actions.

**Spec:** docs/superpowers/specs/2026-09-25-facodi-campus-paper-visual-system-design.md

## Global Constraints

- Target Odoo 19 Community.
- Keep theme_facodi presentation-only.
- Preserve Odoo Website Builder, Website menus, native mobile header, Portal authentication and account dropdown.
- Preserve website_slides as owner of courses, lessons, enrolment, progress and routes.
- Do not add controllers, authentication, parallel course/page models or ORM searches in QWeb.
- Preserve all existing public routes.
- Preserve custom/editor-selected course covers; only replace Odoo's known default cover gradient.
- English remains canonical QWeb source; PT/ES/FR remain native PO catalogues.
- Do not add remote fonts.
- Keep stable XML IDs.
- Do not create academic-equivalence or accreditation claims.
- Keep visible :focus-visible, 44 px mobile touch targets and prefers-reduced-motion.
- No facodi-deploy, Coolify, Supabase or production mutation in this plan.
- Release target: theme_facodi 19.0.7.0.0.

## File Map

- theme_facodi/static/src/scss/website.scss — public shell: header, mobile header, footer, standard public forms.
- theme_facodi/static/src/scss/website_slides.scss — native Odoo eLearning catalogue, cards, course header, lessons, progress and actions.
- theme_facodi/static/src/scss/curriculum.scss — Roadmaps, curricular units, filters, coverage states, tables and learning-path presentation exposed by facodi-learning.
- theme_facodi/static/src/scss/foundation_v2.scss — academic-area/ecosystem surfaces shared across editorial pages.
- theme_facodi/views/header.xml — native Odoo header composition; no parallel mobile menu.
- theme_facodi/views/customizations.xml — footer composition.
- theme_facodi/views/snippets/s_facodi_intro.xml — editorial page hero.
- theme_facodi/views/snippets/s_facodi_editorial_routes.xml — reusable next-destination cards.
- theme_facodi/views/snippets/s_facodi_editorial_pathway.xml — reusable editorial study sequence.
- tests/test_global_shell_contract.sh — new header/footer/forms Campus Paper contract.
- tests/test_curriculum_style_contract.sh — new Roadmap/UC presentation contract.
- tests/test_elearning_catalog_style_contract.sh — extend native eLearning visual contract.
- tests/test_mobile_interaction_contract.sh — extend 320 px/mobile behavior gates.
- theme_facodi/tests/test_header_compatibility.py — preserve customized-header compatibility.
- theme_facodi/tests/test_website.py — rendered shell/eLearning/assets assertions.
- theme_facodi/tests/test_i18n.py and tests/test_i18n_contract.sh — translation regression guard.
- .github/workflows/ci.yml, README.md, docs/validation.md — release gate and evidence.

## Review Focus

1. **Existing Website Builder customization removes/replaces the inner desktop nav** — FACODI header must still render because the theme replaces only the stable outer //header and calls Odoo standard building blocks. Task 1 pins the existing compatibility HttpCase.
2. **A course has a custom image/cover chosen in Odoo** — Campus Paper styling must not overwrite that cover; only Odoo's exact default purple gradient may be replaced. Task 2 pins the exact selector.
3. **Very long course, Roadmap or curricular-unit names on a 320 px viewport** — text wraps, cards remain shrinkable with min-width: 0 and no page-level horizontal overflow appears. Tasks 2 and 3 pin this.
4. **Wide curriculum tables and filter forms on mobile** — tables scroll inside their own container and filters stack without widening the page. Task 3 pins this.
5. **Keyboard-only authenticated navigation and lesson interaction** — account dropdown, course actions and lesson rows retain visible focus and native links/buttons. Tasks 1 and 2 pin this.

---

### Task 1: Refactor the public header, mobile header, footer and standard forms

**Files:**
- Create: tests/test_global_shell_contract.sh
- Modify: theme_facodi/static/src/scss/website.scss
- Modify: theme_facodi/views/header.xml
- Modify: theme_facodi/views/customizations.xml
- Modify: theme_facodi/tests/test_header_compatibility.py
- Modify: theme_facodi/tests/test_website.py
- Modify: tests/test_mobile_interaction_contract.sh

**Interfaces:**
- Consumes: Phase A CSS variables and paper/button primitives.
- Produces: facodi-nav-shell, facodi-footer-campus, facodi-footer-note and standardized public form presentation under facodi-site.

- [ ] **Step 1: Write the failing global-shell contract**

Create tests/test_global_shell_contract.sh:

~~~bash
#!/usr/bin/env bash
set -euo pipefail

fail() { echo "FAIL: $*" >&2; exit 1; }

HEADER="theme_facodi/views/header.xml"
FOOTER="theme_facodi/views/customizations.xml"
SCSS="theme_facodi/static/src/scss/website.scss"

for anchor in \
  'facodi-nav-shell' \
  'website.navbar_nav' \
  'portal.placeholder_user_sign_in' \
  'portal.user_dropdown' \
  'website.template_header_mobile'; do
  grep -Fq "$anchor" "$HEADER" || fail "native header hook missing: $anchor"
done

for anchor in 'facodi-footer-campus' 'facodi-footer-note' 'facodi-footer-links'; do
  grep -Fq "$anchor" "$FOOTER" || fail "footer Campus Paper hook missing: $anchor"
done

for selector in \
  '.facodi-header' \
  '.facodi-dropdown-menu' \
  '.o_header_mobile' \
  '.facodi-footer-campus' \
  '.facodi-footer-note' \
  '.facodi-site .form-control' \
  '.facodi-site .form-select'; do
  grep -Fq "$selector" "$SCSS" || fail "global Campus Paper selector missing: $selector"
done

grep -Fq ':focus-visible' "$SCSS" || fail "global shell needs keyboard focus styles"
grep -Fq 'min-height: 2.75rem' "$SCSS" || fail "public actions must keep a 44px target"

echo "PASS: Campus Paper global shell contract"
~~~

- [ ] **Step 2: Run RED**

Run:

~~~bash
bash tests/test_global_shell_contract.sh
~~~

Expected: FAIL because facodi-footer-campus and facodi-footer-note do not exist.

- [ ] **Step 3: Add semantic footer hooks without changing menu ownership**

In customizations.xml keep the facodi_footer XML ID and current menu loops. Change the outer/footer-note classes only:

~~~xml
<div id="footer"
     class="facodi-footer facodi-footer-campus"
     data-name="FACODI Footer"
     t-if="not no_footer">
    <div class="container-fluid facodi-footer-inner">
        <div class="facodi-footer-note">
            <a href="/" class="facodi-wordmark" t-translation="off">FACODI<span>.</span></a>
            <p>Digital Community College. Open, collaborative and accessible higher education.</p>
        </div>
        <!-- keep current menu loop and footer meta -->
    </div>
</div>
~~~

Do not add or remove footer business data.

- [ ] **Step 4: Keep the header native and add only a presentation hook**

In header.xml preserve the outer-header replacement and every existing Odoo call. Change the shell to:

~~~xml
<div id="o_main_nav" class="container-fluid facodi-nav-shell facodi-paper-nav">
~~~

Do not add another mobile menu, custom sign-in route or duplicate menu loop.

- [ ] **Step 5: Move header/footer geometry to Campus Paper tokens**

In website.scss implement:

~~~scss
.facodi-site {
    background: var(--facodi-surface-page);
    color: var(--facodi-ink);

    .facodi-header {
        background: color-mix(in srgb, var(--facodi-paper-warm) 94%, white);
        border-bottom: var(--facodi-border);

        .facodi-nav-shell {
            min-height: 4.25rem;
            padding-inline: clamp(1rem, 3vw, 2rem);
        }

        .nav-link {
            border-radius: var(--facodi-radius-sm);
            color: var(--facodi-ink);

            &:hover,
            &:focus-visible,
            &.active {
                background: var(--facodi-sun);
                color: var(--facodi-ink);
            }
        }
    }

    .facodi-dropdown-menu {
        background: var(--facodi-surface-sheet);
        border: var(--facodi-border);
        border-radius: var(--facodi-radius);
        box-shadow: var(--facodi-shadow);
    }

    .o_header_mobile {
        background: var(--facodi-paper-warm);
        border-bottom: var(--facodi-border);
    }

    .facodi-footer-campus {
        background: var(--facodi-ink-deep);
        border-top: .35rem solid var(--facodi-sun);
        color: var(--facodi-white);
    }

    .facodi-footer-note {
        border-left: 3px solid var(--facodi-sun);
        padding-left: 1rem;
    }
}
~~~

Keep existing responsive footer grid behavior.

- [ ] **Step 6: Normalize standard public form controls**

Add:

~~~scss
.facodi-site .form-control,
.facodi-site .form-select {
    background-color: var(--facodi-surface-sheet);
    border: 1px solid color-mix(in srgb, var(--facodi-ink) 72%, transparent);
    border-radius: var(--facodi-radius);
    color: var(--facodi-ink);
    min-height: 2.75rem;

    &:focus {
        border-color: var(--facodi-ink);
        box-shadow: var(--facodi-focus-ring);
    }
}

.facodi-site :is(a, button, input, select, textarea):focus-visible {
    outline: 0;
    box-shadow: var(--facodi-focus-ring);
}
~~~

- [ ] **Step 7: Extend rendered shell tests**

Add to theme_facodi/tests/test_website.py:

~~~python
def test_campus_paper_shell_keeps_native_header_footer_and_forms(self):
    from lxml import html

    tree = html.fromstring(self.url_open("/").text)
    self.assertTrue(tree.xpath("//header//*[contains(@class, 'facodi-nav-shell')]"))
    self.assertTrue(
        tree.xpath("//*[@id='footer' and contains(@class, 'facodi-footer-campus')]")
    )
    self.assertTrue(
        tree.xpath("//*[@id='footer']//*[contains(@class, 'facodi-footer-note')]")
    )

    login = self.url_open("/web/login")
    self.assertEqual(login.status_code, 200)
    self.assertIn("form-control", login.text)
~~~

- [ ] **Step 8: Strengthen header/mobile compatibility tests**

In theme_facodi/tests/test_header_compatibility.py add:

~~~python
self.assertIn("facodi-nav-shell", response.text)
self.assertIn("o_header_mobile", response.text)
~~~

In tests/test_mobile_interaction_contract.sh require facodi-footer-campus and keep the native #top_menu_collapse_mobile and navbar-toggler-icon checks.

- [ ] **Step 9: Run GREEN**

~~~bash
bash tests/test_global_shell_contract.sh
bash tests/test_mobile_interaction_contract.sh
bash tests/test_module_contract.sh
~~~

Expected: PASS.

- [ ] **Step 10: Commit**

~~~bash
git add tests/test_global_shell_contract.sh tests/test_mobile_interaction_contract.sh \
  theme_facodi/views/header.xml theme_facodi/views/customizations.xml \
  theme_facodi/static/src/scss/website.scss \
  theme_facodi/tests/test_header_compatibility.py theme_facodi/tests/test_website.py
git commit -m "feat(theme): carry Campus Paper into global website shell"
~~~

---

### Task 2: Carry Campus Paper into native Odoo eLearning surfaces

**Files:**
- Modify: theme_facodi/static/src/scss/website_slides.scss
- Modify: tests/test_elearning_catalog_style_contract.sh
- Modify: tests/test_mobile_interaction_contract.sh
- Modify: theme_facodi/tests/test_website.py

**Interfaces:**
- Consumes: native website_slides hooks already targeted by the theme.
- Produces: Campus Paper presentation for catalogue cards, cover/nav controls, lesson rows, progress and join/done actions.

- [ ] **Step 1: Add failing eLearning assertions**

Extend tests/test_elearning_catalog_style_contract.sh:

~~~bash
for selector in \
  '.facodi-slides-catalog' \
  '.facodi-slides-grid' \
  '.facodi-course-media' \
  '.facodi-course-fallback' \
  '.facodi-content-type' \
  '.o_record_cover_container[data-res-model="slide.channel"]' \
  '.o_wslides_course_nav' \
  '.o_wslides_course_card' \
  '.o_wslides_slide_list_category_header' \
  '.o_wslides_slides_list_slide' \
  '.o_wslides_js_course_join_link.btn-primary' \
  '.o_wslides_done_button.btn-primary'; do
  grep -Fq "$selector" "$SCSS" || fail "missing eLearning selector: $selector"
done

grep -Fq 'var(--facodi-shadow)' "$SCSS" \
  || fail "eLearning cards must use shared Campus Paper shadow"
grep -Fq 'var(--facodi-sun)' "$SCSS" \
  || fail "eLearning primary actions must use the highlighter accent"
grep -Fq '[style*="linear-gradient(120deg, #875A7B, #78516F)"]' "$SCSS" \
  || fail "default-cover override must remain editor-safe"
~~~

- [ ] **Step 2: Run RED**

~~~bash
bash tests/test_elearning_catalog_style_contract.sh
~~~

Expected: FAIL on shared shadow/highlighter usage.

- [ ] **Step 3: Convert catalogue cards/fallbacks to shared paper geometry**

Implement:

~~~scss
body.o_wslides_body .facodi-site {
    .facodi-course-fallback {
        background-color: var(--facodi-paper-warm);
        background-image:
            linear-gradient(color-mix(in srgb, var(--facodi-ink) 10%, transparent) 1px, transparent 1px),
            linear-gradient(90deg, color-mix(in srgb, var(--facodi-ink) 10%, transparent) 1px, transparent 1px);
        background-size: 22px 22px;
        color: var(--facodi-ink);

        .facodi-course-fallback-brand {
            background: var(--facodi-sun);
            border: 1px solid var(--facodi-ink);
            padding: .3rem .45rem;
            width: max-content;
        }
    }

    .o_wslides_course_card {
        background: var(--facodi-surface-sheet);
        border: var(--facodi-border);
        border-radius: var(--facodi-radius);
        box-shadow: var(--facodi-shadow);

        &:hover,
        &:focus-within {
            box-shadow: var(--facodi-shadow-hover);
            transform: translate(2px, 2px);
        }
    }
}
~~~

- [ ] **Step 4: Convert course actions and progress**

~~~scss
body.o_wslides_body .facodi-site {
    .o_wslides_js_course_join_link.btn-primary,
    .o_wslides_done_button.btn-primary {
        background-color: var(--facodi-sun);
        border: var(--facodi-border);
        box-shadow: var(--facodi-shadow-hover);
        color: var(--facodi-ink);

        &:hover,
        &:focus-visible {
            background-color: var(--facodi-mint);
            color: var(--facodi-ink);
        }
    }

    .progress {
        background: var(--facodi-paper-warm);
        border: 1px solid var(--facodi-ink);
    }

    .progress-bar {
        background-color: var(--facodi-mint-strong);
    }
}
~~~

- [ ] **Step 5: Make course nav/lesson hierarchy read as paper layers**

~~~scss
body.o_wslides_body .facodi-site {
    .o_record_cover_container[data-res-model="slide.channel"] {
        .o_wslides_course_nav,
        .o_wslides_course_nav_search {
            background-color: var(--facodi-paper-warm);
            border: 1px solid var(--facodi-ink);
            box-shadow: var(--facodi-shadow-hover);
            color: var(--facodi-ink);
        }
    }

    .o_wslides_slide_list_category_header {
        background: var(--facodi-mint);
        border: var(--facodi-border);
        border-radius: var(--facodi-radius) var(--facodi-radius) 0 0;
    }

    .o_wslides_slides_list_slide {
        background: var(--facodi-surface-sheet);

        &:hover,
        &:focus-within {
            background: color-mix(in srgb, var(--facodi-mint) 30%, white);
            border-color: var(--facodi-ink);
        }
    }
}
~~~

Do not change completion semantics, URLs or JS hooks.

- [ ] **Step 6: Preserve custom-cover safety**

Keep the forced cover override limited to Odoo's exact default:

~~~scss
body.o_wslides_body .facodi-site
.o_record_cover_container[data-res-model="slide.channel"][style*="linear-gradient(120deg, #875A7B, #78516F)"] {
    background-image: linear-gradient(
        120deg,
        var(--facodi-paper-warm),
        var(--facodi-mint)
    ) !important;
}
~~~

Do not add a generic background-image important rule for all slide.channel covers.

- [ ] **Step 7: Add compiled asset assertions**

Add to test_standard_forms_and_compiled_frontend_assets:

~~~python
self.assertIn(".o_wslides_course_card", compiled)
self.assertIn(".o_wslides_slide_list_category_header", compiled)
self.assertIn(".o_wslides_js_course_join_link.btn-primary", compiled)
self.assertIn("var(--facodi-mint-strong)", compiled)
~~~

- [ ] **Step 8: Pin narrow-screen course/lesson text**

Extend tests/test_mobile_interaction_contract.sh:

~~~bash
grep -Fq 'min-width: 0' theme_facodi/static/src/scss/website_slides.scss \
  || fail "eLearning cards and rows must remain shrinkable"
grep -Fq 'overflow-wrap' theme_facodi/static/src/scss/website_slides.scss \
  || fail "long course and lesson text must wrap"
~~~

- [ ] **Step 9: Run GREEN**

~~~bash
bash tests/test_elearning_catalog_style_contract.sh
bash tests/test_mobile_interaction_contract.sh
bash tests/test_module_contract.sh
~~~

Expected: PASS.

- [ ] **Step 10: Commit**

~~~bash
git add theme_facodi/static/src/scss/website_slides.scss \
  tests/test_elearning_catalog_style_contract.sh tests/test_mobile_interaction_contract.sh \
  theme_facodi/tests/test_website.py
git commit -m "feat(elearning): apply Campus Paper to Odoo learning surfaces"
~~~

---

### Task 3: Apply the study-object vocabulary to Roadmaps and Curricular Units

**Files:**
- Create: tests/test_curriculum_style_contract.sh
- Modify: theme_facodi/static/src/scss/curriculum.scss
- Modify: tests/test_mobile_interaction_contract.sh
- Modify: theme_facodi/tests/test_website.py

**Interfaces:**
- Consumes stable public classes already emitted by facodi-learning: facodi-curriculum, facodi-curriculum-pathway, facodi-curriculum-map__unit, facodi-coverage-badge, facodi-editorial-routes-list and facodi-pathway-step.
- Produces presentation only; no facodi-learning data/model/controller change.

- [ ] **Step 1: Write the failing curriculum style contract**

Create tests/test_curriculum_style_contract.sh:

~~~bash
#!/usr/bin/env bash
set -euo pipefail

fail() { echo "FAIL: $*" >&2; exit 1; }

SCSS="theme_facodi/static/src/scss/curriculum.scss"

for selector in \
  '.facodi-curriculum' \
  '.facodi-curriculum .card' \
  '.facodi-curriculum form' \
  '.facodi-curriculum-pathway' \
  '.facodi-curriculum-pathway__header' \
  '.facodi-curriculum-map__unit' \
  '.facodi-coverage-badge' \
  '.facodi-curriculum-table' \
  '.facodi-editorial-routes-list' \
  '.facodi-pathway-step'; do
  grep -Fq "$selector" "$SCSS" || fail "curriculum selector missing: $selector"
done

grep -Fq 'var(--facodi-shadow)' "$SCSS" \
  || fail "curriculum cards must use the shared shadow"
grep -Fq 'overflow-x: auto' "$SCSS" \
  || fail "wide curriculum tables must scroll internally"
grep -Fq '@media (max-width: 767.98px)' "$SCSS" \
  || fail "curriculum needs an explicit phone layout"
grep -Fq 'grid-template-columns: minmax(0, 1fr)' "$SCSS" \
  || fail "phone curriculum layouts must collapse to one shrinkable column"

echo "PASS: Campus Paper curriculum presentation contract"
~~~

- [ ] **Step 2: Run RED**

~~~bash
bash tests/test_curriculum_style_contract.sh
~~~

Expected: FAIL because facodi-curriculum form and shared shadow are missing.

- [ ] **Step 3: Convert cards/pathways to paper surfaces**

~~~scss
.facodi-site {
    .facodi-curriculum .card,
    .facodi-curriculum-card,
    .facodi-curriculum-pathway {
        background: var(--facodi-surface-sheet);
        border: var(--facodi-border);
        border-radius: var(--facodi-radius);
        box-shadow: var(--facodi-shadow);
    }

    .facodi-curriculum-pathway__header {
        background: var(--facodi-mint);
        border-bottom: var(--facodi-border);
    }

    .facodi-curriculum-map__unit {
        background: var(--facodi-paper-warm);
        min-width: 0;
    }
}
~~~

- [ ] **Step 4: Style filters/provenance blocks as reference sheets**

~~~scss
.facodi-site {
    .facodi-curriculum form {
        background: var(--facodi-paper-warm);
        border: var(--facodi-border) !important;
        border-radius: var(--facodi-radius) !important;
        box-shadow: var(--facodi-shadow-hover);
    }

    .facodi-curriculum .alert {
        border: 1px solid var(--facodi-ink);
        border-radius: var(--facodi-radius);
    }

    .facodi-curriculum code {
        background: color-mix(in srgb, var(--facodi-sun) 50%, white);
        border: 1px solid color-mix(in srgb, var(--facodi-ink) 38%, transparent);
        border-radius: var(--facodi-radius-sm);
        color: var(--facodi-ink);
        padding: .1rem .3rem;
    }
}
~~~

Do not alter academic/provenance copy.

- [ ] **Step 5: Preserve coverage-state semantics**

Keep current mapping: covered/covers/equivalent → mint; partial → sun; gap → neutral; supports → cyan. Styling must not create new accreditation wording.

- [ ] **Step 6: Pin mobile filter/table/path behavior**

~~~scss
@media (max-width: 767.98px) {
    .facodi-site {
        .facodi-curriculum form.row {
            display: grid;
            grid-template-columns: minmax(0, 1fr);
        }

        .facodi-editorial-routes-list,
        .facodi-curriculum-map__unit {
            grid-template-columns: minmax(0, 1fr);
        }

        .facodi-curriculum-table,
        .facodi-curriculum .table-responsive {
            max-width: 100%;
            overflow-x: auto;
            overscroll-behavior-inline: contain;
        }
    }
}
~~~

- [ ] **Step 7: Extend compiled asset assertions**

Add:

~~~python
self.assertIn(".facodi-curriculum-pathway", compiled)
self.assertIn(".facodi-curriculum-map__unit", compiled)
self.assertIn(".facodi-coverage-badge", compiled)
~~~

Do not create fake Roadmap routes inside facodi-theme; Phase C will smoke-test the integrated addons together.

- [ ] **Step 8: Run GREEN**

~~~bash
bash tests/test_curriculum_style_contract.sh
bash tests/test_mobile_interaction_contract.sh
bash tests/test_module_contract.sh
~~~

Expected: PASS.

- [ ] **Step 9: Commit**

~~~bash
git add tests/test_curriculum_style_contract.sh tests/test_mobile_interaction_contract.sh \
  theme_facodi/static/src/scss/curriculum.scss theme_facodi/tests/test_website.py
git commit -m "feat(curriculum): apply Campus Paper to Roadmaps and units"
~~~

---

### Task 4: Refactor reusable editorial snippets into the paper language

**Files:**
- Modify: theme_facodi/views/snippets/s_facodi_intro.xml
- Modify: theme_facodi/views/snippets/s_facodi_editorial_routes.xml
- Modify: theme_facodi/views/snippets/s_facodi_editorial_pathway.xml
- Modify: theme_facodi/static/src/scss/curriculum.scss
- Modify: theme_facodi/static/src/scss/snippets.scss
- Modify: tests/test_foundation_v2_contract.sh
- Modify: theme_facodi/tests/test_website.py

**Interfaces:**
- Consumes: Phase A paper primitives.
- Produces: facodi-editorial-intro-sheet, facodi-editorial-route-card and facodi-editorial-pathway-sheet.

- [ ] **Step 1: Add failing editorial assertions**

Extend tests/test_foundation_v2_contract.sh:

~~~bash
INTRO="theme_facodi/views/snippets/s_facodi_intro.xml"
ROUTES="theme_facodi/views/snippets/s_facodi_editorial_routes.xml"
PATHWAY="theme_facodi/views/snippets/s_facodi_editorial_pathway.xml"

grep -Fq 'facodi-editorial-intro-sheet' "$INTRO" \
  || fail "editorial intro must expose a paper-sheet hook"
grep -Fq 'facodi-editorial-route-card' "$ROUTES" \
  || fail "editorial routes need reusable paper cards"
grep -Fq 'facodi-editorial-pathway-sheet' "$PATHWAY" \
  || fail "editorial pathway needs a paper-sheet hook"
~~~

- [ ] **Step 2: Run RED**

~~~bash
bash tests/test_foundation_v2_contract.sh
~~~

Expected: FAIL on facodi-editorial-intro-sheet.

- [ ] **Step 3: Wrap editorial intro in a study sheet**

Preserve copy and XML ID:

~~~xml
<section class="s_facodi_intro facodi-section facodi-grid-paper o_cc o_cc1"
         data-snippet="s_facodi_intro"
         data-name="FACODI Editorial intro">
    <div class="container">
        <div class="facodi-sheet facodi-editorial-intro-sheet">
            <p class="facodi-kicker">FACODI · Open knowledge</p>
            <h1><span class="facodi-highlight">Learning means building together.</span></h1>
            <p class="facodi-lead">A space to present ideas, share resources and give context to your learning journey.</p>
        </div>
    </div>
</section>
~~~

No new source strings.

- [ ] **Step 4: Turn editorial destinations into paper cards**

Keep the same three routes and copy in s_facodi_editorial_routes.xml. Add facodi-sheet facodi-editorial-route-card to each anchor while preserving the facodi-editorial-routes-list nav landmark.

- [ ] **Step 5: Wrap editorial pathway in a reference sheet**

Keep its existing two-step copy and routes. Add a facodi-sheet facodi-editorial-pathway-sheet wrapper around the heading plus ordered list.

- [ ] **Step 6: Add shared editorial styles**

~~~scss
.facodi-site {
    .facodi-editorial-intro-sheet,
    .facodi-editorial-pathway-sheet {
        padding: clamp(1.5rem, 4vw, 3rem);
    }

    .facodi-editorial-routes-list {
        border: 0;
        gap: 1rem;

        .facodi-editorial-route-card {
            color: var(--facodi-ink);
            min-width: 0;
            padding: 1.25rem;

            strong,
            span {
                display: block;
                overflow-wrap: anywhere;
            }

            span {
                margin-top: .5rem;
            }
        }
    }

    .facodi-pathway-step {
        border-top: 1px dashed var(--facodi-ink);
    }
}
~~~

- [ ] **Step 7: Preserve Website Builder registration**

In test_facodi_snippets_are_registered change the expected class for s_facodi_intro to facodi-editorial-intro-sheet. Keep XML IDs and registry structure stable.

- [ ] **Step 8: Run GREEN**

~~~bash
bash tests/test_foundation_v2_contract.sh
bash tests/test_module_contract.sh
bash tests/test_i18n_contract.sh
~~~

Expected: PASS with no PO/POT changes because source copy is unchanged.

- [ ] **Step 9: Commit**

~~~bash
git add theme_facodi/views/snippets/s_facodi_intro.xml \
  theme_facodi/views/snippets/s_facodi_editorial_routes.xml \
  theme_facodi/views/snippets/s_facodi_editorial_pathway.xml \
  theme_facodi/static/src/scss/curriculum.scss theme_facodi/static/src/scss/snippets.scss \
  tests/test_foundation_v2_contract.sh theme_facodi/tests/test_website.py
git commit -m "feat(editorial): unify FACODI pages with Campus Paper"
~~~

---

### Task 5: Normalize shared academic/ecosystem cards and bump release

**Files:**
- Modify: theme_facodi/static/src/scss/foundation_v2.scss
- Modify: theme_facodi/__manifest__.py
- Modify: tests/test_module_contract.sh
- Modify: tests/test_campus_paper_contract.sh

**Interfaces:**
- Consumes existing area/ecosystem classes and Phase A tokens.
- Produces token-consistent shared cards and release version 19.0.7.0.0.

- [ ] **Step 1: Add failing release/token assertions**

In tests/test_module_contract.sh require:

~~~bash
grep -Fq '"version": "19.0.7.0.0"' theme_facodi/__manifest__.py \
  || fail "Campus Paper global-surfaces release version missing"
~~~

In tests/test_campus_paper_contract.sh require foundation_v2.scss to use var(--facodi-border), var(--facodi-radius) and var(--facodi-shadow) for facodi-area-card.

- [ ] **Step 2: Run RED**

~~~bash
bash tests/test_module_contract.sh
bash tests/test_campus_paper_contract.sh
~~~

Expected: FAIL on version 19.0.7.0.0.

- [ ] **Step 3: Move academic-area cards onto shared geometry**

~~~scss
.facodi-site .facodi-area-card {
    border: var(--facodi-border);
    border-radius: var(--facodi-radius);
    box-shadow: var(--facodi-shadow);
}
~~~

Keep current area colors and responsive 4→2→1 grid.

- [ ] **Step 4: Normalize ecosystem card geometry**

~~~scss
.facodi-site .facodi-ecosystem-card {
    border: 1px solid color-mix(in srgb, var(--facodi-white) 54%, transparent);
    border-radius: var(--facodi-radius);
}
~~~

Keep the existing dark ecosystem section and external links.

- [ ] **Step 5: Bump manifest**

Set:

~~~python
"version": "19.0.7.0.0",
~~~

No dependency change.

- [ ] **Step 6: Run GREEN**

~~~bash
bash tests/test_module_contract.sh
bash tests/test_campus_paper_contract.sh
bash tests/test_foundation_v2_contract.sh
~~~

Expected: PASS.

- [ ] **Step 7: Commit**

~~~bash
git add theme_facodi/__manifest__.py theme_facodi/static/src/scss/foundation_v2.scss \
  tests/test_module_contract.sh tests/test_campus_paper_contract.sh
git commit -m "refactor(theme): normalize Campus Paper global card geometry"
~~~

---

### Task 6: Prove install/upgrade, i18n preservation and visual acceptance

**Files:**
- Modify: .github/workflows/ci.yml
- Modify: README.md
- Modify: docs/validation.md
- Modify: tests/test_i18n_contract.sh
- Optional evidence only when actually produced: docs/validation/campus-paper-global-*.png

**Interfaces:**
- Consumes all Phase B changes.
- Produces exact-head CI and acceptance evidence for 19.0.7.0.0; still no deployment pin.

- [ ] **Step 1: Update CI release guard and add new contracts**

Add:

~~~yaml
- name: FACODI global shell contract
  run: bash tests/test_global_shell_contract.sh

- name: FACODI curriculum presentation contract
  run: bash tests/test_curriculum_style_contract.sh
~~~

Change the current-release grep to 19.0.7.0.0. Keep the same historical legacy SHA from Phase A so upgrade/editor-preservation evidence remains comparable.

- [ ] **Step 2: Protect i18n against accidental untranslated source changes**

Add to tests/test_i18n_contract.sh:

~~~bash
for view in \
  theme_facodi/views/header.xml \
  theme_facodi/views/customizations.xml \
  theme_facodi/views/snippets/s_facodi_intro.xml \
  theme_facodi/views/snippets/s_facodi_editorial_routes.xml \
  theme_facodi/views/snippets/s_facodi_editorial_pathway.xml; do
  [[ -f "$view" ]] || fail "missing translated global/editorial view: $view"
done
~~~

Tasks 1–5 deliberately preserve source copy. If implementation changes any user-facing source string, that same commit must update theme_facodi.pot plus pt.po, es.po and fr.po and add a concrete translation assertion before continuing.

- [ ] **Step 3: Update README**

Document 19.0.7.0.0 as the global Campus Paper release:
- native Odoo header/Portal/mobile behavior preserved;
- footer and public forms use Campus Paper;
- website_slides catalogue/course/lesson surfaces styled without replacing logic;
- Roadmaps/UCs styled through facodi-learning public CSS hooks;
- editorial snippets share paper primitives.

- [ ] **Step 4: Extend docs/validation.md**

Add a Phase B matrix covering:
- desktop/mobile header and account dropdown;
- footer grouping and long translated menu names;
- /slides catalogue;
- one real course detail;
- /roadmaps and one Roadmap detail;
- /unidades-curriculares filter/index and one UC detail;
- one editorial page using intro/routes/pathway;
- keyboard focus and reduced motion;
- custom course cover preservation.

- [ ] **Step 5: Run all fast contracts**

~~~bash
bash tests/test_module_contract.sh
bash tests/test_campus_paper_contract.sh
bash tests/test_global_shell_contract.sh
bash tests/test_homepage_dashboard_contract.sh
bash tests/test_foundation_v2_contract.sh
bash tests/test_curriculum_style_contract.sh
bash tests/test_i18n_contract.sh
bash tests/test_elearning_catalog_style_contract.sh
bash tests/test_mobile_interaction_contract.sh
~~~

Expected: all PASS.

- [ ] **Step 6: Run Odoo clean-install/upgrade CI on exact branch head**

Require Odoo 19 Theme CI / test success. It must prove legacy install, theme upgrade, asset compilation, Website Builder preservation, standard header rendering and eLearning catalogue rendering.

- [ ] **Step 7: Perform visual acceptance on a disposable integrated runtime**

Required viewports:

~~~text
Header + homepage: 1440x1200, 1024x1366, 390x844, 320x700
/slides: 1440x1200, 390x844, 320x700
one /slides/<course>: 1440x1200, 390x844
/roadmaps: 1440x1200, 390x844
one /roadmaps/<id>: 1440x1200, 390x844
/unidades-curriculares: 1440x1200, 390x844, 320x700
one curricular-unit detail: 1440x1200, 390x844
~~~

Inspect:
- no page-level horizontal scrollbar;
- header dropdown/menu/account remain usable;
- custom course cover is not replaced;
- course/lesson titles wrap;
- Roadmap/UC filter form stacks;
- wide tables scroll internally;
- provenance/academic-boundary copy remains readable and unaltered;
- footer groups remain readable;
- focus remains visible;
- reduced-motion mode does not hide or reorder content.

Store screenshots only when actually captured and inspected.

- [ ] **Step 8: Commit verification evidence**

~~~bash
git add .github/workflows/ci.yml README.md docs/validation.md tests/test_i18n_contract.sh
git commit -m "test(theme): verify Campus Paper global surfaces release"
~~~

Add screenshot files only if they were actually produced and inspected.

---

## Final Phase B Verification

Run fresh:

~~~bash
bash tests/test_module_contract.sh
bash tests/test_campus_paper_contract.sh
bash tests/test_global_shell_contract.sh
bash tests/test_homepage_dashboard_contract.sh
bash tests/test_foundation_v2_contract.sh
bash tests/test_curriculum_style_contract.sh
bash tests/test_i18n_contract.sh
bash tests/test_elearning_catalog_style_contract.sh
bash tests/test_mobile_interaction_contract.sh
~~~

Then require exact-head Odoo 19 Theme CI success and whole-branch review against the approved specification.

## Phase B Completion Boundary

Phase B is complete when:

- global header/mobile/Portal behavior is still native Odoo and visually matches Campus Paper;
- footer and standard public controls share the same visual system;
- catalogue, course, lesson and progress surfaces use Campus Paper without changing website_slides semantics;
- Roadmaps and Curricular Units use the same study-object vocabulary through existing facodi-learning CSS hooks;
- editorial snippets use shared paper primitives;
- PT/ES/FR remain green;
- clean install/upgrade and Website Builder preservation remain green;
- required visual acceptance has been performed on a disposable runtime.

It does not update facodi-deploy. Phase C starts only after this branch is reviewed and integrated: advance the exact green facodi-theme gitlink in facodi-deploy, run deployment repository/runtime gates and disposable Coolify acceptance, then decide production promotion.
