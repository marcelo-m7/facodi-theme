#!/usr/bin/env bash
set -euo pipefail

fail() { echo "FAIL: $*" >&2; exit 1; }

SCSS="theme_facodi/static/src/scss/curriculum.scss"

for selector in   '.facodi-curriculum'   '.facodi-curriculum .card'   '.facodi-curriculum form'   '.facodi-curriculum-pathway'   '.facodi-curriculum-pathway__header'   '.facodi-curriculum-map__unit'   '.facodi-coverage-badge'   '.facodi-curriculum-table'   '.facodi-editorial-routes-list'   '.facodi-pathway-step'   '.facodi-roadmap-study-path'   '.facodi-unit-layout'   '.facodi-reference-rail'   '.facodi-module-detail'; do
  grep -Fq "$selector" "$SCSS" || fail "curriculum selector missing: $selector"
done

grep -Fq 'var(--facodi-shadow)' "$SCSS"   || fail "curriculum cards must use the shared shadow"
grep -Fq 'overflow-x: auto' "$SCSS"   || fail "wide curriculum tables must scroll internally"
grep -Fq '@media (max-width: 767.98px)' "$SCSS"   || fail "curriculum needs an explicit phone layout"
grep -Fq 'grid-template-columns: minmax(0, 1fr)' "$SCSS"   || fail "phone curriculum layouts must collapse to one shrinkable column"
grep -Fq 'grid-template-columns: minmax(0, 8fr) minmax(18rem, 4fr)' "$SCSS" \
  || fail "UC detail must use the approved 8/4 desktop composition"
grep -Fq 'overflow-wrap: anywhere' "$SCSS" \
  || fail "long D1 curriculum titles must wrap"

echo "PASS: Campus Paper curriculum presentation contract"
