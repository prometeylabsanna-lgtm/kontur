# Деплой Kontur+ на DigitalOcean Droplet

Короткий шлях: Ubuntu 24.04 → Nginx + Gunicorn + systemd. БД: SQLite (файл) або PostgreSQL.

## 1. Створити дроплет

- Image: **Ubuntu 24.04 LTS**
- Plan: від **1 GB RAM** (краще 2 GB)
- Networking: публічний IPv4
- SSH key свого акаунта

У DO: Domain → A-запис на IP дроплета (`@` і `www`).

## 2. Залити код

```bash
ssh root@YOUR_DROPLET_IP
mkdir -p /var/www/kontur
# з локальної машини:
rsync -avz --exclude .venv --exclude db.sqlite3 --exclude media --exclude .git \
  ./ root@YOUR_DROPLET_IP:/var/www/kontur/
```

Або `git clone` у `/var/www/kontur`.

## 3. Перший запуск

```bash
cd /var/www/kontur
chmod +x deploy/scripts/*.sh deploy/gunicorn.sh
sudo bash deploy/scripts/setup_droplet.sh your-domain.com
```

Скрипт поставить пакети, venv, migrate, collectstatic, systemd, nginx.

Перевір `/var/www/kontur/.env`:

- `DEBUG=False`
- `SECRET_KEY` (унікальний)
- `ALLOWED_HOSTS=your-domain.com,www.your-domain.com`
- `CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com`
- `GTM_ID` / `META_PIXEL_ID` за потреби
- `GOOGLE_PLACES_API_KEY` / `GOOGLE_PLACE_ID` для автосинхронізації відгуків

Суперкористувач:

```bash
cd /var/www/kontur && source .venv/bin/activate
python manage.py createsuperuser
```

## 4. HTTPS

```bash
certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 5. Оновлення коду

```bash
# з локальної машини після rsync/git pull на сервері:
ssh root@YOUR_DROPLET_IP 'cd /var/www/kontur && bash deploy/scripts/deploy.sh'
```

## PostgreSQL (опційно)

```bash
apt-get install -y postgresql
sudo -u postgres createuser kontur
sudo -u postgres createdb -O kontur kontur
sudo -u postgres psql -c "ALTER USER kontur PASSWORD 'STRONG';"
```

У `.env`:

```env
DATABASE_URL=postgres://kontur:STRONG@127.0.0.1:5432/kontur
```

Потім `migrate` і `systemctl restart kontur`.

## Корисні команди

```bash
systemctl status kontur
journalctl -u kontur -f
tail -f /var/log/kontur/error.log
nginx -t && systemctl reload nginx
```

### Google Places (відгуки)

1. У Google Cloud увімкніть **Places API (New)**, створіть API key, обмежте по IP сервера.
2. У `.env`: `GOOGLE_PLACES_API_KEY=...` (і опційно `GOOGLE_PLACE_ID=ChIJ...`).
3. В CMS → «Відгуки та кейси» вкажіть Place ID і натисніть «Синхронізувати з Google зараз».
4. Cron (раз на добу):

```bash
cd /var/www/kontur && source .venv/bin/activate && python manage.py sync_google_reviews
```

Адмінка: `https://your-domain.com/kontur-plus-cms/`
