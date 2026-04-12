#!/usr/bin/env python3
"""
process_issue.py — Routes GitHub Issues to game actions.
Called by GitHub Actions on every new Issue.
"""

import json
import os
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from engine import load_state, save_state, found_faction, join_faction, attack, propose_alliance
from render import render_readme

try:
    from gh_stats import get_player_stats
except ImportError:
    def get_player_stats(username, token=None):
        return {}

def parse_title(title: str):
    t = title.strip()
    tu = t.upper()

    if tu.startswith("FOUND:"):
        name = t[6:].strip()
        return "found", {"name": name}

    if tu.startswith("JOIN "):
        slug = t[5:].strip().lower()
        return "join", {"slug": slug}

    if tu.startswith("ATTACK ") or tu.startswith("ATTACK+"):
        clean = t[7:].strip().replace("+", " ")
        parts = clean.split()
        if len(parts) >= 2:
            try:
                return "attack", {"row": int(parts[0]), "col": int(parts[1])}
            except ValueError:
                pass

    if tu.startswith("ALLY ") or tu.startswith("ALLIANCE "):
        parts = t.split()
        if len(parts) >= 3:
            return "alliance", {"from_slug": parts[1].lower(), "to_slug": parts[2].lower()}

    return "unknown", {}

def main():
    title   = os.environ.get("ISSUE_TITLE", "")
    body    = os.environ.get("ISSUE_BODY", "")
    author  = os.environ.get("ISSUE_AUTHOR", "")
    token   = os.environ.get("GITHUB_TOKEN", "")

    if not author:
        print("No author.")
        sys.exit(1)

    print(f"Issue from @{author}: '{title}'")

    action, params = parse_title(title)
    print(f"Action: {action} | Params: {params}")

    gh_data = get_player_stats(author, token)
    print(f"GitHub stats: {gh_data}")

    state = load_state()

    if action == "found":
        ok, msg = found_faction(state, author, params["name"], gh_data)
    elif action == "join":
        ok, msg = join_faction(state, author, params["slug"])
    elif action == "attack":
        ok, msg = attack(state, author, params["row"], params["col"], gh_data)
    elif action == "alliance":
        ok, msg = propose_alliance(state, params["from_slug"], params["to_slug"])
    else:
        ok, msg = False, f"Unrecognized command: `{title}`. Use the issue templates."

    print(msg)
    save_state(state)

    # Re-render README
    readme = render_readme(state)
    with open(Path(__file__).parent.parent / "README.md", "w") as f:
        f.write(readme)
    print("README updated.")

    # Write output for Actions comment
    output_file = os.environ.get("GITHUB_OUTPUT", "/dev/null")
    with open(output_file, "a") as fh:
        escaped = msg.replace("\n", "%0A").replace("\r", "")
        fh.write(f"result={escaped}\n")
        fh.write(f"success={'true' if ok else 'false'}\n")

if __name__ == "__main__":
    main()
