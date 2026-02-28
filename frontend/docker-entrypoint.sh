#!/bin/sh
set -eu

# Generate a small runtime config file that the SPA can read.
# This lets docker-compose `environment:` affect the app without rebuilding.

: "${VITE_API_BASE_URL:=}"

cat >/usr/share/nginx/html/env.js <<'EOF'
// This file is generated at container start.
// It is safe to expose only non-secret, client-side configuration here.
window.__ENV__ = window.__ENV__ || {};
EOF

# Append values with basic JS string escaping (quotes + backslashes).
escape_js_string() {
  # Reads stdin, writes escaped string to stdout
  sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'
}

if [ -n "${VITE_API_BASE_URL}" ]; then
  printf 'window.__ENV__.VITE_API_BASE_URL = "%s";\n' "$(printf %s "${VITE_API_BASE_URL}" | escape_js_string)" >>/usr/share/nginx/html/env.js
fi

# Ensure env.js is not cached too aggressively by clients/proxies.
# (Caching headers are also set in nginx.conf.)

exec "$@"

