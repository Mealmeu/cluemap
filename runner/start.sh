#!/bin/sh
set -e
exec uvicorn app.main:app --host 0.0.0.0 --port 9000 --workers 1 --limit-concurrency 16 --timeout-keep-alive 5