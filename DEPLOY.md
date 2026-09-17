# Деплой Kontur+ на DigitalOcean Droplet

Канон PrometeyLabs: **Docker Compose + nginx + gunicorn + PostgreSQL**.
CI немає: `git push` ≠ live. На сервері потрібні `git pull` + `bash deploy/docker/deploy.sh`.

Дроплет уже є. Публічний IPv4: **68.183.210.146**.
Шлях коду: `/var/www/kontur` (не `/var/www/kontur/kontur`).
Репо: `https://github.com/prometeylabsanna-lgtm/kontur.git`.

Перший захід — **HTTP по IP** (`http://68.183.210.146/`). SSL — окремий крок після DNS.

Архітектура:

```
Internet :80/:443 → nginx (контейнер)
                      ↳ /static/  → volume staticfiles
                      ↳ /media/   → volume mediafiles
                      ↳ /         → gunicorn web:8000 → Django
                  PostgreSQL (контейнер db)
```

Gunicorn слухає лише HTTP. TLS завершує nginx. `SECURE_SSL_REDIRECT` у Django = `False` (інакше `/healthz/` → 301 → unhealthy).

---

## 0. Що має бути в репо перед деплоєм

- [ ] Зміни закомічені і запушені в `main`
- [ ] У tracked-файлах немає `.env` і паролів
- [ ] На Droplet ще немає ручних правок compose/nginx (або їх буде перезаписано `git pull`)

---

## 1. SSH з Mac

Окремий ключ на проєкт, без passphrase. Якщо ключ уже доданий до цього Droplet — використай його.

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_kontur_do -N "" -C "kontur-do"
chmod 600 ~/.ssh/id_kontur_do
cat ~/.ssh/id_kontur_do.pub
```

Публічний рядок — DigitalOcean → Droplet → Access → Add SSH key (або вже стоїть).

Дописати в `~/.ssh/config` (`>>`, не затирати інші `Host`):

```sshconfig
Host kontur
  HostName 68.183.210.146
  User root
  IdentityFile ~/.ssh/id_kontur_do
  IdentitiesOnly yes
  ServerAliveInterval 30
  ServerAliveCountMax 3
```

Перевірка:

```bash
ssh -G kontur | grep -E 'hostname|user|identityfile'
ssh kontur
```

`IdentitiesOnly yes` — не перебирати інші ключі (DO відсікає після кількох fail).

---

## 2. Підготовка хоста (на Droplet)

Ubuntu 24.04. Якщо RAM 1 GB — обов'язково swap. Firewall: 22, 80, 443.

```bash
ssh kontur
mkdir -p /var/www
cd /var/www
```

Якщо репо **приватне**, клон по HTTPS потребує GitHub PAT у полі Password (не пароль акаунта). Або deploy key.

```bash
git clone https://github.com/prometeylabsanna-lgtm/kontur.git kontur
cd /var/www/kontur
bash deploy/docker/install-docker.sh
```

Скрипт ставить Docker, 2G swap (якщо немає), UFW 22/80/443.

Перевірка шляху: `pwd` має бути `/var/www/kontur`, усередині є `manage.py`. Якщо вийшло `/var/www/kontur/kontur` — перенеси вміст на рівень вище.

Зупини host nginx/gunicorn, якщо вони вже слухають 80/443 (це зробить і `deploy.sh`):

```bash
systemctl stop nginx kontur gunicorn 2>/dev/null || true
systemctl disable nginx kontur gunicorn 2>/dev/null || true
```

**Один** спосіб деплою: Docker **або** bare-metal systemd. Не обидва на :80/:443.

---

## 3. `.env` на сервері (HTTP по IP)

```bash
cd /var/www/kontur
cp .env.docker.example .env
python3 - <<'PY'
import secrets, pathlib
p = pathlib.Path(".env")
text = p.read_text()
text = text.replace("SECRET_KEY=change-me-generate-with-python-secrets", "SECRET_KEY=" + secrets.token_urlsafe(50))
p.write_text(text)
print("SECRET_KEY written")
PY
nano .env
```

У `.env` вистав **реальний** пароль Postgres (лише літери/цифри, без `@ : / #`). Перевір:

| Ключ | Значення для HTTP-тесту |
|---|---|
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `68.183.210.146,127.0.0.1,localhost,web` |
| `CSRF_TRUSTED_ORIGINS` | `http://68.183.210.146` |
| `SESSION_COOKIE_SECURE` | `False` |
| `CSRF_COOKIE_SECURE` | `False` |
| `SECURE_SSL_REDIRECT` | `False` |
| `NGINX_CONF` | `docker.conf` |

Пастка: літерал `DROPLET_IP` у `ALLOWED_HOSTS` → **400** на сайт при живому `/healthz/`.

```bash
grep ALLOWED_HOSTS .env
# погано: ALLOWED_HOSTS=DROPLET_IP,127.0.0.1,...
# добре:  ALLOWED_HOSTS=68.183.210.146,127.0.0.1,localhost,web
```

`.env` не в git. Після `nano .env` контейнери треба `--force-recreate` (`deploy.sh` робить це).

---

## 4. Перший HTTP-деплой

```bash
cd /var/www/kontur
bash deploy/docker/deploy.sh
```

Скрипт: звільняє 80/443 на хості → `build` → `up -d --force-recreate` → чекає `/healthz/` → фінальний `up -d` → інвентаризація сервісів.

Перевірка **на сервері**:

```bash
curl -sI -H "Host: 68.183.210.146" http://127.0.0.1/ | head -5
curl -sf http://127.0.0.1/healthz/ && echo HTTP_OK
```

З браузера: `http://68.183.210.146/` → лендінг, `http://68.183.210.146/kontur-plus-cms/` → логін адмінки (не 400).

502 одразу після recreate — почекай entrypoint (`migrate` / `collectstatic`), не вбивай контейнер:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f web
```

---

## 5. Суперкористувач і контент

Entrypoint уже робить `migrate`, `collectstatic`, `seed_cms_content`.

Суперюзер — **після** будь-якого `flush`/`loaddata`, ніколи до:

```bash
cd /var/www/kontur
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec web \
  python manage.py createsuperuser
```

Адмінка: `http://68.183.210.146/kontur-plus-cms/`

Якщо треба залити локальну SQLite-вітрину — спочатку healthz OK, потім dump/load, потім createsuperuser.

---

## 6. Оновлення коду (після першого деплою)

На Mac:

```bash
git push origin main
```

На Droplet:

```bash
ssh kontur
cd /var/www/kontur
git pull origin main
bash deploy/docker/deploy.sh
```

`git pull` лише оновлює файли на диску. Код у контейнері змінюється лише після `build` (це є в `deploy.sh`).

Якщо `git pull` показує pager — натисни `q`.
Якщо abort через local changes:

```bash
git status
git restore docker-compose.prod.yml deploy/nginx/docker.conf
git pull origin main
bash deploy/docker/deploy.sh
```

Не патчити compose/nginx/settings руками на сервері.

---

## 7. SSL (лише коли є домен і DNS)

1. A-записи `@` і `www` → `68.183.210.146`. Дочекайся propagation.
2. У `deploy/nginx/docker.prod.conf` мають збігатися `server_name` і шляхи `/etc/letsencrypt/live/<домен>/`.
3. HTTP-сайт уже відкривається по домену.
4. Certbot на **хості**, не в контейнері:

```bash
apt install -y certbot
mkdir -p /var/www/certbot
# webroot, nginx лишається на :80
certbot certonly --webroot -w /var/www/certbot \
  -d kontur.plus -d www.kontur.plus \
  --agree-tos -m you@example.com
```

Якщо webroot не проходить — `docker compose ... stop nginx`, потім `certbot certonly --standalone`, далі знову `deploy.sh`.

5. У `.env`:

```env
NGINX_CONF=docker.prod.conf
ALLOWED_HOSTS=kontur.plus,www.kontur.plus,68.183.210.146,127.0.0.1,localhost,web
CSRF_TRUSTED_ORIGINS=https://kontur.plus,https://www.kontur.plus
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=31536000
```

`SECURE_SSL_REDIRECT` лишається `False` у Django: редірект HTTP→HTTPS робить nginx.

6. `bash deploy/docker/deploy.sh`

7. Перевірка:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec nginx ls /etc/letsencrypt/live/
curl -sI https://kontur.plus/healthz/ | head -5
```

Renew:

```bash
certbot renew
docker compose -f /var/www/kontur/docker-compose.yml -f /var/www/kontur/docker-compose.prod.yml exec nginx nginx -s reload
```

---

## 8. Google Places (опційно)

1. Google Cloud → Places API (New), ключ обмежити IP `68.183.210.146`.
2. У `.env`: `GOOGLE_PLACES_API_KEY`, опційно `GOOGLE_PLACE_ID`.
3. Recreate web: `bash deploy/docker/deploy.sh` або:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --force-recreate web
```

4. CMS → «Відгуки та кейси» → синхронізація. Cron:

```bash
cd /var/www/kontur && docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T web \
  python manage.py sync_google_reviews
```

---

## Корисні команди

```bash
COMPOSE="docker compose -f docker-compose.yml -f docker-compose.prod.yml"
$COMPOSE ps
$COMPOSE logs --tail=80 web nginx db
$COMPOSE exec web python manage.py check
$COMPOSE exec nginx nginx -t
```

Backup Postgres:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T db \
  pg_dump -U kontur kontur > /root/kontur-$(date +%F).sql
```

---

## Чеклист HTTP-тесту

- [ ] `ssh kontur` заходить, `IdentitiesOnly yes`
- [ ] Код у `/var/www/kontur`, є `manage.py`
- [ ] У `.env` немає рядка `DROPLET_IP`
- [ ] Cookies `SESSION_COOKIE_SECURE=False` / `CSRF_COOKIE_SECURE=False`
- [ ] `curl -H "Host: 68.183.210.146" http://127.0.0.1/` → 200, не 400
- [ ] `/healthz/` → `ok`
- [ ] `/kontur-plus-cms/` → 302 на login, не 400
- [ ] CSS є (`/static/`), медіа після рестарту на місці
- [ ] Після `git push` був `git pull` + `deploy.sh` на Droplet

---

## Типові помилки

| Симптом | Причина | Фікс |
|---|---|---|
| 400 на IP, healthz з localhost OK | літерал `DROPLET_IP` у `ALLOWED_HOSTS` | виправити `.env` → `deploy.sh` |
| Адмінка «не тримає» логін по HTTP | `SESSION_COOKIE_SECURE=True` | `False` в `.env` + recreate `web` |
| 502 ~1–2 хв після recreate | entrypoint ще migrate/collectstatic | `logs -f web`, не вбивати |
| Build killed / OOM | 1 GB без swap | `install-docker.sh` або 2 GB Droplet |
| Port 80 in use | host nginx + Docker | `systemctl stop nginx`; `deploy.sh` |
| Static 404 | volume / alias ≠ `/app/staticfiles/` | `collectstatic` у entrypoint |
| CSRF 403 після SSL | `CSRF_TRUSTED_ORIGINS` без `https://` | домени з https у `.env` |
| `web` unhealthy, логи 301 | `SECURE_SSL_REDIRECT=True` на Gunicorn | лишити `False` |
| Після push «на проді нічого» | немає CI | `git pull` + `deploy.sh` |
| `git pull` abort | ручний патч на сервері | `git restore` → pull |
| HTTPS не працює, HTTP OK | лишився `docker.conf` | `NGINX_CONF=docker.prod.conf` |

Старі файли `deploy/scripts/setup_droplet.sh` і `deploy/systemd/kontur.service` — leftover bare-metal. Для цього Droplet їх не запускати.
