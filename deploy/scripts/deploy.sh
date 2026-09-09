#!/usr/bin/env bash
# Redeploy on droplet from project root (/var/www/kontur)
set -euo pipefail
cd "$(dirname "$0")/../.."

# shellcheck disable=SC1091
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
sudo systemctl restart kontur
sudo systemctl reload nginx
echo "Deploy OK"
