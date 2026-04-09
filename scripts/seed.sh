#!/bin/sh
set -e
docker compose exec -T backend python seed.py
