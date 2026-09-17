#!/usr/bin/env bash
# Production deploy on Droplet. Run from anywhere:
#   bash /var/www/kontur/deploy/docker/deploy.sh
set -euo pipefail

cd "$(dirname "$0")/../.."
APP_DIR="$(pwd)"
COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.prod.yml)

if [[ ! -f "${APP_DIR}/.env" ]]; then
  echo "FATAL: ${APP_DIR}/.env is missing. Copy .env.docker.example first."
  exit 1
fi

if grep -q 'DROPLET_IP' "${APP_DIR}/.env"; then
  echo "FATAL: replace DROPLET_IP in .env with the real IPv4 (68.183.210.146)."
  exit 1
fi

free_host_ports() {
  systemctl stop nginx 2>/dev/null || true
  systemctl disable nginx 2>/dev/null || true
  systemctl stop kontur 2>/dev/null || true
  systemctl disable kontur 2>/dev/null || true
  systemctl stop gunicorn 2>/dev/null || true
  systemctl disable gunicorn 2>/dev/null || true
}

echo "==> Free host :80/:443 (bare-metal nginx/gunicorn)"
free_host_ports
mkdir -p /var/www/certbot

echo "==> Build images"
"${COMPOSE[@]}" build

echo "==> Start stack (first up may be incomplete during migrate)"
"${COMPOSE[@]}" up -d --force-recreate || true

echo "==> Wait for /healthz/"
ok=0
for i in $(seq 1 90); do
  if curl -sf http://127.0.0.1/healthz/ >/dev/null 2>&1; then
    echo "==> healthz OK (${i})"
    ok=1
    break
  fi
  if python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1/healthz/', timeout=5)" >/dev/null 2>&1; then
    echo "==> healthz OK (${i})"
    ok=1
    break
  fi
  sleep 2
done

echo "==> Final up -d (ensure nginx/web/db exist)"
"${COMPOSE[@]}" up -d

echo "==> Service inventory"
"${COMPOSE[@]}" ps

if [[ "${ok}" -ne 1 ]]; then
  echo "WARN: /healthz/ did not return 200. Logs:"
  "${COMPOSE[@]}" logs --tail=80 web nginx db
  exit 1
fi

echo "Deploy OK"
