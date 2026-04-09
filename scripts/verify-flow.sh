#!/bin/sh
set -e
BASE_URL="${1:-${CLUE_MAP_BASE_URL:-http://localhost}}"
export CLUE_MAP_BASE_URL="$BASE_URL"
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3가 필요합니다."
  exit 1
fi
python3 scripts/verify-flow.py
