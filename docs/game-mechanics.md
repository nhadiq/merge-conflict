# Game Mechanics

---

## World Expansion Formula

```
radius = max(2, ceil(sqrt(player_count / 2))) + min(faction_count, 8)
```

| Players | Approx Radius | World Size |
|---------|--------------|------------|
| 1–4 | 3 | 7×7 |
| 10 | 5 | 11×11 |
| 50 | 7 | 15×15 |
| 100 | 9 | 19×19 |
| 500 | 18 | 37×37 |
| 1,000 | 25 | 51×51 |
| 10,000 | 78 | 157×157 |

Expansion fires after every player action and on every world tick.

---

## Biome System

Biome assignment is based on direction from world center:

```
distance < 3 tiles from center  →  heartland
north (|dr| > |dc|, dr < 0)    →  biome_seeds["north"]  (default: norse)
south (|dr| > |dc|, dr > 0)    →  biome_seeds["south"]  (default: carthage)
east  (|dc| > |dr|, dc > 0)    →  biome_seeds["east"]   (default: persia)
west  (|dc| > |dr|, dc < 0)    →  biome_seeds["west"]   (default: egypt)
```

### Heartland

| Terrain | Weight | Emoji | Defense |
|---------|--------|-------|---------|
| Plains | 25 | ⬜ | 0 |
| Forest | 20 | 🌲 | 2 |
| Mountain | 15 | ⛰️ | 3 |
| Desert | 15 | 🏜️ | 0 |
| Ruins | 10 | 🏛️ | 2 |
| Oasis | 5 | 🌴 | 2 |
| Nile | 10 | 🔵 | 1 |

### Norse (north)

| Terrain | Weight | Emoji | Defense |
|---------|--------|-------|---------|
| Tundra | 30 | ❄️ | 0 |
| Fjord | 20 | 🌊 | 1 |
| Mountain | 20 | ⛰️ | 3 |
| Forest | 15 | 🌲 | 2 |
| Longhouse | 5 | 🏠 | 2 |
| Rune Stone | 5 | 🗿 | 3 |
| Plains | 5 | ⬜ | 0 |

### Carthage (south)

| Terrain | Weight | Emoji | Defense |
|---------|--------|-------|---------|
| Jungle | 30 | 🌿 | 1 |
| Savanna | 20 | 🟫 | 0 |
| Lost City | 5 | 🌆 | 3 |
| Swamp | 15 | 🟢 | 1 |
| Volcano | 5 | 🌋 | 2 |
| Coast | 15 | 🏖️ | 0 |
| Plains | 10 | ⬜ | 0 |

### Persia (east)

| Terrain | Weight | Emoji | Defense |
|---------|--------|-------|---------|
| Steppe | 30 | 🌾 | 0 |
| Silk Road | 15 | 🛣️ | 1 |
| Citadel | 5 | 🏰 | 3 |
| Oasis | 10 | 🌴 | 2 |
| Mountain | 15 | ⛰️ | 3 |
| Bazaar | 10 | 🏪 | 1 |
| Ruins | 15 | 🏛️ | 2 |

### Egypt (west)

| Terrain | Weight | Emoji | Defense |
|---------|--------|-------|---------|
| Desert | 35 | 🏜️ | 0 |
| Pyramid | 5 | 🔺 | 3 |
| Oasis | 10 | 🌴 | 2 |
| Nile | 20 | 🔵 | 1 |
| Ruins | 8 | 🏛️ | 2 |
| Plains | 12 | ⬜ | 0 |
| Savanna | 10 | 🟫 | 0 |

---

## Faction Score

Score updates every hour during the world tick:

```
Score = (territories × 10) + (members × 5) + (wonders × 25)
```

Wonders are worth 25 points each — five times a regular territory. The top three factions get 🥇🥈🥉 medals on the leaderboard.

---

## Faction Formation Rules

A player can found a faction if **either** condition is true:
- `followers >= 50`
- `public_repos >= 10`

This gate is waived for the first 10 players globally.

Faction slugs: lowercase, non-alphanumeric → `-`, truncated at 24 characters. The banner pool has **24 distinct options** and cycles if exceeded.

---

## Combat Resolution

```
attack_roll  = (commits_today × 2) + (prs_merged × 3) + morale
             + streak_tier_bonuses + wonder_attack_bonuses

defense_roll = terrain_defense
             + Σ(defender_member.gh_power.defense × 0.5)
             + wonder_defense_bonuses

success = attack_roll > defense_roll
        OR streak_tier >= 2  (7-day streak = guaranteed capture)
```

**Adjacency requirement:** Target must be orthogonally adjacent to at least one tile owned by the attacker's faction.

**Immunity:** A 30-day streak grants `immune_{faction_slug}` = `world_age + 24`. Attacks on immune factions fail immediately.

### Streak Tier Bonuses

| Tier | Streak | Bonus |
|------|--------|-------|
| 1 | 3 days | +1 attack |
| 2 | 7 days | +3 attack + guaranteed capture |
| 3 | 14 days | ×1.5 attack multiplier |
| 4 | 30 days | ×2 attack multiplier + 24h immunity |

---

## GitHub Power Calculation

```python
attack  = min(15, commits_today * 2 + prs_merged * 3)
defense = min(10, prs_open + issues_closed)
morale  = min(8, log(1 + followers))
```

All values are capped. Morale uses log scale to prevent follower domination.

---

## Wonder System

**Spawn probability:** `hash(row, col) % 40 == 7` — ~2.5% of land tiles.

Wonders add **+2 defense** to their hosting tile in addition to the faction-wide bonus.

| Wonder | Emoji | Bonus Key | Effect |
|--------|-------|-----------|--------|
| The Great Pyramid | 🔺 | `double_attack` | +5 attack for all members |
| Valhalla's Gate | ⚡ | `streak_boost` | +1 streak tier for all members |
| The Silk Throne | 👑 | `morale_aura` | +2 morale faction-wide |
| Temple of Baal | 🌆 | `garrison` | +4 defense on all faction tiles |
| The Parthenon | 🏛️ | `scholar` | +2 attack |
| The Colossus | 🗿 | `sea_control` | +3 attack |

Wonders are biome-specific. Control changes when the hosting tile changes ownership.

---

## Alliance System

Proposed via `ALLY slug-a slug-b` Issue. Target faction's founder must submit a corresponding acceptance Issue to activate.

Active alliances:
- Factions cannot attack each other's tiles
- Share morale bonus: `+0.5 morale` per active alliance *(planned, not yet implemented)*

---

## Faction Dissolution

A faction with zero territories for `168 world_age ticks` (≈ 7 days) is marked `dissolved: true`. Their tiles become neutral. Dissolved factions remain in `state.factions` for historical record.

---

## Hall of Fame

Every 30 days, the leading civilization is permanently recorded in the Hall of Fame (`state.hall_of_fame`). Entries include civilization name, founder's GitHub handle, score, and territory count. They persist forever, even if the faction later dissolves.

---

## The Chronicles

`event_log` in `state.json` stores the last 12 world events — attacks, captures, faction foundings, world events, wonder discoveries. Events are timestamped in UTC. The renderer displays these as the event chronicle in the README.

---

## World Events

Fires every 24 ticks (~once per real-world day). Selected randomly from 11 events.

| Event | Effect |
|-------|--------|
| 🌪️ Sandstorm | Desert tiles +1 defense |
| 🌊 Nile Flood | River tiles double morale bonus |
| ☄️ Comet | Smallest faction +5 attack for 24h |
| ❄️ Blizzard | Norse biome tiles +2 defense |
| 🔥 Wildfire | Contested jungle tiles become neutral |
| 🌋 Eruption | Volcano tiles -2 to any attacker |
| 🌟 Golden Age | Factions with 5+ members +1 morale |
| ⚔️ Age of War | All attack rolls +2 |
| 🕊️ Era of Peace | All defense rolls +3 |
| 🏺 Ancient Relics | Ruins and lost cities grant double score |
| 🌍 Migration | All factions get 1 free adjacent claim |

> Note: Events are logged but not all mechanical effects are fully implemented yet. See `roadmap.md`.
