#!/bin/sh
set -e
if [ "$LLM_PROVIDER" = "local" ]; then
  python download_local_model.py
fi
alembic upgrade head
if [ "$RUN_SEED_ON_START" = "true" ]; then
  python seed.py
fi
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips "${FORWARDED_ALLOW_IPS:-*}"
