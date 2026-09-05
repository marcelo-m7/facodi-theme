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
done

# English is the canonical source language in QWeb. These phrases are also
# smoke anchors used by the runtime translation tests.
grep -Fq 'Learn together with the community' "$VIEWS_DIR/snippets/s_facodi_hero.xml" \
  || fail "hero source language must remain English"
grep -Fq 'Digital Community College. Open, collaborative and accessible higher education.' "$VIEWS_DIR/customizations.xml" \
  || fail "website shell source language must be English"

# Portuguese content must be supplied through pt.po instead of being embedded
# as an alternate QWeb branch or left as the source language.
if grep -R -nE 'Aprenda em comunidade|Seu próximo capítulo|Explorar cursos|Minha conta|Faculdade Comunitária Digital|Criado por' "$VIEWS_DIR" --include='*.xml'; then
  fail "Portuguese editorial copy must not remain hardcoded in source QWeb"
fi

# Keep language selection in Odoo's standard Website/i18n stack. The theme must
# not implement parallel language branches.
if grep -R -nE 't-if=.*(lang|language)|request\.(lang|language)|context.*lang.*==' "$VIEWS_DIR" --include='*.xml'; then
  fail "theme must not implement custom per-language QWeb branching"
fi

for catalogue in pt es fr; do
  grep -Fq 'msgid "Learn together with the community"' "$I18N_DIR/${catalogue}.po" \
    || fail "${catalogue}.po does not translate the hero language anchor"
  grep -Fq 'msgid "Digital Community College. Open, collaborative and accessible higher education."' "$I18N_DIR/${catalogue}.po" \
    || fail "${catalogue}.po does not translate the website shell language anchor"
done

echo "PASS: native Odoo i18n contract"
