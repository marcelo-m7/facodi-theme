#!/usr/bin/env bash
set -euo pipefail
FILE="theme_facodi/views/http_error.xml"
grep -Fq 'inherit_id="http_routing.500"' "$FILE"
grep -Fq 'facodi-error-sheet' "$FILE"
grep -Fq 'href="/courses"' "$FILE"
grep -Fq 'http_routing.http_error_debug' "$FILE"
if grep -Fq 'website.layout' "$FILE"; then
  echo "500 page must not depend on website.layout" >&2
  exit 1
fi

if grep -Eq 'request\.|t-field=|request\.env' "$FILE"; then
  echo "500 page must stay self-contained when the request/database state is broken" >&2
  exit 1
fi

if grep -Fq 'inherit_id="website.500"' theme_facodi/views/customizations.xml; then
  echo "Odoo 19 does not expose website.500; error handling must stay on http_routing.500" >&2
  exit 1
fi
