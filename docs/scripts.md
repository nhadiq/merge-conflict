# Scripts Reference

All scripts live in `scripts/`. Python 3.10+ standard library only — no external dependencies.

---

## `world.py` — World Generator

Generates tiles on-demand using deterministic MD5 hashing. Identical inputs always produce identical tiles. Does not mutate `state.json`.

**Tile generation:**
```python
def _hash(row: int, col: int, seed: int = 42) -> int:
    key = f"{seed}:{row}:{col}"
    return int(hashlib.md5(key.encode()).hexdigest(), 16)
```

**Key functions:**
- `get_tile(row, col)` — returns tile dict for given coordinate
- `compute_world_size(player_count, faction_count)` — returns world radius
- `expand_world(state)` — pre-generates new ring of tiles if needed

**Wonder spawn rule:** `hash(row, col) % 40 == 7`

---

## `engine.py` — Game Engine

Handles all state mutations. Only this file should write to `state.json`.

**Key functions:**

| Function | Purpose |
|----------|---------|
| `found_faction(state, username, name)` | Registers a new civilization, claims spawn tile |
| `join_faction(state, username, slug)` | Adds a player to an existing faction |
| `attack(state, username, row, col)` | Resolves combat, updates ownership |
| `propose_alliance(state, username, from_slug, to_slug)` | Records alliance proposal |
| `world_tick(state)` | Hourly update — scores, events, dissolution, expansion |
| `compute_github_power(gh_stats)` | Converts raw GitHub stats into game power values |
| `apply_wonder_bonus(state, faction_slug)` | Adds wonder-derived bonuses to faction power |

**Spawn point selection:**

New factions spawn at cardinal and intercardinal edge points of current world bounds, in order of registration. Falls back to `(0, 0)` if all spawn points are occupied.

---

## `render.py` — README Renderer

Pure function: `state.json` → `README.md`. Has no persistent state of its own.

**Key behaviors:**
- For worlds >20 rows or columns, clips to `MAX_RENDER_SIZE × MAX_RENDER_SIZE` viewport
- Viewport centers on the centroid of all owned tiles
- Every capturable tile renders as a Markdown link opening a pre-filled Issue

```python
def _find_center_of_action(state):
    owned = [t for t in state["tiles"].values() if t.get("owner")]
    avg_r = sum(t["row"] for t in owned) // len(owned)
    avg_c = sum(t["col"] for t in owned) // len(owned)
    return (avg_r, avg_c)
```

**Column labeling:** Columns beyond Z use two-character system (AA, AB...).

---

## `gh_stats.py` — GitHub Stats Fetcher

Fetches public GitHub data using unauthenticated or token-authenticated API calls.

**Endpoints used:**
- `GET /users/{username}` — followers, public repo count
- `GET /users/{username}/events/public?per_page=30` — recent activity

**Stats computed:**

| Stat | Source |
|------|--------|
| `commits_today` | `PushEvent` where `created_at.date == today` |
| `prs_merged` | `PullRequestEvent` with `action == "closed"` and `merged == true` |
| `prs_open` | `PullRequestEvent` with `action == "opened"` |
| `issues_closed` | `IssuesEvent` with `action == "closed"` |
| `streak_days` | `PushEvent` consecutive days with commits backwards from today |
| `followers` | `user.followers` |
| `public_repos` | `user.public_repos` |

**Rate limits:** Unauthenticated: 60 req/hr. With `GITHUB_TOKEN`: 1,000 req/hr. Each move makes 2 API calls.

---

## `process_issue.py` — Issue Processor

Orchestration entry point. Called by `process_move.yml` with environment variables from the GitHub event payload.

**Environment variables consumed:**

| Variable | Source |
|----------|--------|
| `ISSUE_TITLE` | `github.event.issue.title` |
| `ISSUE_BODY` | `github.event.issue.body` |
| `ISSUE_AUTHOR` | `github.event.issue.user.login` |
| `GITHUB_TOKEN` | `secrets.GITHUB_TOKEN` (auto-injected) |

**Title parsing:**
```python
def parse_title(title: str):
    tu = title.strip().upper()
    if tu.startswith("FOUND:"):   return "found",  {"name": title[6:].strip()}
    if tu.startswith("JOIN "):    return "join",   {"slug": title[5:].strip().lower()}
    if tu.startswith("ATTACK "): ...  # parse row/col
    if tu.startswith("ALLY "):   ...  # parse faction slugs
    return "unknown", {}
```

**Output:** Writes to `$GITHUB_OUTPUT` for the Actions comment step.

---

## `build_pages.py` — GitHub Pages Builder

Reads `state.json` and `docs/index.template.html`, injects the state as inline JSON, and writes `docs/index.html`. Called by both workflows after `render.py`.

**Injection pattern:**
```python
state_json = json.dumps(state, separators=(",", ":"))
html = template.replace("__STATE_JSON__", state_json)
html = html.replace("'__REPO_URL__'", json.dumps(repo_url))
```

**Repo URL detection:** Reads `git remote get-url origin` automatically. Can be overridden with `--repo-url https://github.com/owner/repo`.

**Output:** `web/index.html` — fully self-contained, committed alongside `README.md` and `state.json` on every game update. The `deploy_pages.yml` workflow then picks up the push to `main` and deploys the `web/` folder to GitHub Pages.

**Do not hand-edit `web/index.html`** — edit `web/index.template.html` instead.
