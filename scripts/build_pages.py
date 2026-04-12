#!/usr/bin/env python3
"""
build_pages.py — GitHub Pages builder for merge-conflict.

Reads state.json and injects it into web/index.template.html,
producing web/index.html as a fully self-contained interactive
game page. The web/ folder is deployed to GitHub Pages via the
deploy_pages.yml workflow using actions/deploy-pages.

Usage:
    python scripts/build_pages.py [--repo-url https://github.com/owner/repo]

If --repo-url is not provided, the script attempts to read it from
the git remote 'origin', falling back to a placeholder.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT     = Path(__file__).parent.parent
TEMPLATE = ROOT / "web" / "index.template.html"
OUTPUT   = ROOT / "web" / "index.html"
STATE    = ROOT / "state.json"


def get_repo_url() -> str:
    """Try to detect the GitHub repo URL from git remote origin."""
    for arg in sys.argv[1:]:
        if arg.startswith("--repo-url="):
            return arg.split("=", 1)[1].rstrip("/")
        if arg == "--repo-url":
            idx = sys.argv.index("--repo-url")
            if idx + 1 < len(sys.argv):
                return sys.argv[idx + 1].rstrip("/")

    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True, cwd=ROOT, timeout=5
        )
        url = result.stdout.strip()
        if url.endswith(".git"):
            url = url[:-4]
        if url.startswith("git@github.com:"):
            url = "https://github.com/" + url[len("git@github.com:"):]
        return url
    except Exception:
        return "https://github.com/YOUR_USERNAME/merge-conflict"


def build() -> None:
    if not TEMPLATE.exists():
        print(f"ERROR: Template not found at {TEMPLATE}", file=sys.stderr)
        sys.exit(1)

    if not STATE.exists():
        print(f"ERROR: state.json not found at {STATE}", file=sys.stderr)
        sys.exit(1)

    with open(STATE, encoding="utf-8") as f:
        state = json.load(f)

    repo_url = get_repo_url()
    state_json = json.dumps(state, separators=(",", ":"), ensure_ascii=False)

    with open(TEMPLATE, encoding="utf-8") as f:
        html = f.read()

    html = html.replace("__STATE_JSON__", state_json)
    html = html.replace("'__REPO_URL__'", json.dumps(repo_url))

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = OUTPUT.stat().st_size / 1024
    print(f"Built {OUTPUT.relative_to(ROOT)} ({size_kb:.1f} KB) → {repo_url}")


if __name__ == "__main__":
    build()
