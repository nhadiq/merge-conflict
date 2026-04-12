# realm-v2 — Documentation Index

This folder is the **single source of truth** for all technical documentation about the project.

> **Rule for all contributors and AI agents:** Always read the relevant docs here before making any code changes. All updates to architecture, mechanics, or conventions must be reflected here.

---

## Documents

| File | Description |
|------|-------------|
| [architecture.md](./architecture.md) | System architecture, data flow, repository structure |
| [state-schema.md](./state-schema.md) | Full `state.json` schema with field descriptions and full example |
| [game-mechanics.md](./game-mechanics.md) | World gen, combat, biomes, wonders, alliances, events, scoring |
| [scripts.md](./scripts.md) | Each Python script's role, inputs, and outputs |
| [workflows.md](./workflows.md) | GitHub Actions workflows, concurrency, cron timing |
| [contributing.md](./contributing.md) | How to run locally, add biomes, wonders, events, actions |
| [roadmap.md](./roadmap.md) | Planned features, known limitations, scaling notes |
| [player-guide.md](./player-guide.md) | Player-facing guide — how to play, strategy, FAQ |

---

## Update Policy

When you change code that affects any of the following, **update the relevant doc file in this folder**:

- State schema fields → update `state-schema.md`
- Game mechanics or formulas → update `game-mechanics.md`
- Scripts (new functions, changed behavior) → update `scripts.md`
- Workflows (new steps, env vars) → update `workflows.md`
- New contribution patterns → update `contributing.md`
- New planned features or resolved limitations → update `roadmap.md`
- GitHub Pages UI changes → edit `web/index.template.html` (never edit `web/index.html` directly)
