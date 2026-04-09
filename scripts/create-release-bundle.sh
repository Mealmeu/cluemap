#!/bin/sh
set -e
BUNDLE_NAME="${1:-cluemap-release.zip}"
sh scripts/clean-artifacts.sh
mkdir -p release
BUNDLE_NAME="$BUNDLE_NAME" python - <<'PY'
import atexit
import fnmatch
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

root = Path('.').resolve()
release_root = root / 'release'
stage = Path(tempfile.mkdtemp(prefix='bundle-', dir=release_root))
atexit.register(lambda: shutil.rmtree(stage, ignore_errors=True))
include_roots = [
    'backend',
    'frontend',
    'infra',
    'runner',
    'scripts',
    '.env.example',
    '.gitignore',
    '.dockerignore',
    '.bundleignore',
    'docker-compose.yml',
]
ignore_file = root / '.bundleignore'
patterns = [line.strip() for line in ignore_file.read_text(encoding='utf-8').splitlines() if line.strip() and not line.strip().startswith('#')]

def ignored(relative: Path) -> bool:
    posix = relative.as_posix()
    for pattern in patterns:
        normalized = pattern.rstrip('/')
        if posix == normalized or posix.startswith(normalized + '/'):
            return True
        if fnmatch.fnmatch(posix, pattern) or any(fnmatch.fnmatch(part, pattern) for part in relative.parts):
            return True
        if pattern.endswith('/*') and posix.startswith(pattern[:-1]):
            return True
    return False

for item in include_roots:
    source = root / item
    if not source.exists():
        continue
    if source.is_file():
        relative = source.relative_to(root)
        if ignored(relative):
            continue
        target = stage / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        continue
    for path in source.rglob('*'):
        relative = path.relative_to(root)
        if ignored(relative):
            continue
        target = stage / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)

docs_dir = stage / 'docs'
docs_dir.mkdir(parents=True, exist_ok=True)
deploy_guide = root / 'DEPLOY_UBUNTU.md'
if deploy_guide.exists():
    shutil.copy2(deploy_guide, docs_dir / 'DEPLOY_UBUNTU.md')

bundle_name = os.environ['BUNDLE_NAME']
bundle_path = root / bundle_name
bundle_path.parent.mkdir(parents=True, exist_ok=True)
if bundle_path.exists():
    bundle_path.unlink()
with zipfile.ZipFile(bundle_path, 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in stage.rglob('*'):
        if path.is_file():
            archive.write(path, path.relative_to(stage).as_posix())
if not bundle_path.exists() or bundle_path.stat().st_size == 0:
    raise SystemExit('release bundle creation failed')
shutil.rmtree(stage, ignore_errors=True)
PY
