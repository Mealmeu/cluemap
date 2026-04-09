from __future__ import annotations

import fnmatch
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_patterns() -> list[str]:
    return [
        line.strip()
        for line in (ROOT / ".bundleignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def ignored(relative: str, patterns: list[str]) -> bool:
    posix = Path(relative).as_posix()
    parts = Path(relative).parts
    for pattern in patterns:
        normalized = pattern.rstrip("/")
        if posix == normalized or posix.startswith(normalized + "/"):
            return True
        if fnmatch.fnmatch(posix, pattern) or any(fnmatch.fnmatch(part, pattern) for part in parts):
            return True
        if pattern.endswith("/*") and posix.startswith(pattern[:-1]):
            return True
    return False


class BundleRuleTests(unittest.TestCase):
    def test_bundle_rules_exclude_sensitive_artifacts(self) -> None:
        bundleignore = (ROOT / ".bundleignore").read_text(encoding="utf-8")
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        required = [
            ".env",
            "frontend/node_modules",
            "frontend/dist",
            "backend/models",
            "*.pyc",
            "*.pyc.*",
            ".coverage.*",
            "*.zip",
            ".coverage",
        ]
        for item in required:
            self.assertIn(item, bundleignore)
            self.assertIn(item, gitignore)

    def test_bundle_ignore_patterns_match_real_targets(self) -> None:
        patterns = load_patterns()
        blocked = [
            ".env",
            "frontend/node_modules/pkg/index.js",
            "frontend/dist/assets/index.js",
            "backend/models/model.gguf",
            "infra/nginx/certs/fullchain.pem",
            "release/output.txt",
            "backups/db.dump",
            "foo.pyc",
            "foo.pyc.123",
            "foo.zip",
            ".coverage",
            ".coverage.123",
        ]
        allowed = [
            "backend/app/main.py",
            "frontend/src/pages/LoginPage.tsx",
            "runner/app/main.py",
            "scripts/deploy.sh",
            "docker-compose.yml",
            "docs/DEPLOY_UBUNTU.md",
        ]
        for item in blocked:
            self.assertTrue(ignored(item, patterns), item)
        for item in allowed:
            self.assertFalse(ignored(item, patterns), item)


if __name__ == "__main__":
    unittest.main()
