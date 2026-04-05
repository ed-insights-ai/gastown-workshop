# ⛽ Gas Town Workshop

A hands-on workshop for learning Gas Town, a system for orchestrating multiple AI agents to build and ship code.

## What is Gas Town?

Gas Town is a system for coordinating multiple AI agents to design, build, and ship code through structured workflows.

Instead of prompting one model at a time, you:
- Break work into **beads** (small, well-defined units of work)
- Organize them into **convoys** (ordered batches for dispatch)
- Execute them with agents, with full traceability and recovery

This workshop teaches you how to think and operate in that model by building a real project end-to-end.

## What You'll Learn

By the end of this workshop you'll know how to:

- Think in Gas Town's mental model (you'll learn terms like agents, beads, convoys, and molecules)
- Create beads and run them through polecats
- Build dependency chains and parallel work lanes
- Use the full design-to-delivery pipeline (spec → plan → beads → swarm)
- Run a crew session with interactive formula workflows
- Read attribution data and audit what your agents did
- Recover from stalled polecats and broken states

## The Project: `weatherly` 🌦️

You'll build **weatherly**, a CLI weather dashboard in Python. It's small enough to finish in an afternoon but has enough structure to demonstrate everything Gas Town can do:

```
┌────────────────────────────────────────────────────┐
│                    weatherly CLI                   │
├─────────────┬──────────────┬───────────────────────┤
│   fetcher   │   processor  │       display         │
│  (API call) │ (parse JSON) │   (terminal UI)       │
└─────────────┴──────────────┴───────────────────────┘
         ↑                              ↑
    Module 2-3                     Module 4-5
  (dependency                   (full pipeline)
     chains)
```

## Modules

| Module | Topic | Concept |
|--------|-------|---------|
| [0. Mental Model](docs/module-00-mental-model.md) | How Gas Town thinks | Agents, beads, convoys, molecules |
| [1. Idea to Beads](docs/module-01-idea-to-beads.md) | Brief → design → plan | The human layer before the first bead |
| [2. First Bead](docs/module-02-first-bead.md) | Create → sling → done | The core loop |
| [3. Dependency Chain](docs/module-03-dependency-chain.md) | B needs A | Sequential work |
| [4. Parallel Lanes](docs/module-04-parallel-lanes.md) | A, B, C at once | Concurrent work |
| [5. Convoy Launch](docs/module-05-convoy-launch.md) | Stage → launch → watch | Automated dispatch |
| [6. Full Pipeline](docs/module-06-full-pipeline.md) | `mol-idea-to-plan` + `shiny` | Design pipeline + structured execution |
| [7. Recovery & Debugging](docs/module-07-recovery.md) | When things get weird | Stalled polecats, zombies |

## Setup & Reference

| Section | Contents |
|---------|----------|
| [Setup](docs/setup.md) | Full environment setup, shell integration, crew workspace, troubleshooting |
| [Quick Reference](docs/appendix-quick-reference.md) | All key commands in one place |
| [Common Errors](docs/appendix-common-errors.md) | Error messages + fixes |

## Prerequisites

- Gas Town installed (`gt --version` works)
- `bd` and `gt` CLIs in your PATH
- Claude Code authenticated (`claude --version` works)
- **Your own fork of this repo** under an org or account you can push to
- The `gt-sdlc` Claude Code plugin installed (see below)

### Install the gt-sdlc Plugin

This workshop uses the `gt-sdlc` slash commands for the brief → design → plan pipeline in Module 1. Install it once before starting:

Open Claude Code (run `claude` in your terminal), then run these slash commands from within it:

```
/plugin marketplace add https://github.com/danielscholl/claude-sdlc
/plugin install gt-sdlc
```

Verify by running `/gt-sdlc:brief` inside Claude Code. You should see the command prompt.

## Repo Ownership Assumption

This workshop assumes you **fork this repository into your own GitHub org or
personal account** and do the work there.

Why: the tutorial has you creating beads, running polecats, and merging code.
That means your Refinery and polecats need push access to the repo you're using.
If you just clone `claudiogarza/gastown-workshop`, you'll be able to read it but
not push changes back.

Recommended flow:

1. Fork `claudiogarza/gastown-workshop` to your own org/account
2. Use `gt rig add` with your fork URL (Gas Town clones it into its own structure)
3. Let Gas Town push and merge against the fork you control

## Quick Start

If Gas Town is already running, this gets you ready to start the workshop in a few steps.

> 🔧 **Gas Town not installed yet?** → **[Full Setup Guide →](docs/setup.md)**

```bash
# 0. Fork this repo to your own GitHub org/account
# Example (personal account):
#   gh repo fork claudiogarza/gastown-workshop
# Example (org):
#   gh repo fork claudiogarza/gastown-workshop --org YOUR_ORG
# No need to clone. gt rig add handles that.

# 1. Verify Gas Town is running
gt status

# 2. Add a rig pointing at your fork (pick your own rig name)
#   gt rig add workshop https://github.com/YOUR_ORG_OR_USER/gastown-workshop.git \
#     --upstream-url https://github.com/claudiogarza/gastown-workshop

# 3. Verify the rig is registered
gt rig list

# 4. Verify native formulas exist
gt formula list
```

✅ You're ready to start when:
- `gt status` shows Gas Town running (mayor + deacon)
- `gt rig list` shows the rig pointing at your fork
- `gt formula list` includes `mol-idea-to-plan` and `shiny`

**→ [Start with Module 0: The Mental Model →](docs/module-00-mental-model.md)**

If you hit setup issues, check the **[Full Setup Guide →](docs/setup.md)**

---

> 💡 **Tip:** Each module has step-by-step commands to run. **Do them.** Gas Town only makes sense when you watch it move. Reading without doing is half the value.
