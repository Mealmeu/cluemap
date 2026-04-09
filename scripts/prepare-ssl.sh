#!/bin/sh
set -e
CERT_DIR="${1:-infra/nginx/certs}"
COMMON_NAME="${2:-localhost}"
mkdir -p "$CERT_DIR"
if [ -f "$CERT_DIR/fullchain.pem" ] && [ -f "$CERT_DIR/privkey.pem" ]; then
  exit 0
fi
openssl req -x509 -nodes -newkey rsa:2048 -days 365 \
  -keyout "$CERT_DIR/privkey.pem" \
  -out "$CERT_DIR/fullchain.pem" \
  -subj "/CN=$COMMON_NAME" \
  -addext "subjectAltName=DNS:$COMMON_NAME,IP:127.0.0.1"