#!/usr/bin/env sh
# Post-deploy smoke check for the live site.
#
# Confirms the deploy is internally consistent and won't hang on refresh:
#   1. the app shell (index.html) loads and is served no-cache,
#   2. the JS bundle index.html references resolves AS JavaScript (not the
#      HTML fallback — the stale-asset bug that hangs the SPA after a redeploy),
#   3. a missing asset returns a real 404 (not index.html),
#   4. the API is healthy.
#
# Usage: sh scripts/postdeploy-check.sh [BASE_URL]
# Exits non-zero on the first hard failure so it can gate a deploy.
set -eu

BASE_URL="${1:-https://laborator.algomate.ro}"
fail() { echo "POST-DEPLOY CHECK FAILED: $1" >&2; exit 1; }

echo "Checking $BASE_URL ..."

# 1) App shell loads, and should be revalidated on every request.
shell_headers=$(curl -fsS -D - -o /dev/null --max-time 15 "$BASE_URL/") \
  || fail "shell ($BASE_URL/) did not return 200"
echo "$shell_headers" | grep -iq 'cache-control:[[:space:]]*no-cache' \
  || echo "WARN: shell is missing 'Cache-Control: no-cache' — add it in nginx so redeploys are picked up."

# 2) The bundle index.html points at must resolve as JavaScript, not HTML.
html=$(curl -fsS --max-time 15 "$BASE_URL/") || fail "could not fetch index.html"
asset=$(printf '%s' "$html" | grep -oE '/assets/[A-Za-z0-9_.-]+\.js' | head -1 || true)
[ -n "$asset" ] || fail "no /assets/*.js reference found in index.html"
ctype=$(curl -fsS -o /dev/null -w '%{content_type}' --max-time 15 "$BASE_URL$asset") \
  || fail "referenced bundle $asset did not return 200"
case "$ctype" in
  application/javascript*|text/javascript*) : ;;
  *) fail "bundle $asset served as '$ctype' (expected JavaScript) — stale/mismatched build; the app will hang on refresh" ;;
esac

# 3) A missing asset must 404, not fall back to index.html.
miss=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 15 "$BASE_URL/assets/__missing__.js" || true)
[ "$miss" = "404" ] \
  || echo "WARN: missing asset returned $miss (expected 404) — a stale reference would be served HTML."

# 4) API health.
api=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 15 "$BASE_URL/api/v1/health/" || true)
[ "$api" = "200" ] || fail "API health returned $api (expected 200)"

echo "OK: shell + bundle ($asset) + API all healthy."
