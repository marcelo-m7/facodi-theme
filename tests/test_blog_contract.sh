#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

XML="theme_facodi/views/website_blog.xml"
SCSS="theme_facodi/static/src/scss/website_blog.scss"

[[ -f "$XML" ]] || fail "D2 native Blog inheritance missing"
[[ -f "$SCSS" ]] || fail "D2 Blog stylesheet missing"

for inherit_id in \
  'website_blog.blog_post_short' \
  'website_blog.posts_loop' \
  'website_blog.blog_post_complete' \
  'website_blog.blog_post_content'; do
  grep -Fq "inherit_id=\"$inherit_id\"" "$XML" || fail "missing native Blog inheritance: $inherit_id"
done

for hook in \
  'facodi-blog-index' \
  'facodi-bulletin-card' \
  'facodi-blog-article' \
  'facodi-blog-prose'; do
  grep -Fq "$hook" "$XML" || fail "missing D2 Blog QWeb hook: $hook"
  grep -Fq ".$hook" "$SCSS" || fail "missing D2 Blog style: .$hook"
done

grep -Fq 't-call="theme_facodi.s_facodi_bulletin_hero"' "$XML" \
  || fail "Blog index must reuse the FACODI bulletin hero snippet"
grep -Fq '.facodi-bulletin-hero' "$SCSS" \
  || fail "missing D2 Blog bulletin hero style"

if grep -Eiq 'request\.env|\.search\(|\.browse\(|\.sudo\(' "$XML"; then
  fail "Blog presentation QWeb must not query ORM directly"
fi

if grep -Eiq '[0-9]+[[:space:]]+(posts|articles|readers|subscribers)|Author:[[:space:]]+[A-Z]' "$XML"; then
  fail "Blog presentation must not invent metadata or metrics"
fi

python3 - <<'PY'
from pathlib import Path
source = Path("theme_facodi/static/src/scss/website_blog.scss").read_text(encoding="utf-8")
generic = '.o_record_cover_container'
for block in source.split('}'):
    if generic in block and 'background-image:' in block and '!important' in block:
        raise SystemExit("FAIL: D2 Blog must not force generic cover backgrounds")
PY

echo "PASS: D2 native Blog contract"
