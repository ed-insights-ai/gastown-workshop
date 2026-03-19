# ⛽ Gas Town Workshop

A hands-on tutorial for learning Gas Town — the multi-agent orchestration layer for AI coding workflows.

## What You'll Learn

By the end of this workshop you'll know how to:

- Think in Gas Town's mental model (agents, beads, convoys, molecules)
- Create beads and run them through polecats
- Build dependency chains and parallel work lanes
- Use the full design-to-delivery pipeline (spec → plan → beads → swarm)
- Run a crew session with interactive formula workflows
- Read attribution data and audit what your agents did
- Recover from stalled polecats and broken states

## The Project: `weatherly` 🌦️

You'll build **weatherly** — a CLI weather dashboard in Python. It's small enough to finish in an afternoon but has enough structure to demonstrate everything Gas Town can do:

```
┌─────────────────────────────────────────────────────┐
│                    weatherly CLI                    │
├─────────────┬──────────────┬───────────────────────┤
│   fetcher   │   processor  │       display          │
│  (API call) │ (parse JSON) │   (terminal UI)        │
└─────────────┴──────────────┴───────────────────────┘
         ↑                              ↑
    Module 2-3                     Module 4-5
  (dependency                   (full pipeline)
     chains)
```

## Modules

| Module | Topic | Concept |
|--------|-------|---------|
| [Setup](docs/setup.md) | Get your town running | `gt up`, rig setup, crew workspace |
| [0. Mental Model](docs/module-00-mental-model.md) | How Gas Town thinks | Agents, beads, convoys, molecules |
| [1. First Bead](docs/module-01-first-bead.md) | Create → sling → done | The core loop |
| [2. Dependency Chain](docs/module-02-dependency-chain.md) | B needs A | Sequential work |
| [3. Parallel Lanes](docs/module-03-parallel-lanes.md) | A, B, C at once | Concurrent work |
| [4. Convoy Launch](docs/module-04-convoy-launch.md) | Stage → launch → watch | Automated dispatch |
| [5. Full Pipeline](docs/module-05-full-pipeline.md) | spec → plan → beads → swarm | The whole thing |
| [6. Recovery](docs/module-06-recovery.md) | When it breaks | Stalled polecats, zombies |

## Prerequisites

- Gas Town installed (`gt --version` works)
- `bd` and `gt` CLIs in your PATH
- Claude Code authenticated (`claude --version` works)
- A rig configured (`gt rig list` shows at least one)

## Quick Start

```bash
# 1. Go to your Gas Town root
cd ~/gt

# 2. Bring up all services
gt up

# 3. Verify everything is running
gt status

# 4. Start with Setup
```

**→ [Start with Setup →](docs/setup.md)**

---

> 💡 **Tip:** Each module has step-by-step commands to run. **Do them.** Gas Town only makes sense when you watch it move — reading without doing is half the value.
