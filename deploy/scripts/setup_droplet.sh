#!/usr/bin/env bash
# First-time setup on Ubuntu 22.04/24.04 DigitalOcean droplet (run as root)
set -euo pipefail

APP_DIR=/var/www/kontur
APP_USER=www-data
DOMAIN="${1:-}"

if [[ -z "$DOMAIN" ]]; then
  echo "Usage: sudo bash deploy/scripts/setup_droplet.sh your-domain.com"
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y python3 python3-venv python3-pip nginx git curl certbot python3-certbot-nginx

mkdir -p "$APP_DIR" /var/log/kontur
chown -R "$APP_USER:$APP_USER" "$APP_DIR" /var/log/kontur

if [[ ! -d "$APP_DIR/.git" && ! -f "$APP_DIR/manage.py" ]]; then
  echo "Скопіюй проєкт у $APP_DIR (git clone або rsync), потім запусти знову."
  exit 1
fi

cd "$APP_DIR"
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [[ ! -f .env ]]; then
  cp .env.example .env
  SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
  sed -i "s/^SECRET_KEY=.*/SECRET_KEY=$SECRET/" .env
  sed -i "s/^DEBUG=.*/DEBUG=False/" .env
  sed -i "s/^ALLOWED_HOSTS=.*/ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN/" .env
  sed -i "s|^CSRF_TRUSTED_ORIGINS=.*|CSRF_TRUSTED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN|" .env
  echo "Створено .env — перевір значення перед продовженням."
fi

mkdir -p media data
chown -R "$APP_USER:$APP_USER" media data

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py seed_cms_content || true
python manage.py seed_hero_slides || true

install -m 644 deploy/systemd/kontur.service /etc/systemd/system/kontur.service
sed "s/YOUR_DOMAIN/$DOMAIN/g" deploy/nginx/kontur.conf > /etc/nginx/sites-available/kontur
ln -sfn /etc/nginx/sites-available/kontur /etc/nginx/sites-enabled/kontur
rm -f /etc/nginx/sites-enabled/default

systemctl daemon-reload
systemctl enable --now kontur
nginx -t
systemctl reload nginx

echo "HTTP готовий. SSL: certbot --nginx -d $DOMAIN -d www.$DOMAIN"
echo "Адмінка: https://$DOMAIN/kontur-plus-cms/"
