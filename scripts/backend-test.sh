#!/bin/sh
set -e
BASE_URL="${1:-${CLUE_MAP_BASE_URL:-http://localhost}}"
export CLUE_MAP_BASE_URL="$BASE_URL"
sh scripts/verify-flow.sh "$BASE_URL"
