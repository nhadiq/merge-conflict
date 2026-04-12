#!/usr/bin/env python3
"""
render.py — Scalable README renderer for merge-conflict v2
Handles infinite maps by rendering a viewport window.
Shows clickable attack grid, live leaderboard, world stats.
"""

import json
import math
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))
from world import get_or_generate_tile, BIOMES
from engine import _coord

MAX_RENDER_SIZE = 20  # Max rows/cols to render in README (viewport)

def load_state():
    with open(ROOT / "state.json") as f:
        return json.load(f)

def get_banner(state, owner_slug):
    if not owner_slug or owner_slug not in state["factions"]:
        return None
    return state["factions"][owner_slug]["banner"]

def render_map_viewport(state):
    """
    Renders the visible world as an ASCII map.
    Clips to MAX_RENDER_SIZE for README readability.
    Shows faction banners on controlled tiles.
    """
    b = state["world_bounds"]
    total_rows = b["max_row"] - b["min_row"] + 1
    total_cols = b["max_col"] - b["min_col"] + 1

    # If world is larger than viewport, center on most contested area
    if total_rows > MAX_RENDER_SIZE or total_cols > MAX_RENDER_SIZE:
        center_r, center_c = _find_center_of_action(state)
        half = MAX_RENDER_SIZE // 2
        r_start = max(b["min_row"], center_r - half)
        r_end   = min(b["max_row"], r_start + MAX_RENDER_SIZE - 1)
        c_start = max(b["min_col"], center_c - half)
        c_end   = min(b["max_col"], c_start + MAX_RENDER_SIZE - 1)
    else:
        r_start, r_end = b["min_row"], b["max_row"]
        c_start, c_end = b["min_col"], b["max_col"]

    cols_shown = c_end - c_start + 1
    rows_shown = r_end - r_start + 1

    lines = []
    lines.append("```")

    # Column header
    header = "    "
    for c in range(c_start, c_end + 1):
        label = chr(ord('A') + (c % 26))
        if c >= 26: label = chr(ord('A') + c // 26 - 1) + label
        header += f" {label:2}"
    lines.append(header)
    lines.append("  ┌" + "─" * (cols_shown * 3 + 1) + "┐")

    for r in range(r_start, r_end + 1):
        row_str = f"{r:2}│"
        for c in range(c_start, c_end + 1):
            tile = get_or_generate_tile(state, r, c)
            owner = tile.get("owner")
            banner = get_banner(state, owner)
            cell = banner if banner else tile["emoji"]
            row_str += f" {cell}"
        row_str += " │"
        lines.append(row_str)

    lines.append("  └" + "─" * (cols_shown * 3 + 1) + "┘")

    if total_rows > MAX_RENDER_SIZE or total_cols > MAX_RENDER_SIZE:
        lines.append(f"  Showing {rows_shown}×{cols_shown} of {total_rows}×{total_cols} world")

    lines.append("```")
    return "\n".join(lines)

def render_attack_grid(state):
    """
    Renders a clickable markdown table for the current viewport.
    Each capturable tile is a link that opens a pre-filled Issue.
    """
    b = state["world_bounds"]
    total_rows = b["max_row"] - b["min_row"] + 1
    total_cols = b["max_col"] - b["min_col"] + 1

    if total_rows > MAX_RENDER_SIZE or total_cols > MAX_RENDER_SIZE:
        center_r, center_c = _find_center_of_action(state)
        half = MAX_RENDER_SIZE // 2
        r_start = max(b["min_row"], center_r - half)
        r_end   = min(b["max_row"], r_start + MAX_RENDER_SIZE - 1)
        c_start = max(b["min_col"], center_c - half)
        c_end   = min(b["max_col"], c_start + MAX_RENDER_SIZE - 1)
    else:
        r_start, r_end = b["min_row"], b["max_row"]
        c_start, c_end = b["min_col"], b["max_col"]

    # Header row
    col_labels = []
    for c in range(c_start, c_end + 1):
        label = chr(ord('A') + (c % 26))
        if c >= 26: label = chr(ord('A') + c // 26 - 1) + label
        col_labels.append(label)

    header = "| | " + " | ".join(col_labels) + " |"
    sep    = "|---|" + "---|" * len(col_labels)
    lines  = [header, sep]

    for r in range(r_start, r_end + 1):
        row_cells = [f"**{r}**"]
        for c in range(c_start, c_end + 1):
            tile = get_or_generate_tile(state, r, c)
            if tile["terrain"] in ("sea", "fjord"):
                row_cells.append("🌊")
            else:
                owner = tile.get("owner")
                banner = get_banner(state, owner)
                emoji = banner if banner else tile["emoji"]
                title = f"ATTACK+{r}+{c}"
                row_cells.append(f"[{emoji}](../../issues/new?template=attack.yml&title={title})")
        lines.append("| " + " | ".join(row_cells) + " |")

    return "\n".join(lines)

def render_faction_table(state):
    factions = {s: f for s, f in state["factions"].items() if not f.get("dissolved")}
    if not factions:
        return "_No civilizations yet. Be the first to rise._\n\n[⚔️ **Found a Civilization →**](../../issues/new?template=found_faction.yml)"

    ranked = sorted(factions.items(), key=lambda x: x[1]["score"], reverse=True)

    rows = [
        "| Rank | Banner | Civilization | Founder | Warriors | Territories | Wonders | Score |",
        "|------|--------|-------------|---------|----------|-------------|---------|-------|"
    ]

    medals = ["🥇", "🥈", "🥉"]
    for i, (slug, f) in enumerate(ranked):
        rank = medals[i] if i < 3 else f"#{i+1}"
        members = len(f["members"])
        territories = len(f["territories"])
        wonders = sum(1 for t in state["tiles"].values()
                     if t.get("owner") == slug and t.get("wonder"))
        alliances = len(f.get("alliances", []))
        alliance_note = f" 🤝×{alliances}" if alliances else ""
        rows.append(
            f"| {rank} | {f['banner']} | **{f['name']}**{alliance_note} | @{f['founder']} | {members} | {territories} | {wonders} | **{f['score']}** |"
        )

    return "\n".join(rows)

def render_world_stats(state):
    b = state["world_bounds"]
    total_rows = b["max_row"] - b["min_row"] + 1
    total_cols = b["max_col"] - b["min_col"] + 1
    total_tiles = total_rows * total_cols
    claimed = sum(1 for t in state["tiles"].values() if t.get("owner"))
    wonders_found = sum(1 for t in state["tiles"].values() if t.get("wonder") and t.get("owner"))
    wonders_total = sum(1 for t in state["tiles"].values() if t.get("wonder"))
    active_factions = sum(1 for f in state["factions"].values() if not f.get("dissolved"))
    pct = round(claimed / max(total_tiles, 1) * 100, 1)

    return f"""| Stat | Value |
|------|-------|
| 🌍 World size | {total_rows}×{total_cols} ({total_tiles:,} tiles) |
| ⚔️ Claimed | {claimed:,} tiles ({pct}%) |
| 🏛️ Civilizations | {active_factions} active |
| 👥 Warriors | {state['player_count']} |
| ✨ Wonders | {wonders_found}/{wonders_total} discovered |
| 🌐 World Age | {state['world_age']} |"""

def render_streak_guide():
    return """| Streak | Bonus |
|--------|-------|
| 3 days | 🗡️ +1 attack |
| 7 days | ⚡ Guaranteed capture (ignores terrain defense) |
| 14 days | 🌟 Claim 2 tiles per move |
| 30 days | 👑 Legendary: immune to attack for 24h |

**Commits = soldiers. PRs = sieges. Followers = morale. Streaks = divine favour.**"""

def render_hall_of_fame(state):
    hof = state.get("hall_of_fame", [])
    if not hof:
        return "_The chronicles are unwritten. History begins now._"
    rows = ["| Age | Civilization | Founder | Score | Territories |",
            "|-----|-------------|---------|-------|-------------|"]
    for entry in reversed(hof[-10:]):
        rows.append(f"| {entry['age']} | {entry['banner']} **{entry['faction']}** | @{entry['founder']} | {entry['score']} | {entry['territories']} |")
    return "\n".join(rows)

def render_event_log(state):
    log = state.get("event_log", [])[-12:]
    if not log:
        return "_The world is silent. Be the first to make history._"
    return "\n".join(f"- {e}" for e in reversed(log))

def render_join_links(state):
    active = {s: f for s, f in state["factions"].items() if not f.get("dissolved")}
    lines = []
    for slug, f in sorted(active.items(), key=lambda x: x[1]["score"], reverse=True):
        members = len(f["members"])
        territories = len(f["territories"])
        lines.append(
            f"- {f['banner']} **{f['name']}** — {members} warriors, {territories} territories · "
            f"[Join](../../issues/new?template=join_faction.yml&title=JOIN+{slug})"
        )
    lines.append(f"\n[⚔️ **Found your own civilization →**](../../issues/new?template=found_faction.yml)")
    return "\n".join(lines)

def render_biome_legend(state):
    b = state["world_bounds"]
    radius = (b["max_row"] - b["min_row"]) // 2
    seeds = state["biome_seeds"]

    active_biomes = set(["heartland"])
    if radius >= 3:
        active_biomes.update(seeds.values())

    lines = []
    for biome_name in active_biomes:
        if biome_name in BIOMES:
            biome = BIOMES[biome_name]
            sample_emojis = [v[1] for v in list(biome["terrains"].values())[:3]]
            lines.append(f"- {''.join(sample_emojis)} **{biome['label']}**")
    return "\n".join(lines) if lines else ""

def _find_center_of_action(state):
    """Find the most contested area for viewport centering."""
    owned = [t for t in state["tiles"].values() if t.get("owner")]
    if not owned:
        return (0, 0)
    avg_r = sum(t["row"] for t in owned) // len(owned)
    avg_c = sum(t["col"] for t in owned) // len(owned)
    return (avg_r, avg_c)

def render_readme(state):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    b = state["world_bounds"]
    total_rows = b["max_row"] - b["min_row"] + 1
    total_cols = b["max_col"] - b["min_col"] + 1
    active_factions = sum(1 for f in state["factions"].values() if not f.get("dissolved"))

    world_map    = render_map_viewport(state)
    attack_grid  = render_attack_grid(state)
    faction_table = render_faction_table(state)
    world_stats  = render_world_stats(state)
    streak_guide = render_streak_guide()
    hof          = render_hall_of_fame(state)
    event_log    = render_event_log(state)
    join_links   = render_join_links(state)
    biome_legend = render_biome_legend(state)

    return f"""# ⚔️ merge-conflict — The Infinite War

> An endless civilization game that lives entirely on GitHub.
> Your code is your army. Your commits are your soldiers.
> The world grows as the community grows.

**{state['player_count']} warriors · {active_factions} civilizations · {total_rows}×{total_cols} world · Age {state['world_age']} · {now}**

---

## 🗺️ The World Map

{world_map}

**Active Biomes**
{biome_legend}

> The world expands automatically as more players join. New biomes, wonders, and territories unlock continuously.

---

## ⚔️ Conquer Territory — Click any tile

> Click a tile to attack it. Your GitHub activity powers your army automatically.

{attack_grid}

---

## 🏛️ Civilizations

{faction_table}

---

## 📊 World Statistics

{world_stats}

---

## 🎮 How to Play

### 1 — Choose your side

{join_links}

### 2 — Attack tiles

Click any tile in the grid above → submit the Issue → your move is processed automatically.

### 3 — Build your GitHub power

{streak_guide}

### 4 — Expand the world

Every new player grows the map. Recruit allies and unlock new biomes.

---

## ✨ Ancient Wonders

Wonders spawn in newly discovered territory. Controlling one gives your entire faction a permanent bonus:

| Wonder | Bonus |
|--------|-------|
| 🔺 The Great Pyramid | +5 attack for all faction members |
| ⚡ Valhalla's Gate | +1 streak tier for all members |
| 👑 The Silk Throne | +2 morale (faction-wide) |
| 🌆 Temple of Baal | +4 defense (impenetrable garrison) |
| 🏛️ The Parthenon | +2 attack (wisdom of ages) |
| 🗿 The Colossus | +3 attack (sea projection) |

---

## 🤝 Alliances

Factions can form alliances. Allied factions share morale bonuses and cannot attack each other.

[📜 **Propose an Alliance →**](../../issues/new?template=alliance.yml)

---

## 📜 Chronicles

{event_log}

---

## 🏆 Hall of Fame

{hof}

---

## 🌍 World Expansion Rules

| Players | World Size | Factions Allowed |
|---------|-----------|-----------------|
| 1–10 | 5×5 | Unlimited (50+ followers or 10+ repos to found) |
| 10–50 | ~12×12 | Unlimited |
| 50–200 | ~20×20 | Unlimited |
| 200–1000 | ~36×36 | Unlimited |
| 1000+ | ~72×72+ | Unlimited |

The world has no fixed size. It grows forever with the community.
Factions that lose all territory dissolve after 7 days. Their lands are free for the taking.

---

<sub>⚔️ merge-conflict — Built on GitHub Actions · Zero install · Zero sign-up · Just GitHub<br>
Made by <a href="https://github.com/nhadiq">@nhadiq</a> · Star to support the project · Fork to study the engine</sub>
"""

if __name__ == "__main__":
    state = load_state()
    readme = render_readme(state)
    with open(ROOT / "README.md", "w") as f:
        f.write(readme)
    print("README rendered.")
