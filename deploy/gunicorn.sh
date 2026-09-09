#!/usr/bin/env bash
# Gunicorn entry for DigitalOcean droplet
set -euo pipefail
cd "$(dirname "$0")/.."
# shellcheck disable=SC1091
source .venv/bin/activate
exec gunicorn config.wsgi:application \
  --bind 127.0.0.1:8000 \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout 60 \
  --access-logfile - \
  --error-logfile -
