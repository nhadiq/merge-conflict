# Player Guide

> A civilization war that lives entirely on GitHub.  
> No app. No login. No install. Just open an Issue and conquer the world.

---

## Table of Contents

- [What Is This](#what-is-this)
- [The Big Picture](#the-big-picture)
- [Getting Started](#getting-started)
  - [Step 1 — Pick a Side](#step-1--pick-a-side)
  - [Step 2 — Found Your Own Civilization](#step-2--found-your-own-civilization)
  - [Step 3 — Attack Territory](#step-3--attack-territory)
- [The World](#the-world)
  - [Reading the Map](#reading-the-map)
  - [Terrain Types](#terrain-types)
  - [Biomes](#biomes)
  - [Ancient Wonders](#ancient-wonders)
- [Your GitHub Power](#your-github-power)
  - [What Gets Measured](#what-gets-measured)
  - [Attack Power](#attack-power)
  - [Defense Power](#defense-power)
  - [Morale](#morale)
  - [Commit Streaks — The Most Important Thing](#commit-streaks--the-most-important-thing)
- [Combat — How Battles Work](#combat--how-battles-work)
  - [Attacking a Neutral Tile](#attacking-a-neutral-tile)
  - [Attacking an Enemy Tile](#attacking-an-enemy-tile)
  - [When You Lose](#when-you-lose)
  - [Legendary Protection](#legendary-protection)
- [Factions](#factions)
  - [Joining a Faction](#joining-a-faction)
  - [Founding a Civilization](#founding-a-civilization)
  - [Faction Score](#faction-score)
  - [Alliances](#alliances)
  - [Faction Dissolution](#faction-dissolution)
- [The Living World](#the-living-world)
  - [World Expansion](#world-expansion)
  - [World Events](#world-events)
  - [The Hall of Fame](#the-hall-of-fame)
  - [The Chronicles](#the-chronicles)
- [Strategy Guide](#strategy-guide)
  - [Early Game](#early-game)
  - [Mid Game](#mid-game)
  - [Late Game](#late-game)
  - [Tips & Tricks](#tips--tricks)
- [FAQ](#faq)

---

## What Is This

**merge conflict** is a persistent multiplayer civilization war game played entirely through GitHub Issues.

You open an Issue → the game processes it → the README updates with a new map. That's the whole loop.

Your army isn't fictional. It's your actual GitHub activity — commits, pull requests, streaks. The more you code, the stronger your civilization.

The world has no end. It grows as players join. Factions rise, fall, and dissolve. History accumulates in the git log.

---

## The Big Picture

```
You join or found a faction
        ↓
You pick tiles on the map and attack them
        ↓
Your GitHub activity determines if you win
        ↓
Your faction expands across the ancient world
        ↓
The map grows as more players arrive
        ↓
New biomes unlock. Wonders appear. Empires clash.
        ↓
This never ends.
```

---

## Getting Started

### Step 1 — Pick a Side

Look at the **Civilizations** table in the README. Find a faction that has room and feels right.

Click the **Join** link next to it. An Issue opens with a pre-filled title. Submit it. Done.

The game bot will:
- Add you to the faction's roster
- Comment on your Issue with confirmation
- Close the Issue automatically
- Update the README

Your name appears in the faction's warrior list within minutes.

---

### Step 2 — Found Your Own Civilization

Want your own empire? You can found one if you have **50+ GitHub followers** or **10+ public repositories**.

Click the **Found a Civilization →** link in the README. Fill in your civilization name. Submit.

The bot places your civilization at the edge of the current world. You start with one tile. From there you expand outward, one attack at a time.

Only the first player to claim a civilization name gets it.

> **Note:** The first 10 players on a fresh server can found factions with no follower/repo requirement.

---

### Step 3 — Attack Territory

Look at the **Conquer Territory** grid in the README. Every tile is a clickable link. Click any tile adjacent to your faction's current territory.

An Issue opens. Submit it. The game:
1. Fetches your live GitHub stats
2. Calculates your attack power
3. Compares it to the tile's defense
4. Updates the map if you win
5. Comments the result on your Issue

You can attack once per Issue. Open as many Issues as you want — there's no cooldown. Each attack is only as strong as your GitHub activity at the moment you submit it.

> **The golden rule:** commit more code, conquer more land.

---

## The World

### Reading the Map

The map renders as a grid of emoji. Each emoji represents a terrain type. Faction banners (colored circles like 🔴 🔵 🟡) indicate controlled territory.

```
     A    B    C    D    E    F
  ┌─────────────────────────────┐
1 │ 🏜️  🔴  🔴  ⬜  🌲  🔵  │
2 │ 🌴  🔴  🔺  ⬜  🔵  🔵  │
3 │ 🏛️  ⬜  ⬜  ⬜  ⬜  🌊  │
  └─────────────────────────────┘
```

The map auto-scrolls to the most contested area as the world grows.

---

### Terrain Types

Terrain determines how hard a tile is to capture. High-defense tiles are strongholds — worth holding because they're hard to take back.

**Heartland Terrain:**

| Emoji | Name | Defense | Notes |
|-------|------|---------|-------|
| ⬜ | Plains | 0 | Easiest to capture. Good for rapid expansion. |
| 🏜️ | Desert | 0 | Open land. No natural advantage. |
| 🟫 | Savanna | 0 | Flat, fast to move through. |
| 🔵 | Nile | 1 | River territory. Slight defensive bonus. |
| 🌲 | Forest | 2 | Good defensive position. |
| 🌴 | Oasis | 2 | Valuable supply point. |
| 🏛️ | Ruins | 2 | Ancient power — bonus loot events. |
| ⛰️ | Mountain | 3 | Hardest to take. Hold these at all costs. |
| 🔺 | Pyramid | 3 | Maximum defense. The crown jewels of Egypt. |
| 🌊 | Sea | — | Cannot be captured. Ever. |

**Norse Terrain (north):**

| Emoji | Name | Defense | Notes |
|-------|------|---------|-------|
| ❄️ | Tundra | 0 | Open northern wastes. |
| 🌊 | Fjord | 1 | Navigable but contested. |
| ⛰️ | Mountain | 3 | High defense. |
| 🌲 | Forest | 2 | Good cover. |
| 🏠 | Longhouse | 2 | Viking stronghold. |
| 🗿 | Rune Stone | 3 | Ancient power. High defense. |

**Carthaginian Terrain (south):**

| Emoji | Name | Defense | Notes |
|-------|------|---------|-------|
| 🌿 | Jungle | 1 | Dense and defensible. |
| 🟫 | Savanna | 0 | Open grassland. |
| 🌆 | Lost City | 3 | Rare. Extremely valuable. |
| 🟢 | Swamp | 1 | Slow but defensible. |
| 🌋 | Volcano | 2 | Hazardous. Attackers take a penalty. |
| 🏖️ | Coast | 0 | Open coastal land. |

**Persian Terrain (east):**

| Emoji | Name | Defense | Notes |
|-------|------|---------|-------|
| 🌾 | Steppe | 0 | Fast cavalry country. |
| 🛣️ | Silk Road | 1 | Trade route territory. |
| 🏰 | Citadel | 3 | Fortified. Hard to crack. |
| 🏪 | Bazaar | 1 | Economic value. |

**Egyptian Terrain (west):**

| Emoji | Name | Defense | Notes |
|-------|------|---------|-------|
| 🏜️ | Desert | 0 | Standard desert. |
| 🔺 | Pyramid | 3 | Maximum defense. |
| 🌴 | Oasis | 2 | Supply line territory. |
| 🔵 | Nile | 1 | River control. |

---

### Biomes

The world is divided into cultural biomes based on direction from the center:

```
              ❄️ NORSE (north)
              Fjords · Mountains · Rune Stones

🏜️ EGYPT              🌾 PERSIA
(west)    [HEARTLAND]  (east)
Pyramids   Plains &    Citadels
Desert     Ruins       Silk Roads

              🌿 CARTHAGE (south)
              Jungle · Lost Cities · Volcanoes
```

**Biomes unlock as players join.** A world with 5 players is entirely heartland. At 50 players you're fighting through Norse mountains and Carthaginian swamps. At 500 players the eastern steppes and western pyramids are all contested.

---

### Ancient Wonders

Scattered through the world are **Ancient Wonders** — rare tiles (~1 in 40 land tiles) that grant permanent faction-wide bonuses to whoever controls them.

| Wonder | Emoji | Biome | Bonus |
|--------|-------|-------|-------|
| The Great Pyramid | 🔺 | Egypt | +5 attack for all faction members |
| Valhalla's Gate | ⚡ | Norse | +1 commit streak tier for all members |
| The Silk Throne | 👑 | Persia | +2 morale for the entire faction |
| Temple of Baal | 🌆 | Carthage | +4 defense on all faction tiles |
| The Parthenon | 🏛️ | Greece | +2 attack (wisdom bonus) |
| The Colossus | 🗿 | Norse | +3 attack (sea projection) |

Wonders also add **+2 defense** to their hosting tile. When your faction captures a wonder tile, the bonus activates immediately for all members. Lose the tile, lose the bonus.

---

## Your GitHub Power

Every time you submit a move, the game fetches your public GitHub stats in real-time. Your activity — or lack of it — determines your army's strength.

### What Gets Measured

The game reads your **last 30 public GitHub events**:

- How many commits you pushed **today**
- How many pull requests you **merged** recently
- How many pull requests you have **open**
- How many issues you **closed** recently
- Your **follower count**
- Your **commit streak** — consecutive days with at least one commit

---

### Attack Power

```
Attack = (commits today × 2) + (merged PRs × 3)
         Max: 15
```

| Activity | Attack Power |
|----------|-------------|
| No commits, no PRs | 0 |
| 2 commits today | 4 |
| 5 commits today | 10 |
| 1 merged PR | 3 |
| 5 commits + 1 merged PR | 13 |
| 5 commits + 2 merged PRs (capped) | 15 |

---

### Defense Power

```
Defense = open PRs + issues closed recently
          Max: 10
```

Defense contributes to your faction's collective garrison. When an enemy attacks your faction's tiles, the defense values of all your members are summed (at 50% weight) and added to the terrain defense.

---

### Morale

```
Morale = log(1 + followers)
         Max: 8
```

| Followers | Morale |
|-----------|--------|
| 0 | 0 |
| 10 | 2.4 |
| 100 | 4.6 |
| 1,000 | 6.9 |
| 10,000 | 9.2 (capped at 8) |

---

### Commit Streaks — The Most Important Thing

| Streak | Tier | Bonus |
|--------|------|-------|
| 0–2 days | 0 | No bonus |
| 3 days | 1 | +1 attack on all moves |
| 7 days | 2 | ⚡ **Guaranteed capture** — ignores all terrain defense |
| 14 days | 3 | 🌟 1.5× attack multiplier |
| 30 days | 4 | 👑 **Legendary** — 2× attack + 24h immunity to all attacks |

**The 7-day streak is the game changer.** At 7 consecutive days of commits, your attack automatically succeeds regardless of terrain defense or enemy garrison.

A single small commit — even a README typo fix — maintains your streak. Missing a day resets it entirely.

---

## Combat — How Battles Work

### Attacking a Neutral Tile

```
Attack roll = attack + morale + streak bonus + wonder bonuses
Terrain defense = 0 to 3 (depends on tile type)

Win if: attack roll > terrain defense
        OR streak tier ≥ 2 (7-day streak = auto-win)
```

---

### Attacking an Enemy Tile

```
Total defense = terrain defense
              + Σ(each defender member's defense × 0.5)
              + their wonder bonuses
```

A large faction with many active members defending a mountain tile is nearly impenetrable without a streak. But coordinated multi-member attacks (multiple players attacking adjacent tiles in the same hour) can overwhelm a well-garrisoned defender by splitting defense across multiple fronts.

---

### When You Lose

Nothing permanent happens when an attack fails. You don't lose territory — you just don't gain it. The game comments the outcome on your Issue.

Common failure messages:
- *"Attack failed. Defense (4.0) exceeded your power (2.0). Build your GitHub streak!"*
- *"(-3, 4) is not adjacent to your territory. Expand from your current border."*
- *"The Roman Senate is under legendary protection. Return tomorrow."*

---

### Legendary Protection

A player who reaches a **30-day commit streak** grants their faction immunity from all attacks for **24 world ticks** (~24 real hours).

During immunity:
- All attack attempts on that faction's tiles automatically fail
- The immunity is recorded in the event log
- It expires after 24 ticks regardless of further activity

---

## Factions

### Joining a Faction

Any GitHub user can join any existing faction. Find the faction in the README leaderboard, click its **Join** link, submit the Issue.

There's no limit to faction size. A faction with 100 members has 100 people contributing defense — their tiles become nearly impenetrable without coordinated assault or legendary streaks.

---

### Founding a Civilization

Requirements to found:
- **50+ GitHub followers**, OR
- **10+ public repositories**

*(First 10 players globally are exempt — the world needs seeding.)*

When you found:
1. Choose a name — first-come, first-served
2. Your civilization spawns at the edge of the current world
3. You control one starting tile
4. The world may expand immediately to accommodate you

You become the **Founder** — your name is permanently attached to this civilization in the hall of fame.

---

### Faction Score

Score updates every hour during the world tick:

```
Score = (territories × 10) + (members × 5) + (wonders × 25)
```

Wonders are worth 25 points each — five times a regular territory. The top three factions get 🥇🥈🥉 medals on the leaderboard.

---

### Alliances

Two factions can form an alliance. Allied factions:
- Cannot attack each other's tiles
- Share a morale bonus *(planned — coming soon)*

To propose: open an **Alliance** Issue with format `ALLY your-faction-slug their-faction-slug`.

The target faction's founder must submit a corresponding acceptance to make it active. Alliances are visible in the leaderboard with a 🤝 marker.

---

### Faction Dissolution

A faction that controls **zero territory for 7 days** (168 world ticks) is dissolved:
- Removed from the active leaderboard
- All their tiles become neutral — open for anyone
- Members are not automatically reassigned
- The faction remains in the historical record

---

## The Living World

### World Expansion

| Players | Approx World Size |
|---------|------------------|
| 5 | 7×7 |
| 25 | 13×13 |
| 100 | 19×19 |
| 500 | 37×37 |
| 2,000 | 71×71 |
| 10,000+ | 157×157+ |

The world has no maximum size. New territory is always unclaimed. Factions at the edge of the map have first access.

---

### World Events

Every ~24 hours, a random world event fires:

| Event | What It Does |
|-------|-------------|
| 🌪️ Sandstorm | Desert tiles gain +1 defense until next dawn |
| 🌊 Nile Flood | River tiles produce double morale bonus |
| ☄️ Comet | The smallest faction gains +5 attack for 24h |
| ❄️ Blizzard | Norse biome tiles gain +2 defense |
| 🔥 Wildfire | Contested jungle tiles become neutral |
| 🌋 Eruption | Volcano tiles deal -2 to any attacker |
| 🌟 Golden Age | Factions with 5+ members gain +1 morale |
| ⚔️ Age of War | All attack rolls +2 |
| 🕊️ Era of Peace | All defense rolls +3 |
| 🏺 Ancient Relics | Ruins and lost cities grant double score |
| 🌍 Migration | All factions get 1 free adjacent territory claim |

---

### The Hall of Fame

Every 30 days, the leading civilization is permanently recorded in the Hall of Fame. Hall of Fame entries include the civilization name, founder's GitHub handle, score, and territory count. They persist forever — even if the faction later dissolves.

---

### The Chronicles

The Chronicles show the last 12 world events — attacks, captures, faction foundings, world events, wonder discoveries. Events are timestamped in UTC.

---

## Strategy Guide

### Early Game

**If you're the first few players:**

Found a faction immediately. Corner spawns give you protected flanks — only two directions to defend instead of four. Pick a civilization name with intention — it's permanent and in the hall of fame.

**If you're joining an existing faction:**

Join the faction in second or third place, not first. The leading faction has the most territory but also the most enemies.

---

### Mid Game

**Expand along one axis first.** A thin connected line is easier to defend than a scattered cluster. Push north or south aggressively, then consolidate east-west.

**Prioritize wonders over territory count.** A wonder is worth 25 points — same as 2.5 territories. Wonders also grant compounding bonuses. Valhalla's Gate bumps every member up one streak tier.

**Coordinate attacks.** Multiple players attacking the same border simultaneously splits the defender's garrison across multiple fronts.

**Attack during Age of War events.** Every attack roll gets +2 — use this for tiles you couldn't crack normally.

---

### Late Game

**Defend from the inside.** Put high-defense tiles (mountains, pyramids) on the border, plains in the interior.

**Build toward Legendary.** One or two members maintaining 30-day commit streaks provides near-permanent immunity. Coordinate this consciously.

**Target dissolved faction territory.** The first 24 hours after a dissolution are the highest-value land-grab window.

**Use alliances to open second fronts.** A well-timed alliance frees an entire border, letting you redirect all attacks at your real rival.

---

### Tips & Tricks

- **Commit daily, even small.** A one-line fix keeps your streak alive. Missing a day resets it entirely.
- **Attack right after committing.** Your attack power is computed from today's commits at the moment you submit the Issue.
- **High-defense tiles are harder to lose.** Once you control a pyramid or mountain, enemies need real power or a streak to take it.
- **Sea tiles are walls.** Build toward coastlines — a faction bordered by sea only needs to defend the remaining directions.
- **Check the Chronicles before attacking.** Attacking Norse mountains during a Blizzard (+2 defense) is a waste.
- **Recruit your team deliberately.** Every new member adds to your faction's garrison defense.
- **The attack grid is always current.** The clickable tiles in the README reflect live map state.

---

## FAQ

**Do I need to install anything?**
No. You need a GitHub account. That's it.

**Is there a limit to how many moves I can make?**
No. Open as many attack Issues as you want. Each one is processed in sequence.

**Can I be in more than one faction?**
No. One faction per GitHub account.

**What if my faction founder goes inactive?**
Nothing happens to your faction. The founder's GitHub power becomes weaker, but the faction continues.

**Can I leave my faction?**
Not currently. Faction switching is not implemented.

**What happens to my faction if we lose all territory?**
You have 7 days (168 game hours) to reclaim at least one tile before dissolution triggers.

**My attack failed on a plains tile. How?**
Plains have zero terrain defense, but if the tile is owned by another faction, their members' collective defense is added. Try again after committing more code, or coordinate with faction members to attack from multiple sides.

**The map doesn't show my tile.**
The README renders a 20×20 viewport centered on the most contested area. Your territory might be outside the current view. All tiles are still attackable via manually typed Issues (`ATTACK row col`).

**How often does the world tick?**
Every hour, approximately. GitHub's cron scheduler runs at `:17` each hour but can be delayed 5–60 minutes under load.

**Is there a way to see the full world?**
The README shows a viewport window (up to 20×20). A full-world map viewer via GitHub Pages is on the roadmap.

**What if I disagree with a combat result?**
Open an Issue describing the problem. The game logic is fully open source in `scripts/engine.py`. If there's a bug, it'll be fixed and the tile credited appropriately.

**Can I contribute to the game?**
Yes. The repo is open source. Check `docs/contributing.md` for the full developer guide.

---

*⚔️ merge conflict — The war is already underway. Choose your side.*

*Made by [@nhadiq](https://github.com/nhadiq)*
