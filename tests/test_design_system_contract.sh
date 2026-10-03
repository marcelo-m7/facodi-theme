#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

DOC="docs/design-system.md"
TOKENS="theme_facodi/static/src/scss/campus_paper_tokens.scss"
PRIMARY="theme_facodi/static/src/scss/primary_variables.scss"
PRIMITIVES="theme_facodi/static/src/scss/paper_primitives.scss"
COMPONENTS="theme_facodi/static/src/scss/components.scss"
HERO="theme_facodi/views/snippets/s_facodi_hero.xml"

[[ -f "$DOC" ]] || fail "official FACODI design-system documentation is missing"

for section in   '# FACODI Design System — Tactile Academic Neobrutalism'   '## 3. Canonical color palette'   '## 7. Paper primitives'   '## 8. Canonical components'   '## 13. Existing-page convergence plan'   '## 14. Anti-patterns'   '## 16. Definition of done for a refactored page'; do
  grep -Fq "$section" "$DOC" || fail "design-system section missing: $section"
done

# Canonical core palette must remain aligned between Odoo primary variables and
# runtime Campus Paper CSS variables.
for pair in   '$facodi-ink: #142846;'   '$facodi-cyan: #37BED2;'   '$facodi-blue: #3979C8;'   '$facodi-mint: #A7E8BE;'   '$facodi-sun: #EFFF00;'   '$facodi-paper: #F9FAFB;'; do
  grep -Fq "$pair" "$PRIMARY" || fail "primary FACODI token drift: $pair"
done

for pair in   '--facodi-ink: #142846;'   '--facodi-cyan: #37BED2;'   '--facodi-blue: #3979C8;'   '--facodi-mint: #A7E8BE;'   '--facodi-sun: #EFFF00;'   '--facodi-paper: #F9FAFB;'   '--facodi-border: 2px solid var(--facodi-ink);'   '--facodi-shadow-card: 4px 4px 0 var(--facodi-ink);'   '--facodi-radius-card: 18px;'   '--facodi-radius-btn: 12px;'; do
  grep -Fq -- "$pair" "$TOKENS" || fail "runtime FACODI token drift: $pair"
done

for selector in   '.facodi-paper'   '.facodi-sheet'   '.facodi-note'   '.facodi-postit'   '.facodi-card'   '.facodi-badge'; do
  grep -Fq "$selector" "$PRIMITIVES" || fail "canonical primitive missing: $selector"
done

for selector in   '.facodi-button'   '.facodi-button-primary'   '.facodi-button-secondary'   '.facodi-text-link'; do
  grep -Fq "$selector" "$COMPONENTS" || fail "canonical component missing: $selector"
done

# The homepage hero is allowed to illustrate relationships but must never ship
# fictional live/featured learning records or fake counts as if they came from
# FACODI data.
for forbidden in   'FEATURED TODAY:'   'UNIT IN REVIEW:'   'How the Internet really works'   'Computational Thinking'   '12 resources · 4 open readings'   '>Real time<'; do
  if grep -Fq "$forbidden" "$HERO"; then
    fail "homepage hero contains fabricated data/status: $forbidden"
  fi
done

# Progressive enhancement must remain optional.
grep -Fq 'prefers-reduced-motion' "$PRIMITIVES"   || fail "paper primitives must preserve reduced-motion handling"

echo "PASS: FACODI official design-system contract"
