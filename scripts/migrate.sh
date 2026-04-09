#!/bin/sh
set -e
docker compose exec -T backend alembic upgrade head
