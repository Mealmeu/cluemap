#!/bin/sh
set -e
if [ "${ENABLE_TLS:-false}" = "true" ]; then
  sh scripts/prepare-ssl.sh
fi
docker compose up --build -d
