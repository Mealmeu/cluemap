#!/bin/sh
set -e
docker compose exec backend python download_local_model.py
