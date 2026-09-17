#!/usr/bin/env bash
# Ubuntu 24.04 Droplet: swap, UFW, Docker Engine + Compose plugin.
set -euo pipefail

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root"
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y ca-certificates curl gnupg git ufw

if [[ ! -f /swapfile ]]; then
  echo "==> Creating 2G swap"
  if ! fallocate -l 2G /swapfile 2>/dev/null; then
    dd if=/dev/zero of=/swapfile bs=1M count=2048 status=none
  fi
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  echo "==> Docker already installed"
else
  echo "==> Installing Docker"
  curl -fsSL https://get.docker.com | sh
fi

systemctl enable --now docker
docker compose version
mkdir -p /var/www /var/www/certbot
echo "==> Host ready"
