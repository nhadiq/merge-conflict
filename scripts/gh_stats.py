#!/usr/bin/env python3
"""gh_stats.py — Fetches real GitHub stats for power calculation."""

import json, sys, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

GH_API = "https://api.github.com"

def fetch(url, token=None):
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "realm.md-game")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except:
        return None

def get_player_stats(username, token=None):
    user = fetch(f"{GH_API}/users/{username}", token)
    if not user:
        return {}

    events = fetch(f"{GH_API}/users/{username}/events/public?per_page=30", token) or []
    today = datetime.now(timezone.utc).date()

    commits_today = prs_merged = prs_open = issues_closed = 0
    commit_days = set()

    for e in events:
        created = datetime.fromisoformat(e["created_at"].replace("Z","+00:00")).date()
        etype = e.get("type","")
        if etype == "PushEvent":
            commit_days.add(created)
            commits = len(e.get("payload",{}).get("commits",[]))
            if created == today: commits_today += commits
        elif etype == "PullRequestEvent":
            action = e.get("payload",{}).get("action")
            if action == "closed" and e["payload"].get("pull_request",{}).get("merged"):
                prs_merged += 1
            elif action == "opened":
                prs_open += 1
        elif etype == "IssuesEvent":
            if e.get("payload",{}).get("action") == "closed":
                issues_closed += 1

    streak = 0
    day = today
    while day in commit_days:
        streak += 1
        day -= timedelta(days=1)

    return {
        "username": username,
        "followers": user.get("followers", 0),
        "public_repos": user.get("public_repos", 0),
        "commits_today": commits_today,
        "prs_merged": prs_merged,
        "prs_open": prs_open,
        "issues_closed": issues_closed,
        "streak_days": streak,
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: gh_stats.py <username> [token]")
        sys.exit(1)
    stats = get_player_stats(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(json.dumps(stats, indent=2))
