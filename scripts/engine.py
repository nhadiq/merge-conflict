#!/usr/bin/env python3
"""
engine.py — realm.md Game Engine v2
Infinite world. Uncapped factions. GitHub-powered combat.
"""

import json
import math
import os
import sys
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent

sys.path.insert(0, str(Path(__file__).parent))
from world import (
    get_or_generate_tile, expand_world_if_needed,
    compute_world_size, _log, get_biome_name
)

# ── Faction banner pool — expands as factions grow ──────────────────────────
BANNERS = [
    "🔴","🔵","🟡","🟢","🟣","🟠","⚫","⚪",
    "🩷","🩵","🟤","🔶","🔷","🔸","🔹","🔺",
    "💜","💙","💚","💛","🧡","❤️","🖤","🤍",
]

# ── State I/O ────────────────────────────────────────────────────────────────

def load_state():
    with open(ROOT / "state.json") as f:
        return json.load(f)

def save_state(state):
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(ROOT / "state.json", "w") as f:
        json.dump(state, f, indent=2)

# ── GitHub power ─────────────────────────────────────────────────────────────

def compute_github_power(gh_data: dict) -> dict:
    c      = gh_data.get("commits_today", 0)
    prs_m  = gh_data.get("prs_merged", 0)
    prs_o  = gh_data.get("prs_open", 0)
    issues = gh_data.get("issues_closed", 0)
    follow = gh_data.get("followers", 0)
    streak = gh_data.get("streak_days", 0)
    repos  = gh_data.get("public_repos", 0)

    attack  = min(15, c * 2 + prs_m * 3)
    defense = min(10, prs_o + issues)
    morale  = round(min(8, math.log1p(follow)), 2)

    # Streak tiers
    streak_tier = 0
    if streak >= 30: streak_tier = 4
    elif streak >= 14: streak_tier = 3
    elif streak >= 7:  streak_tier = 2
    elif streak >= 3:  streak_tier = 1

    # Wonder bonus (controlling a wonder gives +3 attack)
    return {
        "attack":      attack,
        "defense":     defense,
        "morale":      morale,
        "streak":      streak,
        "streak_tier": streak_tier,
        "repos":       repos,
        "followers":   follow,
    }

def apply_wonder_bonus(state, faction_slug, power):
    """Add bonuses for wonders controlled by this faction."""
    controlled_wonders = [
        tile for tile in state["tiles"].values()
        if tile.get("owner") == faction_slug and tile.get("wonder")
    ]
    bonus = {"attack": 0, "defense": 0, "morale": 0}
    for tile in controlled_wonders:
        wb = tile.get("wonder_bonus", "")
        if wb == "double_attack": bonus["attack"] += 5
        elif wb == "streak_boost": power["streak_tier"] = min(4, power["streak_tier"] + 1)
        elif wb == "morale_aura":  bonus["morale"] += 2
        elif wb == "garrison":     bonus["defense"] += 4
        elif wb == "scholar":      bonus["attack"] += 2
        elif wb == "sea_control":  bonus["attack"] += 3
    power["attack"]  += bonus["attack"]
    power["defense"] += bonus["defense"]
    power["morale"]  += bonus["morale"]
    return power

# ── Faction formation ─────────────────────────────────────────────────────────

def can_found_faction(state, username, gh_data):
    """
    Anyone can found a faction if they have enough GitHub presence.
    Rules: 50+ followers OR 10+ public repos OR existing player vouching.
    """
    followers = gh_data.get("followers", 0)
    repos     = gh_data.get("public_repos", 0)
    return followers >= 50 or repos >= 10

def found_faction(state, username, faction_name, gh_data=None):
    """Found a new faction. No cap on number of factions."""
    gh = gh_data or {}

    if username in state["players"]:
        existing_slug = state["players"][username]["faction"]
        return False, f"You already lead or belong to **{state['factions'][existing_slug]['name']}**."

    # Normalize slug
    slug = re.sub(r"[^a-z0-9]", "-", faction_name.lower())[:24].strip("-")
    if not slug:
        return False, "Invalid name."

    if slug in state["factions"]:
        return False, f"A faction named '{faction_name}' already exists."

    # Founding requirements — relaxed if world is new
    if state["player_count"] > 10 and not can_found_faction(state, username, gh):
        followers = gh.get("followers", 0)
        repos     = gh.get("public_repos", 0)
        return False, (
            f"To found a civilization you need 50+ GitHub followers or 10+ public repos. "
            f"You have {followers} followers and {repos} repos. "
            f"Alternatively, join an existing faction and grow your influence."
        )

    power  = compute_github_power(gh)
    banner = BANNERS[len(state["factions"]) % len(BANNERS)]

    # Spawn at a corner or edge of current world, away from others
    start = _find_spawn(state)

    state["factions"][slug] = {
        "name":         faction_name,
        "slug":         slug,
        "founder":      username,
        "banner":       banner,
        "members":      [username],
        "power":        power,
        "territories":  [list(start)],
        "score":        0,
        "founded_age":  state["world_age"],
        "dissolved":    False,
        "alliances":    [],
    }

    # Claim start tile
    tile = get_or_generate_tile(state, start[0], start[1])
    tile["owner"] = slug

    state["players"][username] = {
        "faction":    slug,
        "role":       "founder",
        "joined_age": state["world_age"],
        "moves":      0,
        "gh_power":   power,
    }

    state["player_count"] = len(state["players"])
    state["faction_count"] = len(state["factions"])

    # Check if world should expand
    expanded = expand_world_if_needed(state)

    _log(state, f"🏛️ **{faction_name}** rises from the earth! Founded by @{username} {banner}")

    msg = f"Civilization **{faction_name}** founded {banner}! You control {_coord(*start)}."
    if expanded:
        msg += " The world just grew — new frontiers await."
    return True, msg

def join_faction(state, username, faction_slug):
    if username in state["players"]:
        return False, "You already belong to a faction."

    slug = faction_slug.lower().strip()
    if slug not in state["factions"]:
        return False, f"No faction '{faction_slug}' found. Check the README for current factions."

    if state["factions"][slug].get("dissolved"):
        return False, "That faction has dissolved. Choose another."

    state["factions"][slug]["members"].append(username)
    state["players"][username] = {
        "faction":    slug,
        "role":       "warrior",
        "joined_age": state["world_age"],
        "moves":      0,
        "gh_power":   {},
    }
    state["player_count"] = len(state["players"])
    expand_world_if_needed(state)

    faction = state["factions"][slug]
    _log(state, f"⚔️ @{username} pledges to **{faction['name']}** {faction['banner']}")
    return True, f"You joined **{faction['name']}** {faction['banner']}! Head to the map and claim territory."

# ── Combat ────────────────────────────────────────────────────────────────────

def attack(state, username, row, col, gh_data=None):
    if username not in state["players"]:
        return False, "Join a faction first — open a Join issue."

    player      = state["players"][username]
    faction_slug = player["faction"]
    faction     = state["factions"][faction_slug]

    tile = get_or_generate_tile(state, row, col)

    # Sea tiles uncapturable
    if tile["terrain"] in ("sea", "fjord"):
        return False, "You cannot conquer open water. Control coastal tiles to project naval power."

    # Must be adjacent to owned territory
    if not _adjacent_to_faction(state, faction_slug, row, col):
        return False, (
            f"({row},{col}) is not adjacent to your territory. "
            f"Expand from your current border tiles."
        )

    # Compute attacker power
    gh   = gh_data or player.get("gh_power", {})
    power = compute_github_power(gh)
    power = apply_wonder_bonus(state, faction_slug, power)
    player["gh_power"] = power
    player["moves"] += 1

    # Streak tiers
    tier = power["streak_tier"]
    attack_roll = power["attack"] + power["morale"]
    if tier >= 1: attack_roll += 1
    if tier >= 2: attack_roll += 3   # guaranteed-ish
    if tier >= 3: attack_roll *= 1.5
    if tier >= 4: attack_roll *= 2   # legendary

    # Defender
    defender_slug = tile.get("owner")
    defense_roll  = tile["defense"]

    if defender_slug and defender_slug != faction_slug:
        defender = state["factions"][defender_slug]
        # Add defenders' collective GitHub defense
        for m in defender["members"]:
            p = state["players"].get(m, {})
            defense_roll += p.get("gh_power", {}).get("defense", 0) * 0.5
        defense_roll = apply_wonder_bonus(state, defender_slug, {"attack": 0, "defense": defense_roll, "morale": 0, "streak_tier": 0})["defense"]

    # 30-day legendary streak = immune for 24h (tracked in state)
    if defender_slug:
        immunity_key = f"immune_{defender_slug}"
        if state.get(immunity_key, 0) > state["world_age"]:
            return False, f"**{state['factions'][defender_slug]['name']}** is under legendary protection. Return tomorrow."

    guaranteed = tier >= 2  # 7+ day streak guarantees capture
    success     = guaranteed or (attack_roll > defense_roll)

    coord_name = _coord(row, col)

    if success:
        # Remove from old owner
        if defender_slug and defender_slug != faction_slug and defender_slug in state["factions"]:
            old = state["factions"][defender_slug]
            old["territories"] = [t for t in old["territories"] if t != [row, col]]
            _log(state, f"⚔️ {faction['banner']} **{faction['name']}** seized **{coord_name}** ({tile['label']}) from {old['banner']} {old['name']}")
            # Check if faction is now destroyed
            _check_dissolution(state, defender_slug)
        elif not defender_slug:
            wonder_note = f" ✨ **{tile['wonder']}** discovered!" if tile.get("wonder") else ""
            _log(state, f"🏴 {faction['banner']} **{faction['name']}** claimed **{coord_name}** ({tile['label']}){wonder_note}")

        tile["owner"] = faction_slug
        if [row, col] not in faction["territories"]:
            faction["territories"].append([row, col])

        # 30-day streak immunity
        if tier >= 4:
            state[f"immune_{faction_slug}"] = state["world_age"] + 24
            _log(state, f"👑 @{username} invokes **Legendary Status** — {faction['name']} is immune for 24 hours!")

        msg = f"Victory! **{faction['name']}** controls {coord_name} ({tile['label']})."
        if tile.get("wonder"):
            msg += f" ✨ You've captured the **{tile['wonder']}** wonder — bonus activated!"
        return True, msg

    else:
        _log(state, f"🛡️ **{coord_name}** holds against {faction['banner']} {faction['name']} (DEF {defense_roll:.1f} vs ATK {attack_roll:.1f})")
        return False, (
            f"Attack failed. {coord_name} defense ({defense_roll:.1f}) exceeded your power ({attack_roll:.1f}). "
            f"Boost your attack: commit more code today, or build a 7-day streak for guaranteed capture."
        )

# ── Alliance system ───────────────────────────────────────────────────────────

def propose_alliance(state, from_slug, to_slug):
    if from_slug not in state["factions"] or to_slug not in state["factions"]:
        return False, "Invalid faction."
    if to_slug in state["factions"][from_slug].get("alliances", []):
        return False, "Already allied."
    if "alliances" not in state:
        state["alliances"] = {}
    key = f"{from_slug}+{to_slug}"
    state["alliances"][key] = {"status": "proposed", "from": from_slug, "to": to_slug}
    faction_a = state["factions"][from_slug]
    faction_b = state["factions"][to_slug]
    _log(state, f"🤝 **{faction_a['name']}** {faction_a['banner']} proposes alliance to **{faction_b['name']}** {faction_b['banner']}")
    return True, f"Alliance proposed to {state['factions'][to_slug]['name']}. They must accept via an Alliance issue."

# ── World tick ────────────────────────────────────────────────────────────────

WORLD_EVENTS = [
    ("🌪️", "Sandstorm sweeps the desert — desert tiles grant +1 defense until next dawn."),
    ("🌊", "The Nile floods — all river tiles produce double morale bonus."),
    ("☄️", "Comet sighted — the smallest faction gains +5 attack for 24h."),
    ("❄️", "Blizzard in the North — Norse biome tiles gain +2 defense."),
    ("🔥", "Wildfire — jungle tiles in contested areas become neutral."),
    ("🌋", "Eruption — volcano tiles deal -2 to any attacker this cycle."),
    ("🌟", "Golden Age — all factions with 5+ members gain +1 morale."),
    ("⚔️",  "Age of War — all attack rolls +2 for this cycle."),
    ("🕊️",  "Era of Peace — defense rolls +3 for this cycle."),
    ("🏺", "Ancient relics unearthed — ruins and lost city tiles grant double score."),
    ("🌍", "Migration wave — all factions gain 1 free territory claim adjacent to their border."),
]

def world_tick(state):
    state["world_age"] += 1

    # Score all factions
    for slug, faction in state["factions"].items():
        if faction.get("dissolved"):
            continue
        territories = len(faction["territories"])
        members     = len(faction["members"])
        wonders     = sum(1 for t in state["tiles"].values()
                         if t.get("owner") == slug and t.get("wonder"))
        faction["score"] = territories * 10 + members * 5 + wonders * 25

    # Daily world event (every 24 ticks)
    if state["world_age"] % 24 == 0:
        import random
        event = random.choice(WORLD_EVENTS)
        _log(state, f"{event[0]} **World Event (Age {state['world_age']}):** {event[1]}")

        # Hall of fame snapshot every 30 days
        if state["world_age"] % 720 == 0:
            _snapshot_hall_of_fame(state)

    # Dissolve dead factions (no territory for 7 days = 168 ticks)
    for slug, faction in list(state["factions"].items()):
        if not faction.get("dissolved") and len(faction["territories"]) == 0:
            age_without = state["world_age"] - faction.get("last_territory_age", 0)
            if age_without > 168:
                faction["dissolved"] = True
                _log(state, f"💀 **{faction['name']}** {faction['banner']} has fallen. Their lands are free for the taking.")

    # Update territory ages
    for slug, faction in state["factions"].items():
        if len(faction["territories"]) > 0:
            faction["last_territory_age"] = state["world_age"]

    # Trim log
    state["event_log"] = state["event_log"][-30:]

    # Check expansion
    expand_world_if_needed(state)

def _snapshot_hall_of_fame(state):
    ranked = sorted(
        [(s, f) for s, f in state["factions"].items() if not f.get("dissolved")],
        key=lambda x: x[1]["score"], reverse=True
    )
    if ranked:
        top_slug, top = ranked[0]
        entry = {
            "age":     state["world_age"],
            "faction": top["name"],
            "banner":  top["banner"],
            "founder": top["founder"],
            "score":   top["score"],
            "territories": len(top["territories"]),
        }
        state["hall_of_fame"].append(entry)
        _log(state, f"📜 **Hall of Fame:** {top['banner']} **{top['name']}** leads the world at Age {state['world_age']} with {top['score']} glory.")

# ── Helpers ───────────────────────────────────────────────────────────────────

def _adjacent_to_faction(state, faction_slug, row, col):
    owned = state["factions"][faction_slug]["territories"]
    for t in owned:
        if abs(t[0] - row) + abs(t[1] - col) == 1:
            return True
    return False

def _find_spawn(state):
    """Find a good spawn point away from other factions."""
    bounds = state["world_bounds"]
    candidates = [
        (bounds["min_row"], bounds["min_col"]),
        (bounds["min_row"], bounds["max_col"]),
        (bounds["max_row"], bounds["min_col"]),
        (bounds["max_row"], bounds["max_col"]),
        (bounds["min_row"], (bounds["min_col"] + bounds["max_col"]) // 2),
        (bounds["max_row"], (bounds["min_col"] + bounds["max_col"]) // 2),
        ((bounds["min_row"] + bounds["max_row"]) // 2, bounds["min_col"]),
        ((bounds["min_row"] + bounds["max_row"]) // 2, bounds["max_col"]),
    ]
    all_owned = {
        tuple(t)
        for f in state["factions"].values()
        for t in f["territories"]
    }
    for c in candidates:
        if c not in all_owned:
            tile = get_or_generate_tile(state, c[0], c[1])
            if tile["terrain"] not in ("sea", "fjord"):
                return c

    # fallback: center
    return (0, 0)

def _check_dissolution(state, slug):
    faction = state["factions"].get(slug)
    if not faction:
        return
    if len(faction["territories"]) == 0:
        faction.setdefault("last_territory_age", state["world_age"])

def _coord(row, col):
    """Human readable coordinate."""
    col_letter = chr(ord('A') + (col % 26))
    if col >= 26: col_letter = chr(ord('A') + col // 26 - 1) + col_letter
    return f"{col_letter}{row}"

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: engine.py <action> [args]")
        sys.exit(1)

    state = load_state()
    action = sys.argv[1]

    if action == "tick":
        world_tick(state)
        print(f"World tick. Age: {state['world_age']}")

    elif action == "found" and len(sys.argv) >= 4:
        username = sys.argv[2]
        name     = " ".join(sys.argv[3:])
        ok, msg  = found_faction(state, username, name)
        print(msg)
        sys.exit(0 if ok else 1)

    elif action == "join" and len(sys.argv) >= 4:
        username = sys.argv[2]
        slug     = sys.argv[3]
        ok, msg  = join_faction(state, username, slug)
        print(msg)
        sys.exit(0 if ok else 1)

    elif action == "attack" and len(sys.argv) >= 5:
        username = sys.argv[2]
        row      = int(sys.argv[3])
        col      = int(sys.argv[4])
        ok, msg  = attack(state, username, row, col)
        print(msg)
        sys.exit(0 if ok else 1)

    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

    save_state(state)
