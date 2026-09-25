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
grep -Fq 'Digital Community College. Open, collaborative and accessible higher education.' "$VIEWS_DIR/customizations.xml" \
  || fail "website shell source language must be English"
grep -Fq 'Published courses' "$VIEWS_DIR/snippets/s_facodi_course_showcase.xml" \
  || fail "course showcase source language must remain English"
grep -Fq 'Find your next field of study.' "$VIEWS_DIR/snippets/s_facodi_academic_areas.xml" \
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
  grep -Fq 'msgid "Digital Community College. Open, collaborative and accessible higher education."' "$I18N_DIR/${catalogue}.po" \
    || fail "${catalogue}.po does not translate the website shell language anchor"
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
  'Learn in public.'
  'Open higher education, one useful next step at a time.'
  'Explore free courses'
  'Where do you want to begin?'
  'From curiosity to the next click.'
  'Choose a question'
  'Study at your pace'
  'Follow the next useful thread'
  'A good discovery deserves company.'
  'We are still building. You can be part of it.'
  'Keep the useful thread going.'
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
