#!/bin/sh
set -e
umask 077
set -a
. ./.env
set +a
mkdir -p backups
STAMP="$(date +%Y%m%d-%H%M%S)"
TARGET="backups/${POSTGRES_DB}-${STAMP}.dump"
docker compose exec -T postgres pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc > "$TARGET"
printf '%s\n' "$TARGET"
