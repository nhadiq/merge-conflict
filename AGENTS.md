# AGENTS.md — AI Agent Instructions for merge-conflict

This file is read by all AI coding agents working in this repository, including:
- **Claude Code** (`claude` CLI)
- **OpenAI Codex** / ChatGPT with code tools
- **Cursor** (also has `.cursor/rules/` for more granular rules)
- **GitHub Copilot Workspace**
- **Gemini Code Assist**
- Any other AI assistant or automated coding agent

---

## 1. Read the Docs First — Always

**Before making any code change**, read the relevant documentation in the `docs/` folder.

Start here: [`docs/README.md`](./docs/README.md)

| If you're changing... | Read this doc first |
|----------------------|---------------------|
| Game mechanics, formulas, biomes, combat | [`docs/game-mechanics.md`](./docs/game-mechanics.md) |
| Scripts (`engine.py`, `world.py`, etc.) | [`docs/scripts.md`](./docs/scripts.md) |
| `state.json` shape or fields | [`docs/state-schema.md`](./docs/state-schema.md) |
| GitHub Actions workflows | [`docs/workflows.md`](./docs/workflows.md) |
| Biomes, wonders, actions, events | [`docs/contributing.md`](./docs/contributing.md) |
| Roadmap or known limitations | [`docs/roadmap.md`](./docs/roadmap.md) |
| Overall architecture and data flow | [`docs/architecture.md`](./docs/architecture.md) |
| Player-facing rules, terrain, strategy | [`docs/player-guide.md`](./docs/player-guide.md) |

Do not guess at intent from code alone. The docs describe the **design decisions** behind the code.

---

## 2. Update the Docs After Every Code Change

After making a change, **update the corresponding doc in `docs/`**. This is mandatory, not optional.

| What you changed | What to update |
|-----------------|----------------|
| Game logic in `engine.py` | `docs/game-mechanics.md` and/or `docs/scripts.md` |
| Tile generation in `world.py` | `docs/game-mechanics.md` and `docs/scripts.md` |
| Rendering in `render.py` | `docs/scripts.md` |
| Stats fetching in `gh_stats.py` | `docs/scripts.md` |
| Issue parsing in `process_issue.py` | `docs/scripts.md` |
| Fields in `state.json` | `docs/state-schema.md` |
| GitHub Actions workflows | `docs/workflows.md` |
| New biome, wonder, action, or event | `docs/contributing.md` and `docs/game-mechanics.md` |
| Roadmap item resolved or new limitation discovered | `docs/roadmap.md` |

If your change is purely cosmetic (formatting, comments, typos), doc updates are not required.

---

## 3. Architecture Rules

These constraints must not be violated:

1. **Only `engine.py` writes to `state.json`** — `world.py` and `render.py` are read-only relative to game state.
2. **`render.py` is a pure function** — it reads `state.json` and writes `README.md`. It has no other side effects.
3. **`README.md` is auto-generated** — never hand-edit it. Run `python scripts/render.py` to regenerate it.
4. **`docs/index.html` is auto-generated** — never hand-edit it. Edit `web/index.template.html`, then run `python scripts/build_pages.py` to regenerate.
5. **No external dependencies** — Python 3.10+ standard library only. Do not add `requirements.txt` entries or import third-party packages.
6. **All state time references use `world_age`** — the integer tick counter, not wall-clock time.

---

## 4. Project Overview (Quick Reference)

`merge-conflict` is a multiplayer civilization strategy game that runs entirely on GitHub. Players interact through GitHub Issues. The README is the live game board, auto-generated from `state.json`.

```
Player opens Issue
  → GitHub Actions fires process_issue.py
  → gh_stats.py fetches player's GitHub stats
  → engine.py resolves the action (found / join / attack)
  → state.json is updated
  → render.py rewrites README.md
  → Commit is pushed; result is commented on the Issue
```

An hourly cron workflow (`world_tick.yml`) ticks the world forward — updating scores, firing world events, checking faction dissolution, triggering map expansion.

**Key files:**
- `state.json` — the database (single source of truth)
- `scripts/engine.py` — all state mutations
- `scripts/world.py` — deterministic tile generation (read-only)
- `scripts/render.py` — README renderer (read-only)
- `scripts/gh_stats.py` — GitHub API fetcher
- `scripts/process_issue.py` — issue router / orchestration entry point
- `scripts/build_pages.py` — GitHub Pages builder (injects state into `web/index.template.html`)
- `web/index.template.html` — edit this to change the game page UI
- `web/index.html` — auto-generated output, deployed to GitHub Pages via `deploy_pages.yml` (never hand-edit)

---

## 5. Common Patterns

### Adding a new game action

1. Add an Issue template in `.github/ISSUE_TEMPLATE/`
2. Add a title prefix + parser branch in `process_issue.py`
3. Add a handler function in `engine.py`
4. Add any new state fields to `state.json`
5. Update `docs/scripts.md`, `docs/state-schema.md`, and `docs/contributing.md`

### Adding a new biome

1. Add biome definition to `BIOMES` in `world.py`
2. Add biome-appropriate wonders to `WONDERS` in `world.py`
3. Add the biome key to `biome_seeds` in `state.json`
4. Update `render_biome_legend()` in `render.py` if needed
5. Update `docs/game-mechanics.md`

### Adding a new wonder

1. Add to `WONDERS` in `world.py`
2. Add bonus effect to `apply_wonder_bonus()` in `engine.py`
3. Update `docs/game-mechanics.md`

---

## 6. Testing Changes Locally

```bash
python scripts/render.py                          # Render README from current state
python scripts/engine.py tick                     # Run a world tick
python scripts/gh_stats.py <github-username>      # Test stat fetching
python scripts/engine.py found testuser "Test Civilization"
python scripts/engine.py join testuser2 test-civilization
python scripts/engine.py attack testuser 0 1
```

No installation required. Python 3.10+ standard library only.
