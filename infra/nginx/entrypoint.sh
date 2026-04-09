#!/bin/sh
set -e
SERVER_NAME="${NGINX_SERVER_NAME:-_}"
ENABLE_TLS="${ENABLE_TLS:-false}"
if [ "$ENABLE_TLS" = "true" ] && [ -f /etc/nginx/certs/fullchain.pem ] && [ -f /etc/nginx/certs/privkey.pem ]; then
  sed "s/\${SERVER_NAME}/$SERVER_NAME/g" /etc/nginx/templates/https.conf.template > /etc/nginx/conf.d/default.conf
else
  sed "s/\${SERVER_NAME}/$SERVER_NAME/g" /etc/nginx/templates/http.conf.template > /etc/nginx/conf.d/default.conf
fi
exec nginx -g 'daemon off;'
