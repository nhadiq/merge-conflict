# State Schema

`state.json` is the single source of truth. It is committed to the repo on every move. There is no external database.

---

## Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `version` | int | Schema version (currently `2`) |
| `world_age` | int | Increments every hourly tick |
| `last_updated` | string | ISO timestamp of last write |
| `player_count` | int | Total registered players |
| `faction_count` | int | Total active factions |
| `world_bounds` | object | Current map extents (`min_row`, `max_row`, `min_col`, `max_col`) |
| `biome_seeds` | object | Direction → biome name mapping |
| `factions` | object | Keyed by faction slug |
| `players` | object | Keyed by GitHub username |
| `tiles` | object | Keyed by `"{row},{col}"` |
| `alliances` | object | Keyed by `"{slug-a}+{slug-b}"` |
| `event_log` | array | Formatted log strings for recent events |
| `hall_of_fame` | array | Records of dissolved/notable factions |
| `wonders` | object | Wonder state (currently sparse) |
| `immune_{slug}` | int | `world_age` tick until which the faction is immune |

---

## Faction Object

```jsonc
"sons-of-the-nile": {
  "name": "Sons of the Nile",           // Display name
  "slug": "sons-of-the-nile",           // URL-safe identifier
  "founder": "naeem",                   // GitHub username
  "banner": "🔴",                       // Emoji identifier
  "members": ["naeem", "dev1"],         // GitHub usernames
  "power": {
    "attack": 9,
    "defense": 3,
    "morale": 4.2,
    "streak": 8,
    "streak_tier": 2
  },
  "territories": [[-2, -2], [-2, -1]], // [row, col] pairs
  "score": 30,
  "founded_age": 0,                     // world_age when founded
  "dissolved": false,
  "alliances": [],                      // Active alliance slugs
  "last_territory_age": 0              // world_age of last territory change
}
```

---

## Player Object

```jsonc
"naeem": {
  "faction": "sons-of-the-nile",
  "role": "founder",                   // "founder" | "warrior"
  "joined_age": 0,
  "moves": 3,
  "gh_power": { ... }                  // Last fetched GitHub power stats
}
```

---

## Tile Object

```jsonc
"-2,-2": {
  "row": -2,
  "col": -2,
  "terrain": "desert",
  "emoji": "🏜️",
  "defense": 0,
  "label": "Desert",
  "biome": "egypt",
  "wonder": null,                      // Wonder name or null
  "wonder_bonus": null,                // Bonus key or null
  "owner": "sons-of-the-nile"          // Faction slug or null
}
```

**Tile key format:** `"{row},{col}"` — signed integers, comma-separated. Example: `"-3,7"`, `"0,0"`, `"12,-5"`.

---

## Alliance Object

```jsonc
"sons-of-the-nile+iron-legion": {
  "status": "proposed",               // "proposed" | "active"
  "from": "sons-of-the-nile",
  "to": "iron-legion"
}
```

---

## Hall of Fame Entry

```jsonc
{
  "age": 720,
  "faction": "Sons of the Nile",
  "banner": "🔴",
  "founder": "naeem",
  "score": 420,
  "territories": 38
}
```

---

## Biome Seeds

```jsonc
"biome_seeds": {
  "north": "norse",
  "south": "carthage",
  "east":  "persia",
  "west":  "egypt"
}
```

Can be customized per-deployment to change the directional biome assignments.

---

## Full Example

```jsonc
{
  "version": 2,
  "world_age": 0,
  "last_updated": "",
  "player_count": 0,
  "faction_count": 0,

  "world_bounds": {
    "min_row": -2, "max_row": 2,
    "min_col": -2, "max_col": 2
  },

  "biome_seeds": {
    "north": "norse",
    "south": "carthage",
    "east":  "persia",
    "west":  "egypt"
  },

  "factions": {
    "sons-of-the-nile": {
      "name": "Sons of the Nile",
      "slug": "sons-of-the-nile",
      "founder": "naeem",
      "banner": "🔴",
      "members": ["naeem", "dev1"],
      "power": { "attack": 9, "defense": 3, "morale": 4.2, "streak": 8, "streak_tier": 2 },
      "territories": [[-2, -2], [-2, -1]],
      "score": 30,
      "founded_age": 0,
      "dissolved": false,
      "alliances": [],
      "last_territory_age": 0
    }
  },

  "players": {
    "naeem": {
      "faction": "sons-of-the-nile",
      "role": "founder",
      "joined_age": 0,
      "moves": 3,
      "gh_power": { "attack": 9, "defense": 3, "morale": 4.2, "streak": 8, "streak_tier": 2 }
    }
  },

  "tiles": {
    "-2,-2": {
      "row": -2, "col": -2,
      "terrain": "desert",
      "emoji": "🏜️",
      "defense": 0,
      "label": "Desert",
      "biome": "egypt",
      "wonder": null,
      "wonder_bonus": null,
      "owner": "sons-of-the-nile"
    }
  },

  "alliances": {
    "sons-of-the-nile+iron-legion": {
      "status": "proposed",
      "from": "sons-of-the-nile",
      "to": "iron-legion"
    }
  },

  "event_log": [
    "`2026-04-12 10:00 UTC` — 🏛️ **Sons of the Nile** rises! Founded by @naeem 🔴"
  ],

  "hall_of_fame": [
    {
      "age": 720,
      "faction": "Sons of the Nile",
      "banner": "🔴",
      "founder": "naeem",
      "score": 420,
      "territories": 38
    }
  ],

  "wonders": {},
  "immune_sons-of-the-nile": 745
}
```
