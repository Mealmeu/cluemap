#!/bin/sh
set -e
DUMP_PATH="$1"
if [ -z "$DUMP_PATH" ] || [ ! -f "$DUMP_PATH" ]; then
  echo "복구할 dump 파일 경로를 전달해 주세요."
  exit 1
fi
set -a
. ./.env
set +a
docker compose exec -T postgres dropdb --if-exists -U "$POSTGRES_USER" "$POSTGRES_DB"
docker compose exec -T postgres createdb -U "$POSTGRES_USER" "$POSTGRES_DB"
cat "$DUMP_PATH" | docker compose exec -T postgres pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists