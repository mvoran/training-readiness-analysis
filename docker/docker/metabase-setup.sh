#!/bin/sh
set -e

echo "→ Waiting for Metabase to expose /api/ready"
# ───── DEBUG ─────
# echo "DEBUG: MB_CONTAINER_URL resolved to ${MB_CONTAINER_URL}"
# ─────────────────
for i in $(seq 1 30); do
  STATUS=$(curl -s --max-time 2 "http://metabase:3000/api/health" || echo "")
  # DEBUG: show the exact curl command and its raw result
  echo "DEBUG: curl -s --max-time 2 \"http://metabase:3000/api/health\"  ⇒  ${STATUS}"
  if echo "$STATUS" | grep -q '"status":"ok"'; then
    echo "✔ Metabase is healthy."
    break
  fi
  if [ $i -eq 30 ]; then
    echo "❌ Metabase failed to become healthy after 60 attempts"
    exit 1
  fi
  echo "… waiting (attempt $i)…"
  sleep 5
done

# Additional wait to ensure Metabase is fully initialized
echo "→ Waiting additional time for Metabase to fully initialize..."
sleep 30

echo "→ Fetching setup token…"
TOKEN=$(curl -s "http://metabase:3000/api/session/properties" | \
        grep -o '"setup-token"[[:space:]]*:[[:space:]]*"[^"]*"' | \
        awk -F'"' '{print $4}')

if [ -z "$TOKEN" ]; then
  echo "‼  Could not retrieve setup token; aborting."
  exit 1
fi
echo "✔  Token = $TOKEN"

echo "→ Calling /api/setup with token…"
SETUP_PAYLOAD=$(cat <<EOF
{
  "token": "$TOKEN",
  "user": {
    "email": "${MB_SETUP_EMAIL}",
    "first_name": "${MB_SETUP_FIRST_NAME}",
    "last_name": "${MB_SETUP_LAST_NAME}",
    "password": "${MB_SETUP_PASSWORD}"
  },
  "prefs": {
    "site_name": "${MB_SITE_NAME}",
    "site_locale": "${MB_SITE_LOCALE}",
    "site_url": "${MB_SITE_URL}",
    "allow_tracking": false
  },
  "database": {
    "name": "${EXT_DB_NAME}",
    "engine": "postgres",
    "details": {
      "host": "${EXT_DB_HOST}",
      "port": ${EXT_DB_PORT},
      "dbname": "${EXT_DB_NAME}",
      "user": "${EXT_DB_USER}",
      "password": "${EXT_DB_PASS}",
      "ssl": false
    }
  }
}
EOF
)

echo "DEBUG PAYLOAD:"
echo "$SETUP_PAYLOAD"

RESPONSE=$(curl -s -H "Content-Type: application/json" \
  -d "$SETUP_PAYLOAD" \
  "http://metabase:3000/api/setup")

echo "→ /api/setup response:"
echo "$RESPONSE"

# If setup only returned a session token, register the external database and set site URL manually
SESSION_TOKEN=$(echo "$RESPONSE" | sed -n 's/.*"id":"\([^"]*\)".*/\1/p')
if [ -n "$SESSION_TOKEN" ] && ! echo "$RESPONSE" | grep -q '"db_configuration"'; then
  echo "→ Adding external database via /api/database…"
  ADDDB_PAYLOAD=$(cat <<EOF
  {
    "name": "${EXT_DB_NAME}",
    "engine": "postgres",
    "details": {
      "host": "${EXT_DB_HOST}",
      "port": ${EXT_DB_PORT},
      "dbname": "${EXT_DB_NAME}",
      "user": "${EXT_DB_USER}",
      "password": "${EXT_DB_PASS}",
      "ssl": false
    }
  }
EOF
  )
  DBRESP=$(curl -s -H "Content-Type: application/json" \
               -H "X-Metabase-Session: $SESSION_TOKEN" \
               -d "$ADDDB_PAYLOAD" \
               "http://metabase:3000/api/database")
  echo "→ /api/database response:"
  echo "$DBRESP"

  echo "→ Updating site_url via /api/setting/site-url…"
  SITEURL_PAYLOAD=$(printf '{"site_url":"%s"}' "${MB_SITE_URL}")
  SITEURL_RESP=$(curl -s -H "Content-Type: application/json" \
                    -H "X-Metabase-Session: $SESSION_TOKEN" \
                    -X PUT \
                    -d "$SITEURL_PAYLOAD" \
                    "http://metabase:3000/api/setting/site-url")
  echo "→ /api/setting/site-url response:"
  echo "$SITEURL_RESP"
fi

echo "metabase-setup finished."
exit 0