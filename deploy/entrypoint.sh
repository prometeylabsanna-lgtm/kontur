#!/usr/bin/env bash
set -euo pipefail

echo "==> Waiting for PostgreSQL..."
python <<'PY'
import os
import sys
import time

url = os.environ.get("DATABASE_URL", "")
if not url:
    print("==> DATABASE_URL not set, skip DB wait")
    sys.exit(0)

try:
    import psycopg
except ImportError:
    print("==> psycopg missing, skip DB wait")
    sys.exit(0)

for attempt in range(30):
    try:
        with psycopg.connect(url) as conn:
            conn.execute("SELECT 1")
        print("==> DB ready")
        break
    except Exception as exc:
        print(f"  {attempt + 1}/30: {exc}")
        time.sleep(2)
else:
    print("FATAL: DB not ready")
    sys.exit(1)
PY

echo "==> Django check + migrate + collectstatic"
python manage.py check --deploy || true
python manage.py migrate --noinput
python manage.py compilemessages -l uk || true
python manage.py collectstatic --noinput --verbosity 0
python manage.py seed_cms_content || true

mkdir -p /app/staticfiles /app/media
_static_count=$(find /app/staticfiles -type f 2>/dev/null | wc -l | tr -d ' ')
echo "==> static files: ${_static_count}"
if [ "${_static_count:-0}" -lt 10 ]; then
  echo "WARN: staticfiles count low — check STATIC_ROOT and collectstatic"
fi

echo "==> Starting: $*"
exec "$@"
