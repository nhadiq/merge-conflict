# Roadmap & Known Limitations

---

## Roadmap

### Near-term (good first issues)

- [ ] Implement mechanical effects for all 11 world events (currently logged but not applied)
- [ ] Alliance acceptance flow (second Issue confirms alliance)
- [ ] Player profile pages (linked from the leaderboard)
- [ ] Tile history — track which factions have controlled each tile
- [ ] `SCOUT row col` action — reveal adjacent tiles without claiming

### Medium-term

- [ ] Trade routes — connect two tiles your faction controls for score bonus
- [ ] Siege mechanics — multi-move captures for high-defense tiles
- [ ] Diplomatic messages — Issue body parsed for flavor text
- [ ] Faction color customization — founder chooses banner emoji from approved set
- [ ] GitHub Pages companion site with a rendered map at any zoom level

### Long-term

- [ ] State sharding for 10,000+ player scale
- [ ] Season snapshots — periodic hall-of-fame entries even without 30-day milestones
- [ ] Spectator mode — GitHub Discussions as a war council channel
- [ ] Multi-repo federation — allied repos share map state via Actions artifacts

---

## Known Limitations

**GitHub cron is not precise.** The hourly tick runs at approximately `:17` but can be delayed 5–60 minutes under GitHub load. Nothing breaks if ticks are late or skipped.

**Scheduled workflows disable after 60 days of inactivity.** If no Issues are opened for 60 days, the cron stops. A `workflow_dispatch` run re-enables it.

**README rendering limit.** GitHub clips rendered READMEs at 512 KB. Very large worlds with full attack grids may exceed this. The viewport clipping (`MAX_RENDER_SIZE = 20`) mitigates this for most cases.

**`state.json` grows unboundedly.** The `tiles` object grows by one entry per unique tile ever touched. At 10,000+ tiles this becomes a meaningful file size. Planned mitigation: move tiles to a separate sharded file.

**GitHub API public events only cover the last 30 events.** Very active developers (100+ public events/day) may have stats slightly undercounted.

**No authentication beyond GitHub identity.** A player's GitHub username is trusted as-is from `github.event.issue.user.login`. This is secure against spoofing, but a bad actor could create a GitHub account specifically to game stats. The 50-follower / 10-repo founding gate partially mitigates this.

---

## Scaling Considerations

**At ~1,000 players:**
- `state.json` size: approximately 2–4 MB (tiles dominate)
- Actions runs per day: 100–500 realistic
- GitHub API calls: 2 per move (within rate limits)
- README size: large but renderable

**At ~10,000 players:**
- `state.json` may exceed 20 MB — approach git's recommended file size limit
- Consider moving `tiles` to a separate `tiles.json` or sharding by quadrant
- README attack grid becomes too large to render — implement a web-based map viewer

**Mitigation options:**
- Shard `tiles.json` into quadrant files (`tiles_NW.json`, etc.)
- Move state to a free Supabase or PlanetScale instance (defeats zero-infra philosophy but enables true scale)
- Render a static site via GitHub Pages instead of the README
