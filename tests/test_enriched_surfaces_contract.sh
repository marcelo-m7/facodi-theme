#!/usr/bin/env bash
set -euo pipefail
fail(){ echo "FAIL: $*" >&2; exit 1; }
SCSS="theme_facodi/static/src/scss/enriched_surfaces.scss"
MANIFEST="theme_facodi/__manifest__.py"
[[ -f "$SCSS" ]] || fail "enriched surface stylesheet missing"
grep -Fq 'enriched_surfaces.scss' "$MANIFEST" || fail "enriched surfaces not loaded"
grep -Fq '"version": "19.0.10.6.0"' "$MANIFEST" || fail "enriched release version missing"
for selector in '.o_portal_my_home' '.facodi-contribution-dashboard' '[data-facodi-community-videos="1"]' '.facodi-empty-state' '.o_wforum_post_reply' '.o_wslides_course_card' '.facodi-learning-meta' '[data-facodi-user-dashboard="1"]' '.facodi-dashboard-action'; do
 grep -Fq "$selector" "$SCSS" || fail "missing enriched component: $selector"
done
grep -Fq 'prefers-reduced-motion: reduce' "$SCSS" || fail "reduced motion missing"
echo "PASS: enriched FACODI component contract"
