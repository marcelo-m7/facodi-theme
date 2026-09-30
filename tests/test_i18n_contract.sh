#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

I18N_DIR="theme_facodi/i18n"
VIEWS_DIR="theme_facodi/views"

[[ -d "$I18N_DIR" ]] || fail "theme_facodi must provide a native Odoo i18n directory"
[[ -f "$I18N_DIR/theme_facodi.pot" ]] || fail "canonical Odoo translation template is missing"

for locale in pt es fr; do
  [[ -f "$I18N_DIR/${locale}.po" ]] || fail "missing Odoo translation catalogue: ${locale}.po"
done

[[ ! -f "$I18N_DIR/en.po" ]] || fail "English is the source language and must not be duplicated as en.po"

grep -Fq '"Language: pt_PT\n"' "$I18N_DIR/pt.po" || fail "Portuguese catalogue must target pt_PT"
grep -Fq '"Language: es_ES\n"' "$I18N_DIR/es.po" || fail "Spanish catalogue must target es_ES"
grep -Fq '"Language: fr_FR\n"' "$I18N_DIR/fr.po" || fail "French catalogue must target fr_FR"

# Odoo design themes are loaded first as theme.ir.ui.view records. Translation
# references therefore target that model/field and are copied into website
# ir.ui.view records when the theme is selected.
for catalogue in theme_facodi.pot pt.po es.po fr.po; do
  grep -Fq 'model_terms:theme.ir.ui.view,arch:theme_facodi.' "$I18N_DIR/$catalogue" \
    || fail "$catalogue must target theme.ir.ui.view arch translations"
  if grep -Fq 'model_terms:ir.ui.view,arch_db:theme_facodi.' "$I18N_DIR/$catalogue"; then
    fail "$catalogue must not target copied website views directly"
  fi
  grep -Fq 'model_terms:theme.ir.ui.view,arch:theme_facodi.s_facodi_course_showcase' "$I18N_DIR/$catalogue" \
    || fail "$catalogue must include course-showcase translations"
  grep -Fq 'model_terms:theme.ir.ui.view,arch:theme_facodi.s_facodi_academic_areas' "$I18N_DIR/$catalogue" \
    || fail "$catalogue must include academic-area translations"
  grep -Fq 'model_terms:theme.ir.ui.view,arch:theme_facodi.s_facodi_ecosystem' "$I18N_DIR/$catalogue" \
    || fail "$catalogue must include ecosystem translations"
done

# English is the canonical source language in QWeb. These phrases are also
# smoke anchors used by the runtime translation tests.
grep -Fq 'An open digital campus' "$VIEWS_DIR/snippets/s_facodi_hero.xml" \
  || fail "hero source language must remain English"
grep -Fq 'Open learning resources, curricular context and community contributions — organised to help people study, discover and share knowledge.' "$VIEWS_DIR/customizations.xml" \
  || fail "website shell source language must be English"
grep -Fq 'Start somewhere useful.' "$VIEWS_DIR/snippets/s_facodi_course_showcase.xml" \
  || fail "course showcase source language must remain English"
grep -Fq 'Move across fields without losing the thread.' "$VIEWS_DIR/snippets/s_facodi_academic_areas.xml" \
  || fail "academic areas source language must remain English"
grep -Fq 'A learning ecosystem designed to stay open.' "$VIEWS_DIR/snippets/s_facodi_ecosystem.xml" \
  || fail "ecosystem source language must remain English"

# Portuguese content must be supplied through pt.po instead of being embedded
# as an alternate QWeb branch or left as the source language.
if grep -R -nE 'Aprenda em comunidade|Seu próximo capítulo|Explorar cursos|Minha conta|Faculdade Comunitária Digital|Criado por|Cursos publicados|Área de estudo|Rede universitária' "$VIEWS_DIR" --include='*.xml'; then
  fail "Portuguese editorial copy must not remain hardcoded in source QWeb"
fi

# Keep language selection in Odoo's standard Website/i18n stack. The theme must
# not implement parallel language branches.
if grep -R -nE 't-if=.*(lang|language)|request\.(lang|language)|context.*lang.*==' "$VIEWS_DIR" --include='*.xml'; then
  fail "theme must not implement custom per-language QWeb branching"
fi

FOUNDATION_MSGIDS=(
  'Published courses'
  'Explore the available courses'
  'Find your next field of study.'
  'Computing & Technology'
  'Mathematics & Data'
  'Business & Society'
  'Languages & Culture'
  'A learning ecosystem designed to stay open.'
  'Open resources'
  'Community learning'
  'University network'
  'Contribute to FACODI'
)

for catalogue in pt es fr; do
  grep -Fq 'msgid "Knowledge is everywhere. Find your next step."' "$I18N_DIR/${catalogue}.po" \
    || fail "${catalogue}.po does not translate the hero language anchor"
  grep -Fq 'msgid "Open learning resources, curricular context and community contributions — organised to help people study, discover and share knowledge."' "$I18N_DIR/${catalogue}.po" \
    || fail "${catalogue}.po does not translate the website shell language anchor"
  for footer_msgid in 'Policies' 'Accessibility' 'Cookie Policy'; do
    grep -Fq "msgid \"${footer_msgid}\"" "$I18N_DIR/${catalogue}.po" \
      || fail "${catalogue}.po does not translate footer label: ${footer_msgid}"
  done
  for msgid in "${FOUNDATION_MSGIDS[@]}"; do
    grep -Fq "msgid \"${msgid}\"" "$I18N_DIR/${catalogue}.po" \
      || fail "${catalogue}.po does not translate Foundation v2 string: ${msgid}"
  done
done

for msgid in "${FOUNDATION_MSGIDS[@]}"; do
  grep -Fq "msgid \"${msgid}\"" "$I18N_DIR/theme_facodi.pot" \
    || fail "theme_facodi.pot is missing Foundation v2 string: ${msgid}"
done

for catalogue in theme_facodi.pot pt.po es.po fr.po; do
  for ref in \
    'theme_facodi.s_facodi_community' \
    'theme_facodi.s_facodi_course_cta' \
    'theme_facodi.s_facodi_faq'; do
    grep -B8 -F 'msgid "I want to contribute"' "$I18N_DIR/$catalogue" \
      | grep -Fq "model_terms:theme.ir.ui.view,arch:$ref" \
      || fail "$catalogue must bind 'I want to contribute' to $ref"
  done
  for ref in \
    'theme_facodi.s_facodi_institutional' \
    'theme_facodi.s_facodi_ecosystem' \
    'theme_facodi.s_facodi_community'; do
    grep -B8 -F 'msgid "Contact FACODI"' "$I18N_DIR/$catalogue" \
      | grep -Fq "model_terms:theme.ir.ui.view,arch:$ref" \
      || fail "$catalogue must bind 'Contact FACODI' to $ref"
  done
done


CAMPUS_PAPER_MSGIDS=(
  'Knowledge is everywhere.'
  'Find your next step.'
  'Open learning becomes easier to navigate when useful resources connect.'
  'Explore courses'
  'See how FACODI works'
  'Explore learning in the way that makes sense to you.'
  'From a question to the next useful link.'
  'Choose a question'
  'Study at your pace'
  'Follow the useful thread'
  'Leave the trail clearer'
  'A useful discovery deserves company.'
  'Still building. You can improve the trail.'
  'Community-built. Academically aware. Still very much open.'
  'Still building. You can help shape what comes next.'
)

for catalogue in pt es fr; do
  for msgid in "${CAMPUS_PAPER_MSGIDS[@]}"; do
    grep -Fq "msgid \"${msgid}\"" "$I18N_DIR/${catalogue}.po" \
      || fail "${catalogue}.po is missing Campus Paper string: ${msgid}"
  done
done
for msgid in "${CAMPUS_PAPER_MSGIDS[@]}"; do
  grep -Fq "msgid \"${msgid}\"" "$I18N_DIR/theme_facodi.pot" \
    || fail "theme_facodi.pot is missing Campus Paper string: ${msgid}"
done


ABOUT_PAGE_MSGIDS=(
  'Where this sits'
  'FACODI is a community-learning project connected to the University of Algarve and the SEA-EU ecosystem. Official curricular references provide context; the community layer helps people discover, discuss and improve public learning resources.'
  'Read the project file'
  'Build something with FACODI'
  'Keep a few tabs open.'
  'FACODI editorial destinations'
  'Find the next useful rabbit hole'
  'Browse published courses and follow the thread into learning resources.'
  'Bring the messy question'
  'Ask, compare notes and leave a useful answer for the next learner.'
  'Found a gap? Drop it here.'
  'Share a resource, a correction or a collaboration idea with enough context to be useful.'
)

for catalogue in theme_facodi.pot pt.po es.po fr.po; do
  for msgid in "${ABOUT_PAGE_MSGIDS[@]}"; do
    grep -Fq "msgid \"${msgid}\"" "$I18N_DIR/$catalogue" \
      || fail "$catalogue is missing About page string: $msgid"
  done
done

for view in \
  theme_facodi/views/header.xml \
  theme_facodi/views/customizations.xml \
  theme_facodi/views/snippets/s_facodi_intro.xml \
  theme_facodi/views/snippets/s_facodi_editorial_routes.xml \
  theme_facodi/views/snippets/s_facodi_editorial_pathway.xml; do
  [[ -f "$view" ]] || fail "missing translated global/editorial view: $view"
done

echo "PASS: native Odoo i18n contract"


python3 - <<'PY'
from pathlib import Path

files = [
    Path("theme_facodi/i18n/theme_facodi.pot"),
    Path("theme_facodi/i18n/pt.po"),
    Path("theme_facodi/i18n/es.po"),
    Path("theme_facodi/i18n/fr.po"),
]
messages = ["Learning catalogue", "Courses", "Roadmaps", "Curricular Units"]
occurrence = "#: model_terms:theme.ir.ui.view,arch:theme_facodi.facodi_courses_home"

for path in files:
    content = path.read_text(encoding="utf-8")
    for message in messages:
        marker = f'msgid "{message}"'
        pos = content.find(marker)
        if pos < 0:
            raise SystemExit(f"FAIL: {path} missing D1 msgid {message}")
        start = content.rfind("\n\n", 0, pos) + 2
        end = content.find("\n\n", pos)
        if end < 0:
            end = len(content)
        block = content[start:end]
        if occurrence not in block:
            raise SystemExit(
                f"FAIL: {path} does not register {message!r} for facodi_courses_home"
            )
PY


python3 - <<'PY'
from pathlib import Path

D2_EDITORIAL_OCCURRENCES = {
    "A digital campus built from the good stuff already out there.": ["theme_facodi.s_facodi_about_hero"],
    "Open by default": ["theme_facodi.s_facodi_about_hero"],
    "Context, not claims": ["theme_facodi.s_facodi_about_hero"],
    "Built in public": ["theme_facodi.s_facodi_about_hero"],
    "Project dossier // why this exists": ["theme_facodi.s_facodi_project_story"],
    "Too many good tabs. Not enough map.": ["theme_facodi.s_facodi_project_story"],
    "FACODI started from a very ordinary study habit: finding brilliant public lessons, videos and documents across the web, then losing the thread between them.": ["theme_facodi.s_facodi_project_story"],
    "FACODI organises those finds around courses, curricular references and learning paths, so the useful stuff feels less like a tab graveyard and more like a campus.": ["theme_facodi.s_facodi_project_story"],
    "Open the campus map": ["theme_facodi.s_facodi_project_story"],
    "Working note": ["theme_facodi.s_facodi_project_story"],
    "The point is not to replace universities or invent equivalence. It is to make open learning easier to navigate, discuss and improve.": ["theme_facodi.s_facodi_project_story"],
    "Open beats locked": ["theme_facodi.s_facodi_principles_ledger"],
    "Start with public learning resources people can actually open, share and revisit without a paywall getting in the way.": ["theme_facodi.s_facodi_principles_ledger"],
    "Context beats link dumps": ["theme_facodi.s_facodi_principles_ledger"],
    "Connect useful resources to a course, curricular unit or learning question instead of dropping isolated links into a pile.": ["theme_facodi.s_facodi_principles_ledger"],
    "Review beats guesswork": ["theme_facodi.s_facodi_principles_ledger"],
    "Keep community contribution separate from publication, and make the editorial boundary visible when something is still under review.": ["theme_facodi.s_facodi_principles_ledger"],
    "Pick a route": ["theme_facodi.s_facodi_process_timeline"],
    "Start with a course, Roadmap, curricular unit or one very concrete question.": ["theme_facodi.s_facodi_process_timeline"],
    "Open the good tabs": ["theme_facodi.s_facodi_process_timeline"],
    "Use public resources and follow only the context that helps you move forwards.": ["theme_facodi.s_facodi_process_timeline"],
    "Connect the dots": ["theme_facodi.s_facodi_process_timeline"],
    "Relate useful material to the learning path so it becomes more than one clever link in isolation.": ["theme_facodi.s_facodi_process_timeline"],
    "Send something back": ["theme_facodi.s_facodi_process_timeline"],
    "Found a useful public resource or a gap worth fixing? Put it on the review desk for the community.": ["theme_facodi.s_facodi_process_timeline"],
    "Resource": ["theme_facodi.s_facodi_contribution_board"],
    "Suggest a public learning resource": ["theme_facodi.s_facodi_contribution_board"],
    "Share a useful course, video, playlist, article, or other public resource for review.": ["theme_facodi.s_facodi_contribution_board"],
    "Suggest a resource": ["theme_facodi.s_facodi_contribution_board", "theme_facodi.s_facodi_contact_sheet"],
    "Context": ["theme_facodi.s_facodi_contribution_board"],
    "Improve context or translation": ["theme_facodi.s_facodi_contribution_board"],
    "Help make descriptions, routes, and learning references clearer for more people.": ["theme_facodi.s_facodi_contribution_board"],
    "Contact FACODI": ["theme_facodi.s_facodi_contribution_board"],
    "Collaboration": ["theme_facodi.s_facodi_contribution_board"],
    "Build something together": ["theme_facodi.s_facodi_contribution_board"],
    "Propose a collaboration around open education, public resources, or community learning.": ["theme_facodi.s_facodi_contribution_board"],
    "Start a conversation": ["theme_facodi.s_facodi_contribution_board"],
    "Campus bulletin": ["theme_facodi.s_facodi_bulletin_hero"],
    "News, project notes, and community stories.": ["theme_facodi.s_facodi_bulletin_hero"],
    "Follow what FACODI is building, learning, testing, and sharing in public.": ["theme_facodi.s_facodi_bulletin_hero"],
    "Open learning becomes more useful when people can see the path, the source, and the next step.": ["theme_facodi.s_facodi_editorial_quote"],
    "FACODI editorial note": ["theme_facodi.s_facodi_editorial_quote"],
    "Write to the campus": ["theme_facodi.s_facodi_contact_sheet"],
    "Choose the shortest path to the right conversation.": ["theme_facodi.s_facodi_contact_sheet"],
    "Use Contact for collaboration, project questions, or general enquiries. If you are suggesting a learning resource, the guided contribution route keeps the review context together.": ["theme_facodi.s_facodi_contact_sheet"],
    "Contact form area": ["theme_facodi.s_facodi_contact_sheet"],
    "Keep the native Odoo form here.": ["theme_facodi.s_facodi_contact_sheet"],
    "This editable column is designed to frame the Website contact form without replacing its submission behaviour.": ["theme_facodi.s_facodi_contact_sheet"],
    "Policy document": ["theme_facodi.s_facodi_policy_document", "theme_facodi.snippets"],
    "Document title": ["theme_facodi.s_facodi_policy_document"],
    "Use this component as a readable shell around policy text maintained by the Website editor.": ["theme_facodi.s_facodi_policy_document"],
    "Document sections": ["theme_facodi.s_facodi_policy_document"],
    "Section": ["theme_facodi.s_facodi_policy_document"],
    "Section heading": ["theme_facodi.s_facodi_policy_document"],
    "Keep the approved policy wording here. The theme provides presentation and reading structure only.": ["theme_facodi.s_facodi_policy_document"],
    "Project story": ["theme_facodi.snippets"],
    "Principles ledger": ["theme_facodi.snippets"],
    "Process timeline": ["theme_facodi.snippets"],
    "Contribution board": ["theme_facodi.snippets"],
    "Bulletin hero": ["theme_facodi.snippets"],
    "Editorial quote": ["theme_facodi.snippets"],
    "Contact sheet": ["theme_facodi.snippets"],
}

files = [
    Path("theme_facodi/i18n/theme_facodi.pot"),
    Path("theme_facodi/i18n/pt.po"),
    Path("theme_facodi/i18n/es.po"),
    Path("theme_facodi/i18n/fr.po"),
]

for path in files:
    content = path.read_text(encoding="utf-8")
    for message, refs in D2_EDITORIAL_OCCURRENCES.items():
        marker = f'msgid "{message}"'
        pos = content.find(marker)
        if pos < 0:
            raise SystemExit(f"FAIL: {path} missing D2 msgid {message!r}")
        start = content.rfind("\n\n", 0, pos) + 2
        end = content.find("\n\n", pos)
        if end < 0:
            end = len(content)
        block = content[start:end]
        for ref in refs:
            occurrence = f"model_terms:theme.ir.ui.view,arch:{ref}"
            if occurrence not in block:
                raise SystemExit(
                    f"FAIL: {path} does not bind D2 msgid {message!r} to {ref}"
                )
PY

REUSABLE_BLOCK_MSGIDS=(
  'Open learning note'
  'Turn a useful idea into a'
  'visible next step'
  'Use this heading to introduce a section, learning milestone, or community contribution.'
  'Open module'
  'Build a compact learning card'
  'Summarize a topic, assignment, resource collection, or community activity in a tactile paper surface.'
  'Explore courses'
  'Study note'
  'Write down the question you want to answer next.'
  'Short reminders work best when they stay specific, useful, and easy to revisit.'
  'Learning sections'
  'Courses'
  'Roadmaps'
  'Curricular Units'
  'Contribute'
  'Topic labels'
  'All topics'
  'Open learning'
  'Technology'
  'Community'
  'Study notes'
  'Open course'
  '4 modules'
  'Open access'
  'Course title with a'
  'highlighted idea'
  'Use this editable card when the content is editorial rather than connected to a live eLearning record.'
  'Community learning'
  'View course'
  'Choose a question'
  'Start from something concrete you want to understand or build.'
  'Follow the thread'
  'Connect courses, curricular units, and public resources around that question.'
  'Share what helped'
  'Contribute useful resources so the next learner starts with better context.'
  'Community notebook // open page'
  'Found a gem?'
  'Put the good tab on the shared desk.'
  'Send a public resource with enough context to make it useful. FACODI keeps contribution separate from publication, so suggestions can be reviewed before they become part of the learning map.'
  'Drop a resource'
  'Learning metadata'
  'Core topic'
  'Margin note'
  'Keep the important part visible.'
  'Use this callout for a prerequisite, study hint, deadline, review warning, or short editorial note.'
)

REUSABLE_BUILDER_MSGIDS=(
  'Highlighter heading'
  'Paper card'
  'Sticky note'
  'Folder tabs'
  'Filter pills'
  'Static course card'
  'Study steps'
  'CTA sheet'
  'Metadata row'
  'Highlighter callout'
)

for catalogue in pt es fr; do
  for msgid in "${REUSABLE_BLOCK_MSGIDS[@]}"; do
    grep -Fq "msgid \"${msgid}\"" "$I18N_DIR/${catalogue}.po" \
      || fail "${catalogue}.po is missing reusable-block string: ${msgid}"
  done
done
for msgid in "${REUSABLE_BLOCK_MSGIDS[@]}"; do
  grep -Fq "msgid \"${msgid}\"" "$I18N_DIR/theme_facodi.pot" \
    || fail "theme_facodi.pot is missing reusable-block string: ${msgid}"
done

for catalogue in theme_facodi.pot pt.po es.po fr.po; do
  for ref in \
    'theme_facodi.s_facodi_highlighter_heading' \
    'theme_facodi.s_facodi_paper_card' \
    'theme_facodi.s_facodi_sticky_note' \
    'theme_facodi.s_facodi_folder_tabs' \
    'theme_facodi.s_facodi_filter_pills' \
    'theme_facodi.s_facodi_course_card' \
    'theme_facodi.s_facodi_study_steps' \
    'theme_facodi.s_facodi_cta_sheet' \
    'theme_facodi.s_facodi_metadata_row' \
    'theme_facodi.s_facodi_highlighter_callout'; do
    grep -Fq "model_terms:theme.ir.ui.view,arch:${ref}" "$I18N_DIR/$catalogue" \
      || fail "$catalogue must register translations for $ref"
  done
done


ERROR_PAGE_MSGIDS=(
  'FACODI // OPEN CAMPUS'
  'Error navigation'
  '← Back'
  'server detour'
  'This page hit a'
  'rough patch.'
  'FACODI could not finish this request right now. Return to the open campus, browse the learning catalogue, or try the page again in a moment.'
  'Back to FACODI'
  'Explore courses'
  'If this keeps happening, use the contact page and tell us what you were trying to open.'
)

for catalogue in pt es fr; do
  for msgid in "${ERROR_PAGE_MSGIDS[@]}"; do
    grep -Fq "msgid \"${msgid}\"" "$I18N_DIR/${catalogue}.po" \
      || fail "${catalogue}.po is missing 500-page string: ${msgid}"
  done
done
for msgid in "${ERROR_PAGE_MSGIDS[@]}"; do
  grep -Fq "msgid \"${msgid}\"" "$I18N_DIR/theme_facodi.pot" \
    || fail "theme_facodi.pot is missing 500-page string: ${msgid}"
done
