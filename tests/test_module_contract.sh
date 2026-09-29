#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

[[ -f theme_facodi/__manifest__.py ]] || fail "theme_facodi manifest missing"
[[ ! -e website_facodi ]] || fail "legacy website_facodi addon must not remain installable"
[[ -f theme_facodi/data/ir_asset.xml ]] || fail "theme primary asset record missing"
[[ ! -d theme_facodi/controllers ]] || fail "presentation theme must not add parallel learning routes/controllers"

grep -Fq '"theme_common"' theme_facodi/__manifest__.py || fail "theme_common dependency missing"
grep -Fq '"website_slides"' theme_facodi/__manifest__.py || fail "website_slides dependency missing"
grep -Fq '"website_blog"' theme_facodi/__manifest__.py || fail "website_blog dependency missing"
grep -Fq '"version": "19.0.10.66.0"' theme_facodi/__manifest__.py || fail "visual direction release version missing"
grep -Fq 'id="visual_direction_page"' theme_facodi/views/website_public.xml || fail "visual direction page missing"
grep -Fq 'data-facodi-visual-direction="1"' theme_facodi/views/website_public.xml || fail "visual direction semantic hook missing"
grep -Fq '.facodi-visual-direction' theme_facodi/static/src/scss/website_public.scss || fail "visual direction styling missing"
grep -Fq 'Theme/Education' theme_facodi/__manifest__.py || fail "theme category must be Theme/Education"
grep -Fq 'theme_facodi.primary_variables_scss' theme_facodi/data/ir_asset.xml || fail "primary variables asset key missing"
grep -Fq 'web._assets_primary_variables' theme_facodi/data/ir_asset.xml || fail "primary variables bundle missing"

# The production-safe header mirrors Odoo's own website.layout header-state
# expressions. Outside that compatibility shell, theme QWeb must not perform
# business-data access or hard-code database-specific assets.
if grep -R -nE 'request\.env|sudo\(\)|href="/theme_facodi/static/src/img/favicon\.svg"|/web/content/431' \
    theme_facodi --include='*.xml' --exclude='header.xml'; then
  fail "theme QWeb contains business-data access, a database asset id, or a forced favicon"
fi

# Website Builder color combinations own semantic heading colors. A global
# #wrapwrap heading override would make headings unreadable on dark combinations.
if grep -Eq '^[[:space:]]*#wrapwrap[[:space:]]+h[1-6]' theme_facodi/static/src/scss/website.scss \
   || grep -Fq 'color: $headings-color' theme_facodi/static/src/scss/website.scss; then
  fail "website.scss must not override Website Builder heading colors globally"
fi

# Production-safe selectable FACODI header. Existing Website databases may have
# COW/header customizations that remove the inner <nav>, so the FACODI template
# owns the stable outer header shell while composing its contents exclusively
# from Odoo Website/Portal building blocks.
for path in \
  theme_facodi/models/__init__.py \
  theme_facodi/models/theme_models.py \
  theme_facodi/views/header.xml \
  theme_facodi/static/src/builder/header.xml \
  theme_facodi/static/src/img/template_header_facodi.svg; do
  [[ -f "$path" ]] || fail "missing native FACODI header file: $path"
done

grep -Fq 'from . import models' theme_facodi/__init__.py \
  || fail "theme root must load models"
grep -Fq 'from . import theme_models' theme_facodi/models/__init__.py \
  || fail "theme models package must load theme_models"
grep -Fq '_inherit = "theme.utils"' theme_facodi/models/theme_models.py \
  || fail "theme.utils extension missing"
grep -Fq 'theme_facodi.template_header_facodi' theme_facodi/models/theme_models.py \
  || fail "FACODI header must be registered by theme.utils"
grep -Fq '_theme_facodi_post_copy' theme_facodi/models/theme_models.py \
  || fail "FACODI theme post-copy hook missing"

grep -Fq 'views/header.xml' theme_facodi/__manifest__.py \
  || fail "header view missing from manifest"
grep -Fq 'html_builder.assets' theme_facodi/__manifest__.py \
  || fail "Website Builder asset bundle missing"
grep -Fq 'theme_facodi/static/src/builder/**/*' theme_facodi/__manifest__.py \
  || fail "FACODI builder assets missing"

grep -Fq 'id="template_header_facodi"' theme_facodi/views/header.xml \
  || fail "selectable FACODI header template missing"
grep -Fq 'xpath expr="//header" position="replace"' theme_facodi/views/header.xml \
  || fail "FACODI header must target the stable outer header shell"
if grep -Fq 'xpath expr="//header//nav" position="replace"' theme_facodi/views/header.xml; then
  fail "FACODI header must not depend on an existing inner nav"
fi
grep -Fq 't-if="not no_header"' theme_facodi/views/header.xml \
  || fail "header must preserve the standard no_header contract"
grep -Fq 'data-anchor="true"' theme_facodi/views/header.xml \
  || fail "header must preserve the standard Odoo anchor"
grep -Fq 't-call="website.navbar"' theme_facodi/views/header.xml \
  || fail "header must compose the standard Website navbar"
grep -Fq 'website.placeholder_header_brand' theme_facodi/views/header.xml \
  || fail "header must retain standard configurable Website brand"
grep -Fq 'website.navbar_nav' theme_facodi/views/header.xml \
  || fail "header must use standard navbar wrapper"
grep -Fq 'website.menu_id.child_id' theme_facodi/views/header.xml \
  || fail "header must use standard dynamic Website menus"
grep -Fq '_facodi_landing_url' theme_facodi/views/header.xml \
  || fail "header must keep parent navigation separate from submenu disclosure"
grep -Fq '_inherit = "website.menu"' theme_facodi/models/theme_models.py \
  || fail "FACODI parent landing resolver must extend standard website.menu"
grep -Fq 't-call="website.submenu"' theme_facodi/views/header.xml \
  || fail "header must use native submenu recursion"
grep -Fq 'portal.placeholder_user_sign_in' theme_facodi/views/header.xml \
  || fail "header must retain standard Portal sign-in"
grep -Fq 'portal.user_dropdown' theme_facodi/views/header.xml \
  || fail "header must retain standard Portal user dropdown"
grep -Fq 'website.template_header_mobile' theme_facodi/views/header.xml \
  || fail "header must retain the standard Odoo mobile header"
grep -Fq 'id="submenu_split_navigation"' theme_facodi/views/header.xml \
  || fail "FACODI split submenu navigation missing"
grep -Fq 'inherit_id="website.submenu"' theme_facodi/views/header.xml \
  || fail "split navigation must minimally extend the standard Odoo submenu"
grep -Fq 'facodi-split-menu__link' theme_facodi/views/header.xml \
  || fail "submenu parent text must remain a real destination"
grep -Fq 'facodi-split-menu__toggle' theme_facodi/views/header.xml \
  || fail "submenu disclosure must remain a separate control"
grep -Fq 'submenu._facodi_landing_url()' theme_facodi/views/header.xml \
  || fail "hash-only parent data must resolve navigation through the presentation helper"
grep -Fq 'header_bg_color_class' theme_facodi/views/header.xml \
  || fail "header must preserve Website Builder header color state"
grep -Fq 'header_visible' theme_facodi/views/header.xml \
  || fail "header must preserve per-page header visibility"

grep -Fq 't-inherit="website.HeaderTemplateOption"' theme_facodi/static/src/builder/header.xml \
  || fail "FACODI header must extend native header picker"
grep -Fq "'header-template': 'facodi'" theme_facodi/static/src/builder/header.xml \
  || fail "FACODI header picker must set facodi header-template"
grep -Fq "views: ['theme_facodi.template_header_facodi']" theme_facodi/static/src/builder/header.xml \
  || fail "FACODI picker must activate FACODI header view"

# Every FACODI Website block must have one stable source file and one registry
# entry. The XML ids stay unchanged so page compositions and i18n remain stable.
SNIPPET_IDS=(
  s_facodi_hero
  s_facodi_learning_journey
  s_facodi_course_showcase
  s_facodi_academic_areas
  s_facodi_institutional
  s_facodi_intro
  s_facodi_features
  s_facodi_community
  s_facodi_ecosystem
  s_facodi_roadmap
  s_facodi_faq
  s_facodi_course_cta
  s_facodi_editorial_pathway
  s_facodi_editorial_routes
)

[[ -f theme_facodi/views/snippets/snippets.xml ]] \
  || fail "FACODI snippet registry missing"

for snippet_id in "${SNIPPET_IDS[@]}"; do
  path="theme_facodi/views/snippets/${snippet_id}.xml"
  [[ -f "$path" ]] || fail "missing reusable snippet source: $path"
  grep -Fq "id=\"${snippet_id}\"" "$path" \
    || fail "snippet source does not define ${snippet_id}"
  count="$(grep -R -h -o "id=\"${snippet_id}\"" theme_facodi/views/snippets --include='*.xml' | wc -l)"
  [[ "$count" -eq 1 ]] || fail "${snippet_id} must be defined exactly once"
  grep -Fq "t-snippet=\"theme_facodi.${snippet_id}\"" theme_facodi/views/snippets/snippets.xml \
    || fail "${snippet_id} is not registered in Website Builder"
done

[[ ! -f theme_facodi/views/snippets.xml ]] \
  || fail "legacy monolithic snippets.xml must be removed"

# Default snippets use the canonical FACODI editorial and learning routes.
# General contact/contribution actions go through the contextual intake.
# Production FACODI owns the editor-managed /sobre page. Homepage snippets may
# link to it, but the theme must not create or overwrite that page.
if grep -R -Fq 'href="/contactus"' theme_facodi/views/snippets --include='*.xml'; then
  fail "FACODI snippets must not bypass the contextual contact intake"
fi
grep -Fq 'href="/sobre">See how FACODI works' theme_facodi/views/snippets/s_facodi_hero.xml \
  || fail "hero explanation CTA must use the live editor-managed About page"
if grep -Riq 'dither[- _]veil' theme_facodi/static theme_facodi/views theme_facodi/__manifest__.py; then
  fail "removed Dither Veil implementation must not remain in the live theme"
fi
grep -Fq 'theme_facodi/static/src/js/facodi_catalogue_switcher.js' theme_facodi/__manifest__.py \
  || fail "homepage catalogue switcher frontend asset missing"
grep -Fq 'theme_facodi/static/src/js/facodi_interactions.js' theme_facodi/__manifest__.py \
  || fail "sitewide FACODI interaction asset missing"
grep -Fq 'data-facodi-spotlight' theme_facodi/static/src/js/facodi_interactions.js \
  || fail "FACODI spotlight interaction missing"
grep -Fq 'prefers-reduced-motion' theme_facodi/static/src/scss/components.scss \
  || fail "interaction primitives must respect reduced motion"
grep -Fq 'data-facodi-explore-map' theme_facodi/static/src/scss/enriched_surfaces.scss \
  || fail "Explore learning-map styling missing"
grep -R -Fq '/submissions/new?type=resource' theme_facodi/views/snippets --include='*.xml' \
  || fail "FACODI resource-contribution CTA must use the contextual intake"
if grep -R -Fq 'href="/contribuir/recurso"' theme_facodi/views/snippets --include='*.xml'; then
  fail "reusable snippets must not drop contribution context through the legacy alias"
fi
grep -Fq 'source=folder_tabs_contribute&amp;section=learning-navigation' theme_facodi/views/snippets/components/s_facodi_folder_tabs.xml \
  || fail "Folder Tabs contribution CTA must preserve navigation context"
grep -Fq 'source=course_showcase_contribute&amp;section=learning-catalogue' theme_facodi/views/snippets/s_facodi_course_showcase.xml \
  || fail "Course Showcase contribution CTA must preserve catalogue context"
grep -Fq 'source=cta_sheet_resource_cta&amp;section=cta-sheet' theme_facodi/views/snippets/components/s_facodi_cta_sheet.xml \
  || fail "CTA Sheet must preserve its contribution source context"
grep -R -Fq '/contact?source=' theme_facodi/views/snippets --include='*.xml' \
  || fail "FACODI contextual collaboration CTA missing"
grep -R -Fq '/submissions/new?type=correction' theme_facodi/views/snippets --include='*.xml' \
  || fail "FACODI contextual correction CTA missing"
grep -Fq 'source=study_player_question_cta&amp;section=lesson' theme_facodi/views/website_slides_player.xml \
  || fail "Study Player question CTA must preserve lesson context"

grep -Fq 'a1818df4ade65406ac0184382c0fd46f1023a22612c' .github/workflows/ci.yml >/dev/null 2>&1 \
  && fail "CI contains an addon SHA where design-themes pin is expected"
grep -Fq 'a1818df4ade65406c0cacae8b1ea676e6f70095f' .github/workflows/ci.yml || fail "CI must pin design-themes"
grep -Fq '/mnt/design-themes' .github/workflows/ci.yml || fail "CI must mount design-themes"
grep -Fq -- '-i theme_facodi' .github/workflows/ci.yml || fail "CI must install theme_facodi"
grep -Fq -- '--test-tags /theme_facodi' .github/workflows/ci.yml || fail "CI must run theme_facodi tests"

for file in primary_variables bootstrap_overridden campus_paper_tokens paper_primitives editorial_interfaces learning_interfaces components website snippets website_slides; do
  [[ -f "theme_facodi/static/src/scss/${file}.scss" ]] || fail "missing ${file}.scss"
done

for selector in \
  '.form-control' \
  '.form-select' \
  '.form-check-input' \
  '.invalid-feedback' \
  '.modal-content' \
  '.offcanvas' \
  '.accordion-button' \
  '.nav-tabs' \
  '.table' \
  '.progress' \
  '.oe_login_form'; do
  grep -Fq "$selector" theme_facodi/static/src/scss/components.scss \
    || fail "missing FACODI standard-component selector: $selector"
done

for color in '#142846' '#37BED2' '#3979C8' '#A7E8BE' '#EFFF00' '#F9FAFB'; do
  grep -Riq "$color" theme_facodi || fail "live FACODI color missing: $color"
done

if grep -RiqE '#6a4bff|#5dc7ff|#f7f6ff|#1f1e42|#111035' theme_facodi --exclude-dir=tests; then
  fail "superseded purple FACODI identity must not remain"
fi

grep -Fq "'facodi'" theme_facodi/static/src/scss/primary_variables.scss || fail "FACODI palette missing"
grep -Fq 'web.assets_frontend' theme_facodi/__manifest__.py || fail "frontend asset bundle missing"
grep -Fq 'form > .d-flex:last-child' theme_facodi/static/src/scss/enriched_surfaces.scss \
  || fail "contextual submission action row must be styled through its form parent"
grep -Fq 'web._assets_frontend_helpers' theme_facodi/data/ir_asset.xml || fail "bootstrap overrides must use frontend helpers"

grep -Fq 'facodi-footer' theme_facodi/views/customizations.xml || fail "live FACODI footer missing"
grep -Fq 'facodi-footer-heading-link' theme_facodi/views/customizations.xml || fail "footer parent destinations must remain clickable"
grep -Fq 'content="#142846"' theme_facodi/views/customizations.xml || fail "live browser theme color missing"

python3 - <<'PY'
from pathlib import Path
from xml.etree import ElementTree

source = Path("theme_facodi/views/header.xml")
root = ElementTree.parse(source).getroot()
header = root.find(".//template[@id='template_header_facodi']")
if header is None:
    raise SystemExit("FAIL: FACODI native header template missing")

parents = {
    child: parent
    for parent in header.iter()
    for child in parent
}

brand_calls = [
    node
    for node in header.iter("t")
    if node.get("t-call") == "website.placeholder_header_brand"
]
if len(brand_calls) != 1:
    raise SystemExit("FAIL: header must call the standard Website brand exactly once")

literal_brands = [
    node
    for node in header.iter("a")
    if {"navbar-brand", "facodi-wordmark"}.issubset(
        set(node.get("class", "").split())
    )
]
if literal_brands:
    raise SystemExit("FAIL: header must not replace configured Website logo with literal text")

navbar_calls = [
    node for node in header.iter("t") if node.get("t-call") == "website.navbar_nav"
]
if len(navbar_calls) != 1:
    raise SystemExit("FAIL: header must call website.navbar_nav exactly once")
navbar = navbar_calls[0]

for call_name in ("portal.placeholder_user_sign_in", "portal.user_dropdown"):
    calls = [
        node for node in header.iter("t") if node.get("t-call") == call_name
    ]
    if len(calls) != 1:
        raise SystemExit(f"FAIL: header must call {call_name} exactly once")
    call = calls[0]
    ancestor = parents.get(call)
    while ancestor is not None and ancestor is not navbar:
        ancestor = parents.get(ancestor)
    if ancestor is not navbar:
        raise SystemExit(f"FAIL: {call_name} must remain inside website.navbar_nav")
    item_sets = [
        child for child in call.findall("t") if child.get("t-set") == "_item_class"
    ]
    if len(item_sets) != 1 or "ms-lg-2" not in item_sets[0].get("t-valuef", "").split():
        raise SystemExit(f"FAIL: {call_name} must carry its own list-item spacing")
PY

grep -Fq '.o_header_mobile' theme_facodi/static/src/scss/website.scss \
  || fail "theme must style the standard Odoo mobile header instead of replacing it"

for class_name in facodi-hero facodi-hero-study-board facodi-learning-entry-grid facodi-institutional-sheet; do
  grep -R -Fq "$class_name" theme_facodi/views/snippets --include='*.xml' \
    || fail "live FACODI snippet class missing: $class_name"
done

grep -Fq 'body.o_wslides_body .facodi-site' theme_facodi/static/src/scss/website_slides.scss \
  || fail "eLearning styling must be scoped to the active FACODI theme"
grep -Fq '.o_record_cover_container[data-res-model="slide.channel"]' theme_facodi/static/src/scss/website_slides.scss \
  || fail "live eLearning course cover styling missing"
grep -Fq '.o_wslides_js_course_join_link.btn-primary' theme_facodi/static/src/scss/website_slides.scss \
  || fail "live eLearning join action styling missing"

if grep -R -n '<record[^>]*model="website.page"' theme_facodi --include='*.xml'; then
  fail "presentation theme must not import editorial Website pages"
fi

if grep -R -n '\$facodi-' theme_facodi/static/src/scss \
    --include='*.scss' --exclude='primary_variables.scss'; then
  fail "frontend SCSS must not depend on theme-primary-only FACODI variables"
fi

if grep -R -n 'website_facodi' README.md docs/architecture.md; then
  fail "current docs still describe website_facodi as the active addon"
fi

grep -Fq 'theme_common' README.md || fail "README must document theme_common"
grep -Fq 'odoo/design-themes' docs/architecture.md || fail "architecture must document upstream design-themes"
grep -Fq 'edu-open2.odoo.com' README.md || fail "README must name the live visual source"
grep -Fq '#142846' README.md || fail "README must document live FACODI ink"
grep -Fq '#EFFF00' README.md || fail "README must document live FACODI sun"
grep -Fq 'does not import Website pages' README.md || fail "README must document the editorial-page boundary"
grep -Fq 'facodi-online.css' docs/architecture.md || fail "architecture must document the database asset source"
grep -Fq 'theme_default' docs/architecture.md || fail "architecture must document the live standard theme baseline"
grep -Fq '"version": "19.0.10.65.0"' theme_facodi/__manifest__.py || fail "Campus Paper reusable-learning release version missing"

CANONICAL_ROUTE_MIGRATION="theme_facodi/migrations/19.0.10.20.0/post-20-canonical-learning-routes.py"
[[ -f "$CANONICAL_ROUTE_MIGRATION" ]] || fail "canonical learning-route upgrade migration missing"
grep -Fq '"/slides": "/courses"' "$CANONICAL_ROUTE_MIGRATION" \
  || fail "canonical migration must rewrite /slides to /courses"
grep -Fq '"/unidades-curriculares": "/curricular-units"' "$CANONICAL_ROUTE_MIGRATION" \
  || fail "canonical migration must rewrite legacy curricular-unit route"
grep -Fq '"s_facodi_course_showcase"' "$CANONICAL_ROUTE_MIGRATION" \
  || fail "canonical migration must stay scoped to persisted course-showcase navigation"

RETIRED_HERO_MIGRATION="theme_facodi/migrations/19.0.10.60.0/post-10-remove-legacy-hero-visual.py"
[[ -f "$RETIRED_HERO_MIGRATION" ]] || fail "retired hero visual cleanup migration missing"
grep -Fq '"facodi-dither-veil"' "$RETIRED_HERO_MIGRATION" \
  || fail "cleanup migration must remove persisted retired hero layers"
grep -Fq '("key", "=", _HERO_KEY)' "$RETIRED_HERO_MIGRATION" \
  || fail "retired hero cleanup must stay scoped to FACODI hero COW views"
[[ ! -f theme_facodi/migrations/19.0.10.59.0/post-10-repair-dither-veil-cow.py ]] \
  || fail "retired hero visual repair migration must be removed"

if grep -Rq 'prefers-color-scheme: dark\|background-image: none !important' theme_facodi/static/src/scss; then
  fail "partial dark mode or hidden editorial cover regression"
fi

python3 - <<'CHECK'
from pathlib import Path
from xml.etree import ElementTree as ET

for path in Path('theme_facodi').rglob('*.xml'):
    ET.parse(path)

snippet_dir = Path('theme_facodi/views/snippets')
blocks = set()
for path in snippet_dir.glob('s_facodi_*.xml'):
    root = ET.parse(path).getroot()
    for node in root.findall('template'):
        if node.get('id', '').startswith('s_facodi_'):
            blocks.add(node.get('id'))

expected = {
    's_facodi_hero',
    's_facodi_learning_journey',
    's_facodi_course_showcase',
    's_facodi_academic_areas',
    's_facodi_institutional',
    's_facodi_intro',
    's_facodi_features',
    's_facodi_community',
    's_facodi_ecosystem',
    's_facodi_roadmap',
    's_facodi_faq',
    's_facodi_course_cta',
    's_facodi_editorial_pathway',
    's_facodi_editorial_routes',
}
component_ids = {
    's_facodi_highlighter_heading',
    's_facodi_paper_card',
    's_facodi_sticky_note',
    's_facodi_folder_tabs',
    's_facodi_filter_pills',
    's_facodi_course_card',
    's_facodi_study_steps',
    's_facodi_cta_sheet',
    's_facodi_metadata_row',
    's_facodi_highlighter_callout',
    's_facodi_about_hero',
    's_facodi_project_story',
    's_facodi_principles_ledger',
    's_facodi_process_timeline',
    's_facodi_contribution_board',
    's_facodi_bulletin_hero',
    's_facodi_editorial_quote',
    's_facodi_contact_sheet',
    's_facodi_policy_document',
}
assert blocks == expected, (blocks, expected)

pages = ET.parse('theme_facodi/views/page_templates.xml').getroot()
compositions = [
    node for node in pages.findall('template')
    if node.get('id', '').startswith('new_page_template_sections_')
]
assert len(compositions) == 10
for page in compositions:
    for node in page.iter('t'):
        key = node.get('t-snippet-call')
        if key:
            assert key.startswith('theme_facodi.')
            assert key.split('.', 1)[1] in expected | component_ids
CHECK

echo "PASS: theme module contract"

# Contextual contribution/contact CTAs must preserve intent for facodi_learning
# while the native /contactus page remains available independently.
grep -Fq 'source=ecosystem_contact_cta&amp;section=ecosystem&amp;topic=partnership' theme_facodi/views/snippets/s_facodi_ecosystem.xml \
  || fail "ecosystem contact CTA must prefill partnership context"
grep -Fq 'source=institutional_contact_cta&amp;section=institutional&amp;topic=partnership' theme_facodi/views/snippets/s_facodi_institutional.xml \
  || fail "institutional contact CTA must prefill partnership context"
grep -Fq 'source=community_collaboration_cta&amp;section=community&amp;topic=collaboration' theme_facodi/views/snippets/s_facodi_community.xml \
  || fail "community contact CTA must prefill collaboration context"
grep -Fq 'source=faq_contribution_cta&amp;section=faq&amp;topic=collaboration' theme_facodi/views/snippets/s_facodi_faq.xml \
  || fail "FAQ contribution CTA must prefill collaboration context"

grep -Fq '.facodi-submission-type-switcher' theme_facodi/static/src/scss/enriched_surfaces.scss \
  || fail "contextual submission type switcher styling missing"

grep -Fq '[data-facodi-revision-request="1"]' theme_facodi/static/src/scss/enriched_surfaces.scss \
  || fail "requested-revision highlighter surface missing"
grep -Fq '.facodi-revision-resubmit' theme_facodi/static/src/scss/enriched_surfaces.scss \
  || fail "revision resubmit card styling missing"
grep -Fq '.facodi-contribution-journey__revision' theme_facodi/static/src/scss/enriched_surfaces.scss \
  || fail "revision journey styling missing"

# User-facing FACODI contact CTAs use the richer contextual intake; the native
# /contactus route remains available and is still covered independently.
grep -Fq 'href="/contact?source=faq_contact_cta&amp;section=faq&amp;topic=collaboration">Open full contact form' theme_facodi/views/snippets/s_facodi_faq.xml \
  || fail "FAQ full contact form must preserve FAQ context"
grep -Fq 'href="/contact?source=forum_postit_contact_cta&amp;section=community&amp;topic=collaboration" class="facodi-text-link">Continue the conversation' theme_facodi/views/snippets/components/s_facodi_forum_postit.xml \
  || fail "forum post-it contact must preserve community context"

grep -Fq '.facodi-captured-context' theme_facodi/static/src/scss/enriched_surfaces.scss \
  || fail "captured contribution context surface missing"
grep -Fq '.facodi-captured-context__grid' theme_facodi/static/src/scss/enriched_surfaces.scss \
  || fail "captured contribution context grid missing"

grep -Fq 'minmax(#{"min(100%, 12rem)"}, 1fr)' theme_facodi/static/src/scss/enriched_surfaces.scss \
  || fail "LibSass-safe captured context grid missing"

if grep -R -Fq '/submissions/new?type=contact' theme_facodi/views/snippets --include='*.xml'; then
  fail "theme snippets must use canonical /contact for contact intent"
fi
grep -R -Fq '/contact?source=' theme_facodi/views/snippets --include='*.xml' \
  || fail "theme snippets must preserve contextual contact source through canonical /contact"
