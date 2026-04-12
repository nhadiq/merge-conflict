#!/usr/bin/env python3
"""
world.py — Infinite procedural world generator for merge-conflict
Tiles are generated on-demand using deterministic noise.
Biomes expand outward with cultural themes based on direction.
"""

import math
import hashlib
import json

# ── Biome definitions ────────────────────────────────────────────────────────

BIOMES = {
    "egypt": {
        "label": "The Ancient Nile",
        "terrains": {
            "desert":   (35, "🏜️", 0, "Desert"),
            "pyramid":  (5,  "🔺", 3, "Pyramid"),
            "oasis":    (10, "🌴", 2, "Oasis"),
            "nile":     (20, "🔵", 1, "Nile"),
            "ruins":    (8,  "🏛️", 2, "Ruins"),
            "plains":   (12, "⬜", 0, "Plains"),
            "savanna":  (10, "🟫", 0, "Savanna"),
        }
    },
    "norse": {
        "label": "The Frozen North",
        "terrains": {
            "tundra":   (30, "❄️", 0, "Tundra"),
            "fjord":    (20, "🌊", 1, "Fjord"),
            "mountain": (20, "⛰️", 3, "Mountain"),
            "forest":   (15, "🌲", 2, "Forest"),
            "longhouse":(5,  "🏠", 2, "Longhouse"),
            "rune_stone":(5, "🗿", 3, "Rune Stone"),
            "plains":   (5,  "⬜", 0, "Plains"),
        }
    },
    "persia": {
        "label": "The Eastern Steppes",
        "terrains": {
            "steppe":   (30, "🌾", 0, "Steppe"),
            "silk_road":(15, "🛣️", 1, "Silk Road"),
            "citadel":  (5,  "🏰", 3, "Citadel"),
            "oasis":    (10, "🌴", 2, "Oasis"),
            "mountain": (15, "⛰️", 3, "Mountain"),
            "bazaar":   (10, "🏪", 1, "Bazaar"),
            "ruins":    (15, "🏛️", 2, "Ruins"),
        }
    },
    "carthage": {
        "label": "The Southern Wilds",
        "terrains": {
            "jungle":   (30, "🌿", 1, "Jungle"),
            "savanna":  (20, "🟫", 0, "Savanna"),
            "lost_city":(5,  "🌆", 3, "Lost City"),
            "swamp":    (15, "🟢", 1, "Swamp"),
            "volcano":  (5,  "🌋", 2, "Volcano"),
            "coast":    (15, "🏖️", 0, "Coast"),
            "plains":   (10, "⬜", 0, "Plains"),
        }
    },
    "greece": {
        "label": "The Western Isles",
        "terrains": {
            "island":   (25, "🏝️", 2, "Island"),
            "agora":    (10, "🏛️", 2, "Agora"),
            "vineyard": (15, "🍇", 1, "Vineyard"),
            "coast":    (20, "🏖️", 0, "Coast"),
            "mountain": (15, "⛰️", 3, "Mountain"),
            "sea":      (15, "🌊", 0, "Sea"),
        }
    },
    "heartland": {
        "label": "The Ancient Heartland",
        "terrains": {
            "plains":   (25, "⬜", 0, "Plains"),
            "forest":   (20, "🌲", 2, "Forest"),
            "mountain": (15, "⛰️", 3, "Mountain"),
            "desert":   (15, "🏜️", 0, "Desert"),
            "ruins":    (10, "🏛️", 2, "Ruins"),
            "oasis":    (5,  "🌴", 2, "Oasis"),
            "nile":     (10, "🔵", 1, "Nile"),
        }
    }
}

# Special wonders that can spawn in new territory
WONDERS = [
    {"name": "The Great Pyramid", "emoji": "🔺", "bonus": "double_attack", "biome": "egypt"},
    {"name": "Valhalla's Gate",   "emoji": "⚡", "bonus": "streak_boost",  "biome": "norse"},
    {"name": "The Silk Throne",   "emoji": "👑", "bonus": "morale_aura",   "biome": "persia"},
    {"name": "Temple of Baal",    "emoji": "🌆", "bonus": "garrison",      "biome": "carthage"},
    {"name": "The Parthenon",     "emoji": "🏛️", "bonus": "scholar",       "biome": "greece"},
    {"name": "The Colossus",      "emoji": "🗿", "bonus": "sea_control",   "biome": "greece"},
]

def _hash(row: int, col: int, seed: int = 42) -> int:
    """Deterministic hash for a coordinate — same world every time."""
    key = f"{seed}:{row}:{col}"
    return int(hashlib.md5(key.encode()).hexdigest(), 16)

def _get_biome(row: int, col: int, bounds: dict, biome_seeds: dict) -> str:
    """Determine which biome a coordinate belongs to based on direction from origin."""
    center_row = (bounds["min_row"] + bounds["max_row"]) / 2
    center_col = (bounds["min_col"] + bounds["max_col"]) / 2

    dr = row - center_row
    dc = col - center_col
    dist = math.sqrt(dr*dr + dc*dc)

    # Heartland = within 3 tiles of center
    if dist < 3:
        return "heartland"

    # Direction determines biome
    if abs(dr) > abs(dc):
        return biome_seeds["north"] if dr < 0 else biome_seeds["south"]
    else:
        return biome_seeds["east"] if dc > 0 else biome_seeds["west"]

def generate_tile(row: int, col: int, bounds: dict, biome_seeds: dict) -> dict:
    """
    Procedurally generate a tile at (row, col).
    Deterministic — same inputs always produce same tile.
    """
    biome_name = _get_biome(row, col, bounds, biome_seeds)
    biome = BIOMES[biome_name]

    h = _hash(row, col)

    # Select terrain from biome weights
    terrains = biome["terrains"]
    total = sum(w for w, *_ in terrains.values())
    r = h % total
    cumulative = 0
    terrain_key = list(terrains.keys())[0]
    for tkey, (weight, emoji, defense, label) in terrains.items():
        cumulative += weight
        if r < cumulative:
            terrain_key = tkey
            break

    weight, emoji, defense, label = terrains[terrain_key]

    # Rare wonder spawn (1 in 40 non-sea tiles)
    is_wonder = (h % 40 == 7) and terrain_key not in ("sea", "fjord")
    wonder = None
    if is_wonder:
        biome_wonders = [w for w in WONDERS if w["biome"] == biome_name]
        if biome_wonders:
            wonder = biome_wonders[h % len(biome_wonders)]

    return {
        "row": row,
        "col": col,
        "terrain": terrain_key,
        "emoji": wonder["emoji"] if wonder else emoji,
        "defense": defense + (2 if wonder else 0),
        "label": wonder["name"] if wonder else label,
        "biome": biome_name,
        "wonder": wonder["name"] if wonder else None,
        "wonder_bonus": wonder["bonus"] if wonder else None,
        "owner": None,
    }

def get_or_generate_tile(state: dict, row: int, col: int) -> dict:
    """Retrieve tile from state or generate it on the fly."""
    key = f"{row},{col}"
    if key not in state["tiles"]:
        state["tiles"][key] = generate_tile(
            row, col,
            state["world_bounds"],
            state["biome_seeds"]
        )
    return state["tiles"][key]

def compute_world_size(player_count: int, faction_count: int) -> tuple:
    """
    Returns (radius) — the world expands outward from origin.
    Formula: radius = max(2, ceil(sqrt(players/2)) + factions)
    Always keeps ~30% frontier unclaimed.
    """
    base = max(2, math.ceil(math.sqrt(max(1, player_count) / 2)))
    faction_bonus = min(faction_count, 8)  # cap influence at 8 factions
    radius = base + faction_bonus
    return radius

def expand_world_if_needed(state: dict) -> bool:
    """
    Check if world should grow. Expand if needed.
    Returns True if world expanded.
    """
    player_count = state["player_count"]
    faction_count = len(state["factions"])
    new_radius = compute_world_size(player_count, faction_count)

    bounds = state["world_bounds"]
    current_radius = (bounds["max_row"] - bounds["min_row"]) // 2

    if new_radius <= current_radius:
        return False

    # Expand bounds
    old_bounds = dict(bounds)
    state["world_bounds"] = {
        "min_row": -new_radius,
        "max_row": new_radius,
        "min_col": -new_radius,
        "max_col": new_radius,
    }

    # Pre-generate edge tiles for the new ring
    new_tiles = 0
    for r in range(-new_radius, new_radius + 1):
        for c in range(-new_radius, new_radius + 1):
            if abs(r) == new_radius or abs(c) == new_radius:
                get_or_generate_tile(state, r, c)
                new_tiles += 1

    _log(state, f"🌍 **The known world expands!** {new_tiles} new territories emerge beyond the frontier. Radius: {new_radius} tiles.")
    return True

def get_visible_tiles(state: dict) -> list:
    """Return all tiles within current world bounds as 2D list."""
    b = state["world_bounds"]
    rows = []
    for r in range(b["min_row"], b["max_row"] + 1):
        row = []
        for c in range(b["min_col"], b["max_col"] + 1):
            tile = get_or_generate_tile(state, r, c)
            row.append(tile)
        rows.append(row)
    return rows

def get_biome_name(state: dict, row: int, col: int) -> str:
    return _get_biome(row, col, state["world_bounds"], state["biome_seeds"])

def _log(state, message):
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    state["event_log"].append(f"`{ts}` — {message}")
    state["event_log"] = state["event_log"][-30:]
