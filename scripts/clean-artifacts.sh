#!/bin/sh
set -e
find . -type d \( -name '__pycache__' -o -name '.pytest_cache' -o -name '.mypy_cache' -o -name '.ruff_cache' -o -name '.vite' -o -name 'coverage' \) -prune -exec rm -rf {} +
find . -type f \( -name '*.pyc' -o -name '*.pyc.*' -o -name '*.pyo' -o -name '*.tsbuildinfo' -o -name '.DS_Store' -o -name 'Thumbs.db' -o -name '.coverage' -o -name '.coverage.*' -o -name '*.tmp' \) -delete
rm -rf frontend/node_modules frontend/dist release
find . -maxdepth 1 -type f \( -name 'cluemap-release*.zip' -o -name '*.log' -o -name 'npm-debug.log*' -o -name 'yarn-*.log*' -o -name 'pnpm-debug.log*' \) -delete
