#!/bin/sh
set -e
DOMAIN="$1"
EMAIL="$2"
if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
  echo "사용법: sh scripts/issue-certbot.sh example.com admin@example.com"
  exit 1
fi
sudo apt update
sudo DEBIAN_FRONTEND=noninteractive apt install -y certbot
if docker compose ps nginx >/dev/null 2>&1; then
  docker compose stop nginx || true
fi
sudo certbot certonly --standalone --preferred-challenges http --non-interactive --agree-tos --no-eff-email -m "$EMAIL" -d "$DOMAIN"
mkdir -p infra/nginx/certs
sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" infra/nginx/certs/fullchain.pem
sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" infra/nginx/certs/privkey.pem
sudo chown "$USER":"$USER" infra/nginx/certs/fullchain.pem infra/nginx/certs/privkey.pem
docker compose up -d nginx