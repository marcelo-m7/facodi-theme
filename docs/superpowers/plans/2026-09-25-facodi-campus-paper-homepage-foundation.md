# FACODI Campus Paper Homepage Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended when available) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Build the reusable FACODI Campus Paper design-system foundation and refactor the editable homepage into that visual language while preserving Odoo-native Website Builder, dynamic course data, Portal, translations and website_slides behavior.

**Architecture:** This is Phase A of the approved Campus Paper specification. It introduces semantic runtime tokens and paper primitives, then refactors existing stable FACODI snippets rather than replacing them with a static landing page. Dynamic course data stays on Odoo website.snippet.filter + slide.channel; English remains the QWeb source language and PT/ES/FR stay in native PO catalogues.

**Tech Stack:** Odoo 19 Community, QWeb, Website Builder snippets, website_slides, SCSS/CSS custom properties, native Odoo i18n PO/POT catalogues, Bash contract tests, Odoo HttpCase, GitHub Actions, PostgreSQL 16 and odoo:19.0.

**Spec:** docs/superpowers/specs/2026-09-25-facodi-campus-paper-visual-system-design.md

## Global Constraints

- Target Odoo 19 Community.
- Keep theme_facodi presentation-only.
- Preserve Website Builder, Website menus, Portal identity controls and native localization.
- Preserve website_slides as owner of courses, lessons, enrolment, progress and routes.
- Do not add controllers, authentication, parallel course/page models or ORM searches in QWeb.
- English remains canonical QWeb source; PT/ES/FR remain native PO catalogues.
- Do not add remote Google Font requests.
- Preserve stable snippet XML IDs.
- Dynamic course data must continue to use published slide.channel records through the existing Odoo dynamic-snippet infrastructure.
- No invented metrics, live-state claims, fake progress or academic-recognition claims.
- Preserve :focus-visible, prefers-reduced-motion and no-horizontal-overflow behavior.
- Production is not an experimentation surface.
- No facodi-deploy write belongs to this plan.

## Scope decomposition

This plan implements only **Phase A: Campus Paper foundation + homepage v3**.

A later Phase B plan carries the same system into global header/footer polish, standard eLearning surfaces, Roadmaps, Curricular Units and editorial pages. A Phase C plan advances the exact green facodi-theme gitlink in facodi-deploy and runs disposable Coolify acceptance before production promotion.

## Review Focus

1. **Long translated hero copy at 320 px** — it must wrap without horizontal overflow or overlap. Covered in Task 2.
2. **Zero published courses** — the dynamic showcase must preserve Odoo’s empty-state contract and render no invented course data. Covered in Task 4.
3. **Persisted Website Builder markup from the previous theme release** — module upgrade must preserve editor-owned content and the legacy dynamic-snippet structure. Covered in Task 7.
4. **Keyboard-only navigation with reduced motion** — cards and actions must keep visible focus and must not require transforms to remain usable. Covered in Tasks 1 and 7.
5. **Long PT/ES/FR strings** — localized homepage routes must use native catalogues without language-specific QWeb branches. Covered in Task 6.

---

### Task 1: Add Campus Paper runtime tokens and reusable primitives

**Files:**
- Create: theme_facodi/static/src/scss/campus_paper_tokens.scss
- Create: theme_facodi/static/src/scss/paper_primitives.scss
- Create: tests/test_campus_paper_contract.sh
- Modify: theme_facodi/static/src/scss/primary_variables.scss
- Modify: theme_facodi/static/src/scss/components.scss
- Modify: theme_facodi/__manifest__.py
- Modify: tests/test_module_contract.sh

**Interfaces:**
- Consumes: existing .facodi-site scope and current palette.
- Produces: semantic CSS custom properties and reusable paper/highlight/label primitives used by every later task.

- [ ] **Step 1: Write the failing design-system contract**

Create tests/test_campus_paper_contract.sh:

~~~bash
#!/usr/bin/env bash
set -euo pipefail

fail() { echo "FAIL: $*" >&2; exit 1; }

TOKENS="theme_facodi/static/src/scss/campus_paper_tokens.scss"
PRIMITIVES="theme_facodi/static/src/scss/paper_primitives.scss"
MANIFEST="theme_facodi/__manifest__.py"

[[ -f "$TOKENS" ]] || fail "Campus Paper token file missing"
[[ -f "$PRIMITIVES" ]] || fail "Campus Paper primitive file missing"

for token in --facodi-ink-deep --facodi-sun-bright --facodi-mint-strong \
  --facodi-sky --facodi-coral --facodi-pink --facodi-paper-warm \
  --facodi-surface-page --facodi-surface-sheet --facodi-border \
  --facodi-shadow --facodi-shadow-hover --facodi-focus-ring; do
  grep -Fq -- "$token" "$TOKENS" || fail "missing token: $token"
done

for selector in .facodi-paper .facodi-grid-paper .facodi-sheet .facodi-note \
  .facodi-postit .facodi-highlight .facodi-marker-line .facodi-label \
  .facodi-tab .facodi-button-ghost; do
  grep -Fq "$selector" "$PRIMITIVES" || fail "missing primitive: $selector"
done

grep -Fq 'campus_paper_tokens.scss' "$MANIFEST" || fail "tokens not loaded"
grep -Fq 'paper_primitives.scss' "$MANIFEST" || fail "primitives not loaded"
grep -Fq ':focus-visible' "$PRIMITIVES" || fail "focus treatment missing"
grep -Fq 'prefers-reduced-motion: reduce' "$PRIMITIVES" || fail "reduced-motion treatment missing"

if grep -RniE '@import[[:space:]]+url|fonts\.googleapis\.com|fonts\.gstatic\.com' \
  theme_facodi/static theme_facodi/views; then
  fail "theme must not request remote fonts"
fi

echo "PASS: Campus Paper design-system contract"
~~~

- [ ] **Step 2: Run it and verify RED**

Run:

~~~bash
bash tests/test_campus_paper_contract.sh
~~~

Expected: exit 1 with “Campus Paper token file missing”.

- [ ] **Step 3: Extend primary_variables.scss**

Add:

~~~scss
$facodi-ink-deep: #0B1325;
$facodi-sun-bright: #FAFF00;
$facodi-mint-strong: #86EFAC;
$facodi-sky: #38BDF8;
$facodi-coral: #FF8A7A;
$facodi-pink: #F9A8D4;
$facodi-paper-warm: #FDFCF7;
~~~

Keep the existing Odoo color-palette mapping stable.

- [ ] **Step 4: Create campus_paper_tokens.scss**

~~~scss
.facodi-site {
    --facodi-ink: #142846;
    --facodi-ink-deep: #0B1325;
    --facodi-sun: #EFFF00;
    --facodi-sun-bright: #FAFF00;
    --facodi-mint: #A7E8BE;
    --facodi-mint-strong: #86EFAC;
    --facodi-cyan: #37BED2;
    --facodi-blue: #3979C8;
    --facodi-sky: #38BDF8;
    --facodi-coral: #FF8A7A;
    --facodi-pink: #F9A8D4;
    --facodi-paper: #F9FAFB;
    --facodi-paper-warm: #FDFCF7;
    --facodi-white: #FFFFFF;
    --facodi-surface-page: var(--facodi-paper-warm);
    --facodi-surface-sheet: var(--facodi-white);
    --facodi-border: 2px solid var(--facodi-ink);
    --facodi-shadow: 4px 4px 0 var(--facodi-ink);
    --facodi-shadow-hover: 2px 2px 0 var(--facodi-ink);
    --facodi-focus-ring: 0 0 0 3px var(--facodi-paper-warm), 0 0 0 6px var(--facodi-ink);
    --facodi-radius-sm: .25rem;
    --facodi-radius: .5rem;
    --facodi-radius-lg: .75rem;
}
~~~

- [ ] **Step 5: Create paper_primitives.scss**

Implement .facodi-paper, .facodi-grid-paper, .facodi-sheet, .facodi-note, .facodi-postit, .facodi-highlight, .facodi-marker-line, .facodi-label, .facodi-tab and .facodi-button-ghost. Use var(--facodi-border), var(--facodi-shadow), 24px graph-paper grid lines, dark ink text, visible :focus-visible and a prefers-reduced-motion block that removes decorative transforms.

- [ ] **Step 6: Load the new files first in web.assets_frontend**

Use this order:

~~~python
"web.assets_frontend": [
    "theme_facodi/static/src/scss/campus_paper_tokens.scss",
    "theme_facodi/static/src/scss/paper_primitives.scss",
    "theme_facodi/static/src/scss/components.scss",
    "theme_facodi/static/src/scss/website.scss",
    "theme_facodi/static/src/scss/snippets.scss",
    "theme_facodi/static/src/scss/foundation_v2.scss",
    "theme_facodi/static/src/scss/website_slides.scss",
    "theme_facodi/static/src/scss/curriculum.scss",
],
~~~

- [ ] **Step 7: Move generic card/button geometry onto semantic tokens**

In components.scss, make .facodi-card and .facodi-stat-card consume var(--facodi-surface-sheet), var(--facodi-border), var(--facodi-radius) and var(--facodi-shadow). Keep existing Odoo component semantics and color-combination ownership.

- [ ] **Step 8: Bump the theme version and extend module contract**

Set manifest version to 19.0.6.0.0. Extend tests/test_module_contract.sh to require campus_paper_tokens.scss and paper_primitives.scss and to assert the new release version.

- [ ] **Step 9: Verify GREEN**

~~~bash
bash tests/test_campus_paper_contract.sh
bash tests/test_module_contract.sh
~~~

Expected: both PASS.

- [ ] **Step 10: Commit**

~~~bash
git add theme_facodi tests/test_campus_paper_contract.sh tests/test_module_contract.sh
git commit -m "feat(theme): add Campus Paper design primitives"
~~~

---

### Task 2: Rebuild the hero as a Campus Paper study board

**Files:**
- Modify: theme_facodi/views/snippets/s_facodi_hero.xml
- Modify: theme_facodi/static/src/scss/snippets.scss
- Modify: theme_facodi/tests/test_website.py
- Modify: tests/test_foundation_v2_contract.sh
- Modify: tests/test_mobile_interaction_contract.sh

**Interfaces:**
- Consumes: Task 1 tokens/primitives.
- Produces: stable theme_facodi.s_facodi_hero with .facodi-hero-study-board, .facodi-study-sheet, .facodi-study-note and .facodi-study-route.

- [ ] **Step 1: Add failing hero assertions**

Require these source anchors in tests/test_foundation_v2_contract.sh:

~~~text
Learn in public.
Open higher education, one useful next step at a time.
Explore free courses
How FACODI works
facodi-hero-study-board
facodi-study-sheet
facodi-study-note
facodi-study-route
~~~

Also fail if s_facodi_hero.xml still contains facodi-live-dot, because the visual must not imply live state without live data.

- [ ] **Step 2: Add failing mobile assertions**

In tests/test_mobile_interaction_contract.sh require a max-width: 767.98px rule for snippets.scss and overflow-wrap: anywhere on long hero text.

- [ ] **Step 3: Run RED**

~~~bash
bash tests/test_foundation_v2_contract.sh
bash tests/test_mobile_interaction_contract.sh
~~~

Expected: failure on the new hero anchors.

- [ ] **Step 4: Replace only hero internals, preserving its XML ID**

Use this content structure:

~~~xml
<section class="s_facodi_hero facodi-hero facodi-grid-paper o_cc o_cc1"
         data-snippet="s_facodi_hero" data-name="FACODI Hero">
    <div class="facodi-hero-copy">
        <p class="facodi-kicker">FACODI · An open digital campus</p>
        <h1><span class="facodi-highlight">Learn in public.</span></h1>
        <p class="facodi-hero-subtitle">Open higher education, one useful next step at a time.</p>
        <p class="facodi-lead">Courses, Roadmaps and curricular units connect public learning resources so you can start with a question and keep following the thread.</p>
        <div class="facodi-actions">
            <a class="btn facodi-button facodi-button-primary" href="/slides">Explore free courses</a>
            <a class="btn facodi-button facodi-button-secondary" href="/contactus">How FACODI works</a>
        </div>
    </div>
    <div class="facodi-hero-study-board" aria-label="FACODI learning map">
        <article class="facodi-sheet facodi-study-sheet">
            <span class="facodi-tab">Roadmap</span>
            <p class="facodi-label">Question 01</p>
            <h2>Start with what you want to understand.</h2>
            <div class="facodi-study-route" aria-hidden="true">
                <span>01</span><i></i><span>02</span><i></i><span>03</span>
            </div>
        </article>
        <article class="facodi-note facodi-study-note">
            <span class="facodi-label">Curricular unit</span>
            <strong>Find verified academic context.</strong>
        </article>
        <article class="facodi-postit facodi-study-note facodi-study-note-secondary">
            <span class="facodi-label">Course</span>
            <strong>Keep following the useful thread.</strong>
        </article>
    </div>
</section>
~~~

- [ ] **Step 5: Implement responsive hero CSS**

Use a two-column desktop grid with minmax(0, ...) columns, clamp-based type/spacing, max 13ch heading width, overflow-wrap: anywhere and a relative study-board. At max-width 767.98px collapse to one column, remove decorative rotations, keep notes inside the viewport, and keep a single readable flow at 320 px.

- [ ] **Step 6: Add an Odoo rendered-home test**

Add:

~~~python
def test_homepage_renders_campus_paper_hero(self):
    from lxml import html
    response = self.url_open("/")
    self.assertEqual(response.status_code, 200)
    tree = html.fromstring(response.text)
    hero = tree.xpath("//section[contains(@class, 'facodi-hero')]")
    self.assertEqual(len(hero), 1)
    self.assertTrue(hero[0].xpath(".//*[contains(@class, 'facodi-hero-study-board')]"))
    self.assertIn("Learn in public.", hero[0].text_content())
    self.assertNotIn("real-time", hero[0].text_content().lower())
~~~

- [ ] **Step 7: Run GREEN**

~~~bash
bash tests/test_foundation_v2_contract.sh
bash tests/test_mobile_interaction_contract.sh
bash tests/test_module_contract.sh
~~~

Expected: PASS.

- [ ] **Step 8: Commit**

~~~bash
git add theme_facodi/views/snippets/s_facodi_hero.xml theme_facodi/static/src/scss/snippets.scss \
  theme_facodi/tests/test_website.py tests/test_foundation_v2_contract.sh tests/test_mobile_interaction_contract.sh
git commit -m "feat(home): rebuild FACODI hero as Campus Paper study board"
~~~

---

### Task 3: Turn entry points and learning journey into reusable study cards

**Files:**
- Modify: theme_facodi/views/snippets/s_facodi_learning_journey.xml
- Modify: theme_facodi/views/snippets/s_facodi_features.xml
- Modify: theme_facodi/static/src/scss/snippets.scss
- Modify: tests/test_foundation_v2_contract.sh
- Modify: theme_facodi/tests/test_website.py

**Interfaces:**
- Consumes: Task 1 primitives and existing /slides, /roadmaps and /unidades-curriculares routes.
- Produces: .facodi-learning-entry-grid and .facodi-learning-steps.

- [ ] **Step 1: Add failing source contracts**

Require learning_journey to contain Where do you want to begin?, Courses, Roadmaps, Curricular units, facodi-learning-entry-grid, plus exact hrefs /slides, /roadmaps and /unidades-curriculares.

Require features to contain From curiosity to the next click., Choose a question, Study at your pace, Follow the next useful thread and facodi-learning-steps.

- [ ] **Step 2: Run RED**

~~~bash
bash tests/test_foundation_v2_contract.sh
~~~

Expected: failure on facodi-learning-entry-grid.

- [ ] **Step 3: Refactor learning_journey**

Build three anchor cards:
- Courses → /slides → mint.
- Roadmaps → /roadmaps → sky.
- Curricular units → /unidades-curriculares → sun.

Each card must contain a .facodi-label, icon, h3, one explanatory paragraph and .facodi-text-link.

- [ ] **Step 4: Refactor features into the three-step journey**

Use three paper objects:
- 01 · Starting point — Choose a question.
- 02 · No rush — Study at your pace.
- 03 · Continuity — Follow the next useful thread.

Keep s_facodi_features as the stable XML ID.

- [ ] **Step 5: Add shared SCSS**

Define .facodi-learning-entry-grid and .facodi-learning-steps as three minmax(0, 1fr) columns on desktop and one minmax(0, 1fr) column on phones. Define .facodi-learning-card using var(--facodi-border), var(--facodi-shadow), var(--facodi-radius), semantic mint/sky/sun backgrounds, visible focus, and reduced-motion-safe hover behavior.

- [ ] **Step 6: Add rendered route assertions**

~~~python
def test_homepage_learning_entries_keep_canonical_routes(self):
    from lxml import html
    tree = html.fromstring(self.url_open("/").text)
    for route, label in (
        ("/slides", "Courses"),
        ("/roadmaps", "Roadmaps"),
        ("/unidades-curriculares", "Curricular units"),
    ):
        links = tree.xpath(
            f"//a[@href='{route}' and contains(@class, 'facodi-learning-card')]"
        )
        self.assertEqual(len(links), 1, (route, label))
        self.assertIn(label, links[0].text_content())
~~~

- [ ] **Step 7: Run GREEN**

~~~bash
bash tests/test_foundation_v2_contract.sh
bash tests/test_mobile_interaction_contract.sh
~~~

Expected: PASS.

- [ ] **Step 8: Commit**

~~~bash
git add theme_facodi/views/snippets/s_facodi_learning_journey.xml \
  theme_facodi/views/snippets/s_facodi_features.xml theme_facodi/static/src/scss/snippets.scss \
  theme_facodi/tests/test_website.py tests/test_foundation_v2_contract.sh
git commit -m "feat(home): add reusable Campus Paper learning cards"
~~~

---

### Task 4: Restyle the dynamic course showcase without changing its data contract

**Files:**
- Modify: theme_facodi/views/snippets/s_facodi_course_showcase.xml
- Modify: theme_facodi/static/src/scss/snippets.scss
- Modify: tests/test_homepage_dashboard_contract.sh
- Modify: theme_facodi/tests/test_website.py

**Interfaces:**
- Consumes: theme_facodi.dynamic_filter_published_courses, website.snippet.filter, slide.channel and theme_facodi.dynamic_filter_template_slide_channel_facodi_course_card.
- Produces: same dynamic template/filter contract under a Campus Paper shell.

- [ ] **Step 1: Add failing contract assertions**

Require facodi-course-catalogue-paper and the existing empty-state sentence. Continue rejecting request.env and sudo() in the snippet. Add a guard against invented hard-coded course names such as Introduction to Algorithms.

- [ ] **Step 2: Run RED**

~~~bash
bash tests/test_homepage_dashboard_contract.sh
~~~

Expected: failure on facodi-course-catalogue-paper.

- [ ] **Step 3: Replace only the visual shell**

Preserve all three Odoo dynamic-snippet hooks:
- s_dynamic_snippet_container.
- s_dynamic_snippet_content.
- dynamic_snippet_template.

Build a paper catalogue section with:
- Learning catalogue / Published courses heading.
- tab-like links to Roadmaps, Curricular Units, Courses and Contribute.
- the existing dynamic content region.
- an editable “Next study” paper card linking to /slides.

- [ ] **Step 4: Restyle dynamic course cards**

Change .facodi-course-card from the current dark dashboard treatment to white/warm paper, dark ink, 2px border and hard offset shadow. Keep existing image/fallback behavior, total_slides rendering, course URL and channel.description_short data expressions intact.

- [ ] **Step 5: Add zero-published-course coverage**

~~~python
def test_course_showcase_does_not_invent_courses_when_none_are_published(self):
    channels = self.env["slide.channel"].search([("website_published", "=", True)])
    channels.write({"website_published": False})
    showcase = self.env["ir.ui.view"].search([
        ("key", "=", "theme_facodi.s_facodi_course_showcase"),
        ("website_id", "!=", False),
    ], limit=1)
    self.assertTrue(showcase)
    self.assertIn("s_dynamic_snippet_content", showcase.arch_db)
    self.assertIn("Course cards appear here when published courses are available.", showcase.arch_db)
    self.assertNotIn("Introduction to Algorithms", showcase.arch_db)
~~~

- [ ] **Step 6: Run GREEN**

~~~bash
bash tests/test_homepage_dashboard_contract.sh
bash tests/test_foundation_v2_contract.sh
~~~

Expected: PASS.

- [ ] **Step 7: Commit**

~~~bash
git add theme_facodi/views/snippets/s_facodi_course_showcase.xml \
  theme_facodi/static/src/scss/snippets.scss theme_facodi/tests/test_website.py \
  tests/test_homepage_dashboard_contract.sh
git commit -m "feat(home): restyle dynamic course catalogue as Campus Paper"
~~~

---

### Task 5: Recompose the homepage around learner flow and community contribution

**Files:**
- Modify: theme_facodi/views/page_templates.xml
- Modify: theme_facodi/views/snippets/s_facodi_community.xml
- Modify: theme_facodi/views/snippets/s_facodi_institutional.xml
- Modify: theme_facodi/views/snippets/s_facodi_course_cta.xml
- Modify: theme_facodi/static/src/scss/snippets.scss
- Modify: theme_facodi/tests/test_website.py
- Modify: tests/test_foundation_v2_contract.sh

**Interfaces:**
- Consumes: stable snippet IDs from Tasks 2–4.
- Produces exact home order: Hero → Learning Entry → Learning Steps → Dynamic Courses → Academic Areas → Community → Institutional → Closing CTA.

- [ ] **Step 1: Add a failing composition-order test**

Parse new_page_template_sections_facodi_home and require exactly:

~~~text
theme_facodi.s_facodi_hero
theme_facodi.s_facodi_learning_journey
theme_facodi.s_facodi_features
theme_facodi.s_facodi_course_showcase
theme_facodi.s_facodi_academic_areas
theme_facodi.s_facodi_community
theme_facodi.s_facodi_institutional
theme_facodi.s_facodi_course_cta
~~~

- [ ] **Step 2: Run RED**

~~~bash
bash tests/test_foundation_v2_contract.sh
~~~

Expected: composition-order failure.

- [ ] **Step 3: Update the Home composition to those eight snippet calls**

Do not copy internal snippet markup into page_templates.xml.

- [ ] **Step 4: Refactor community**

Create two reusable paper cards:
- “A good discovery deserves company.” with Suggest a resource → /contribuir/recurso and Collaborate with FACODI → /contactus.
- “Help make the learning trail clearer.” with Improve a translation → /contactus.

Do not invent contribution metrics.

- [ ] **Step 5: Refactor institutional block**

Use:
- label FACODI project.
- title “We are still building. You can be part of it.”
- concise explanation of open learning resources, reviewed academic context and community contribution.
- Meet FACODI → /contactus.
- Explore SEA-EU → https://sea-eu.org/ with target=_blank and rel="noopener noreferrer".

- [ ] **Step 6: Refactor closing CTA**

Use “Keep the useful thread going.” and canonical links to /slides, /roadmaps and /unidades-curriculares.

- [ ] **Step 7: Add responsive community/institutional SCSS**

Use two minmax(0, 1fr) columns for community on desktop, one on phones. Make institutional/closing paper sheets flexible rows on desktop and vertical stacks on phones.

- [ ] **Step 8: Update New Page rendering expectations**

In test_native_templates_render_create_and_preserve_editor_content, detect Home by facodi-hero-study-board and assert:
- Learn in public.
- A good discovery deserves company.
- Keep the useful thread going.
- exactly eight Home sections.

Keep the existing editor-preservation round trip after theme reload.

- [ ] **Step 9: Run GREEN**

~~~bash
bash tests/test_foundation_v2_contract.sh
bash tests/test_homepage_dashboard_contract.sh
bash tests/test_module_contract.sh
~~~

Expected: PASS.

- [ ] **Step 10: Commit**

~~~bash
git add theme_facodi/views/page_templates.xml theme_facodi/views/snippets \
  theme_facodi/static/src/scss/snippets.scss theme_facodi/tests/test_website.py \
  tests/test_foundation_v2_contract.sh
git commit -m "feat(home): compose Campus Paper learner and community flow"
~~~

---

### Task 6: Refresh native i18n catalogues for Campus Paper copy

**Files:**
- Modify: theme_facodi/i18n/theme_facodi.pot
- Modify: theme_facodi/i18n/pt.po
- Modify: theme_facodi/i18n/es.po
- Modify: theme_facodi/i18n/fr.po
- Modify: tests/test_i18n_contract.sh
- Modify: theme_facodi/tests/test_i18n.py

**Interfaces:**
- Consumes: English QWeb source strings from Tasks 2–5.
- Produces: native PT/ES/FR translations with theme.ir.ui.view source references.

- [ ] **Step 1: Add failing msgid anchors**

Require these msgids in POT and all three PO files:

~~~text
Learn in public.
Open higher education, one useful next step at a time.
Explore free courses
Where do you want to begin?
From curiosity to the next click.
Choose a question
Study at your pace
Follow the next useful thread
A good discovery deserves company.
We are still building. You can be part of it.
Keep the useful thread going.
~~~

Keep existing guards against hard-coded Portuguese and custom language branching.

- [ ] **Step 2: Run RED**

~~~bash
bash tests/test_i18n_contract.sh
~~~

Expected: failure on Learn in public.

- [ ] **Step 3: Add Portuguese translations**

Use:
- Learn in public. → Aprender em público.
- Open higher education, one useful next step at a time. → Ensino superior aberto, um próximo passo útil de cada vez.
- Explore free courses → Explorar cursos gratuitos.
- Where do you want to begin? → Por onde queres começar?
- From curiosity to the next click. → Da curiosidade ao próximo clique.
- Choose a question → Escolhe uma pergunta.
- Study at your pace → Estuda ao teu ritmo.
- Follow the next useful thread → Segue o próximo fio útil.
- A good discovery deserves company. → Uma boa descoberta merece companhia.
- We are still building. You can be part of it. → Ainda estamos a construir. Podes fazer parte.
- Keep the useful thread going. → Continua a seguir o fio que te ajuda.

- [ ] **Step 4: Add Spanish translations**

Use:
- Aprender en público.
- Educación superior abierta, un siguiente paso útil cada vez.
- Explorar cursos gratuitos.
- ¿Por dónde quieres empezar?
- De la curiosidad al siguiente clic.
- Elige una pregunta.
- Estudia a tu ritmo.
- Sigue el siguiente hilo útil.
- Un buen descubrimiento merece compañía.
- Todavía estamos construyendo. Puedes formar parte.
- Sigue el hilo que te ayuda.

- [ ] **Step 5: Add French translations**

Use:
- Apprendre en public.
- Un enseignement supérieur ouvert, une prochaine étape utile à la fois.
- Explorer les cours gratuits.
- Par où veux-tu commencer ?
- De la curiosité au prochain clic.
- Choisis une question.
- Étudie à ton rythme.
- Suis le prochain fil utile.
- Une bonne découverte mérite d’être partagée.
- Nous construisons encore. Tu peux en faire partie.
- Continue à suivre le fil qui t’aide.

- [ ] **Step 6: Update POT source references**

Every new msgid must point at the actual theme.ir.ui.view QWeb record that contains the source string. Do not add an en.po file.

- [ ] **Step 7: Add localized render assertions**

Extend the existing language test setup to request PT, ES and FR homepage routes and assert the localized hero title:
- pt_PT → Aprender em público.
- es_ES → Aprender en público.
- fr_FR → Apprendre en public.

Reuse the repository’s existing language activation and routing helpers.

- [ ] **Step 8: Run GREEN**

~~~bash
bash tests/test_i18n_contract.sh
~~~

Expected: PASS.

- [ ] **Step 9: Commit**

~~~bash
git add theme_facodi/i18n theme_facodi/tests/test_i18n.py tests/test_i18n_contract.sh
git commit -m "feat(i18n): translate Campus Paper homepage copy"
~~~

---

### Task 7: Prove release safety and record evidence

**Files:**
- Modify: .github/workflows/ci.yml
- Modify: docs/validation.md
- Modify: README.md
- Modify: theme_facodi/tests/test_website.py
- Modify: tests/test_mobile_interaction_contract.sh
- Optional evidence only when actually produced: docs/validation/campus-paper-*.png

**Interfaces:**
- Consumes: complete Phase A implementation.
- Produces: release evidence for theme_facodi 19.0.6.0.0, not a deployment pin.

- [ ] **Step 1: Add compiled-asset assertions**

Extend test_standard_forms_and_compiled_frontend_assets to require:
- --facodi-ink-deep
- --facodi-paper-warm
- .facodi-grid-paper
- .facodi-postit
- .facodi-learning-card
- .facodi-course-catalogue-paper

- [ ] **Step 2: Pin mobile-critical selectors**

Extend tests/test_mobile_interaction_contract.sh to require .facodi-hero, .facodi-learning-entry-grid, .facodi-learning-steps and .facodi-community-grid plus the phone single-column minmax(0, 1fr) rule.

- [ ] **Step 3: Update the CI release-version guard**

Change only the current-release grep from 19.0.5.0.4 to 19.0.6.0.0. Keep the historical legacy baseline SHA unchanged so upgrade preservation remains meaningful.

- [ ] **Step 4: Update README**

Add a Campus Paper section documenting:
- warm paper/graph-paper surfaces.
- ink borders and hard offset shadows.
- lime/mint/cyan study accents.
- editable snippets rather than copied static HTML.
- dynamic course cards still backed by website.snippet.filter + slide.channel.
- no remote font requests.

- [ ] **Step 5: Update docs/validation.md**

Record the 19.0.6.0.0 matrix:
- semantic tokens/primitives.
- no remote fonts.
- editable hero, entry, journey, community, institutional and closing CTA.
- standard dynamic-course empty state.
- canonical learning routes.
- PT/ES/FR translations.
- phone collapse.
- focus/reduced motion.
- persisted Website Builder content across upgrade.

- [ ] **Step 6: Run every fast contract**

~~~bash
bash tests/test_module_contract.sh
bash tests/test_campus_paper_contract.sh
bash tests/test_homepage_dashboard_contract.sh
bash tests/test_foundation_v2_contract.sh
bash tests/test_i18n_contract.sh
bash tests/test_elearning_catalog_style_contract.sh
bash tests/test_mobile_interaction_contract.sh
~~~

Expected: every command exits 0 and prints PASS.

- [ ] **Step 7: Run the exact Odoo clean-install/upgrade CI gate**

Push the implementation branch only after fast contracts pass. Require Odoo 19 Theme CI to succeed on that exact head commit.

It must prove:
- legacy install succeeds.
- Odoo theme tests pass.
- current upgrade succeeds.
- frontend assets compile.
- persisted legacy course-showcase builder markup is repaired/preserved.
- Website Builder-created content remains intact.

- [ ] **Step 8: Perform visual acceptance on disposable/staging Odoo**

Inspect:
- Homepage 1440x1200.
- Homepage 1024x1366.
- Homepage 390x844.
- Homepage 320x700.
- /slides 1440x1200.
- /slides 390x844.

For each viewport verify:
- no horizontal scrollbar.
- no clipped hero/post-it text.
- CTA focus remains visible.
- long headings wrap instead of overlapping.
- course cards remain readable.
- zero-course state contains no invented card.
- reduced-motion mode does not hide content.

Store deterministic screenshots under docs/validation/campus-paper-*.png only if the execution harness can actually produce them. Otherwise record the exact checked viewports in docs/validation.md and do not claim pixel-perfect evidence.

- [ ] **Step 9: Commit evidence updates**

~~~bash
git add .github/workflows/ci.yml README.md docs/validation.md \
  theme_facodi/tests/test_website.py tests/test_mobile_interaction_contract.sh
git commit -m "test(theme): verify Campus Paper homepage release"
~~~

Add screenshot files only if they were actually produced and inspected.

---

## Final Phase A verification

Run again, fresh:

~~~bash
bash tests/test_module_contract.sh
bash tests/test_campus_paper_contract.sh
bash tests/test_homepage_dashboard_contract.sh
bash tests/test_foundation_v2_contract.sh
bash tests/test_i18n_contract.sh
bash tests/test_elearning_catalog_style_contract.sh
bash tests/test_mobile_interaction_contract.sh
~~~

Then require the exact branch-head Odoo 19 Theme CI workflow to be green.

Review the final diff against docs/superpowers/specs/2026-09-25-facodi-campus-paper-visual-system-design.md.

Phase A must not touch facodi-deploy, facodi-learning, Supabase, Odoo controllers, authentication or business models.

## Phase A completion boundary

Phase A is complete only when:
- the reusable Campus Paper token/primitive layer exists.
- homepage v3 is composed from editable snippets.
- dynamic courses remain Odoo-native.
- PT/ES/FR translations are native.
- clean install, upgrade and Website Builder preservation are green.
- responsive and keyboard/reduced-motion checks have evidence.
- the theme branch is ready for independent code review.

The approved specification is broader than Phase A. Phase B still carries the system into header/footer, eLearning, Roadmaps, Curricular Units and editorial pages. Phase C advances facodi-deploy only after the theme work is independently green.
