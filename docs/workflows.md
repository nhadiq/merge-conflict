# GitHub Actions Workflows

---

## `process_move.yml` — Fires on Every New Issue

```yaml
on:
  issues:
    types: [opened]

concurrency:
  group: realm-update
  cancel-in-progress: false     # Queue moves, don't drop them
```

**Steps:**
1. `checkout` with write token
2. `setup-python 3.12`
3. `process_issue.py` — main game logic
4. `build_pages.py` — rebuild `web/index.html` from new state
5. `git-auto-commit-action` — commits `README.md`, `state.json`, and `web/index.html`
6. `actions/github-script` — comments result on Issue, closes Issue, adds `processed` label

---

## `world_tick.yml` — Runs Hourly at `:17`

```yaml
on:
  schedule:
    - cron: '17 * * * *'    # :17 avoids GitHub's top-of-hour congestion
  workflow_dispatch:          # Manual trigger for testing
```

**Steps:**
1. `checkout`
2. `engine.py tick` — world tick logic
3. `render.py` — re-render README
4. `build_pages.py` — rebuild `web/index.html` from new state
5. `git-auto-commit-action` — commits `README.md`, `state.json`, and `web/index.html` only if files changed

---

## `deploy_pages.yml` — Deploys to GitHub Pages

Triggers on every push to `main` that modifies `web/index.html` (i.e., after every game update commit). Also has `workflow_dispatch` for manual deploys.

```yaml
on:
  push:
    branches: [main]
    paths:
      - "web/index.html"
  workflow_dispatch:
```

**Steps:**
1. `checkout`
2. `actions/configure-pages` — set up Pages environment
3. `actions/upload-pages-artifact` — uploads the `web/` folder as the Pages artifact
4. `actions/deploy-pages` — deploys the artifact to GitHub Pages

**Required repo setting:** Go to Settings → Pages → Source: **GitHub Actions** (not "Deploy from a branch").

The live site URL is `https://{owner}.github.io/{repo}/`.

The tick workflow skips the commit entirely if nothing changed.

---

## Concurrency

Both workflows share the same concurrency group `realm-update`. GitHub Actions serializes all runs — one active, one queued. `cancel-in-progress: false` ensures no move is silently dropped.

**Worst case:** A player submits a move during a world tick. Their move queues and runs immediately after the tick completes. Total delay is at most ~30 seconds.

**Commit conflicts:** `stefanzweifel/git-auto-commit-action` uses `git pull --rebase` before pushing. Since only one workflow runs at a time, conflicts do not occur in practice.

---

## Race Condition Notes

The primary risk is two moves being processed simultaneously, causing a git conflict on `state.json`. The concurrency group prevents this entirely — GitHub Actions serializes at most 1 running + 1 pending per group. At high volume this means some moves queue briefly, but none are dropped or corrupted.

---

## Issue Template Protocol

Templates live in `.github/ISSUE_TEMPLATE/`. The `title` field in each template pre-fills the Issue title, which is the primary input the game engine parses.

| Action | Title Format | Example |
|--------|-------------|---------|
| Found | `FOUND: Civilization Name` | `FOUND: Sons of the Nile` |
| Join | `JOIN slug` | `JOIN sons-of-the-nile` |
| Attack | `ATTACK row col` | `ATTACK -3 4` |
| Alliance | `ALLY from-slug to-slug` | `ALLY sons-of-the-nile iron-legion` |

**Negative coordinate handling:**

`ATTACK+-3+4` in a URL → `ATTACK -3 4` in the title → `row=-3, col=4`.

The parser handles this:
```python
clean = t[7:].strip().replace("+", " ")
parts = clean.split()
return "attack", {"row": int(parts[0]), "col": int(parts[1])}
```
