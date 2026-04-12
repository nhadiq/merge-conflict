# Architecture

## What This Is

`merge-conflict` is a persistent, multiplayer civilization strategy game that uses a GitHub repository as its entire game surface. Players interact exclusively through GitHub Issues. The README is the live game board, rewritten by a GitHub Actions workflow on every move.

The world is infinite and procedurally generated. It expands as player count grows. Factions are uncapped. The game has no end state.

**Entire stack:**

- **State**: a single `state.json` file committed to the repo
- **Logic**: Python scripts in `scripts/`
- **Automation**: two GitHub Actions workflows
- **Frontend**: a dynamically rendered `README.md`
- **Input**: GitHub Issues with structured titles
- **Infrastructure cost**: $0

---

## Data Flow

```
Player opens an Issue
        ↓
GitHub Actions fires (on: issues: opened)
        ↓
process_issue.py reads the Issue title
        ↓
gh_stats.py fetches the player's live GitHub stats
        ↓
engine.py resolves the action (found / join / attack)
        ↓
state.json is updated
        ↓
render.py rewrites README.md from the new state
        ↓
build_pages.py injects state.json into web/index.template.html → web/index.html
        ↓
stefanzweifel/git-auto-commit-action commits README.md, state.json, web/index.html
        ↓
GitHub Actions comments the result on the Issue and closes it
        ↓
deploy_pages.yml detects the push to main, uploads web/ and deploys to GitHub Pages
        ↓
Player sees their move on the live README and the GitHub Pages map
```

A cron workflow runs every hour at `:17` to tick the world forward — updating scores, firing world events, checking faction dissolution, triggering map expansion.

---

## Repository Structure

```
merge-conflict/
├── README.md                          # Live game board (auto-generated — do not hand-edit)
├── state.json                         # Single source of truth for all game state
├── docs/                              # Documentation only (never hand-edit generated files)
│   ├── README.md                      # Index and update policy
│   ├── architecture.md                # This file
│   ├── state-schema.md
│   ├── game-mechanics.md
│   ├── scripts.md
│   ├── workflows.md
│   ├── contributing.md
│   ├── roadmap.md
│   └── player-guide.md
├── web/                               # GitHub Pages source
│   ├── index.template.html            # Game page template (hand-edit this)
│   └── index.html                     # Built output (auto-generated — do not hand-edit)
├── scripts/
│   ├── world.py                       # Infinite procedural world generator
│   ├── engine.py                      # Core game logic (factions, combat, ticks)
│   ├── render.py                      # README renderer (map, tables, links)
│   ├── gh_stats.py                    # GitHub public API stat fetcher
│   ├── process_issue.py               # Issue router — entry point for Actions
│   └── build_pages.py                 # GitHub Pages builder (state.json → web/index.html)
└── .github/
    ├── workflows/
    │   ├── process_move.yml           # Fires on every new Issue
    │   ├── world_tick.yml             # Hourly cron tick
    │   └── deploy_pages.yml           # Deploys web/ to GitHub Pages on push to main
    └── ISSUE_TEMPLATE/
        ├── found_faction.yml
        ├── join_faction.yml
        ├── attack.yml
        └── config.yml
```

---

## System Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     GitHub Platform                      │
│                                                          │
│  Issues ──► Actions ──► Python ──► state.json           │
│                │                        │                │
│                │                        ▼                │
│                └──────────────► README.md (committed)    │
│                                                          │
│  Cron (hourly) ──► Actions ──► Python ──► state.json    │
│                                      │                   │
│                                      ▼                   │
│                              README.md (committed)       │
└─────────────────────────────────────────────────────────┘
```

There is no external server, database, or hosting. Everything lives in git history. The `state.json` file is the database. Each commit is an append-only transaction log.

---

## Key Design Principles

- **All state mutations go through `engine.py`** — `world.py` and `render.py` are read-only relative to game state
- **`render.py` is a pure function** — it has no persistent state, just transforms `state.json` → `README.md`
- **Concurrency is handled at the Actions level** — both workflows share a `merge-conflict-update` concurrency group
- **No external dependencies** — Python 3.10+ standard library only
