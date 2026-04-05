# Module 0: The Mental Model

> **Goal:** Understand how Gas Town thinks before touching a single command.

You won't run any commands in this module. You'll build a mental model of how Gas Town works so everything in later modules makes sense.

---

## The Core Idea

Gas Town is a **steam engine**. You don't run code directly. You put *work items* on a conveyor belt, and agents pick them up and run them. The key insight:

> Every action is attributed. Every agent has a track record. Every piece of work has provenance.

This isn't just tracking. It's the foundation for routing, debugging, and quality measurement at scale.

---

## The Vocabulary

Before anything else, get familiar with these five core terms:

### 🪨 Bead
A unit of work. Like a GitHub issue, but richer: it has type, priority, acceptance criteria, dependencies, and attribution. Beads live in a **Dolt** (version-controlled SQL) database.

```
Bead: edi-042
  Title: "Add weather fetcher module"
  Type: task
  Priority: P2
  Status: open → in_progress → closed
  created_by: edinsights_ui/crew/claudio
```

### 🦡 Polecat
An **ephemeral worker**. Think: a Claude Code session in a git worktree that picks up one bead, does the work, and destroys itself. Polecats don't wait around. When they're done, they're gone.

```
Polecat: Toast
  Rig: edinsights_ui
  Status: Working
  Hook: edi-042 (Add weather fetcher module)
  Sandbox: ~/gt/edinsights_ui/polecats/Toast/
```

### 🚚 Convoy
A **tracking unit** for batched work. When you kick off multiple related beads, a convoy lets you see them all in one place and get notified when they all land.

### 🧪 Molecule
A **structured workflow**: a formula that defines multiple steps with dependencies. Think of it like a mini pipeline: instead of a polecat just getting "do this task," it gets "do step 1, then step 2, then step 3." The molecule tracks progress through the steps.

### 👤 Crew
A **persistent human workspace**. Your git clone where you (or an AI acting as you) do exploratory work, run interactive pipelines, and make judgment calls.

---

## The Role Hierarchy

```
                    ┌─────────┐
                    │  Mayor  │  ← Global coordinator, cross-rig decisions
                    └────┬────┘
                         │
                    ┌────┴────┐
                    │ Deacon  │  ← Background daemon, watchdog, spawns Dogs
                    └────┬────┘
              ┌──────────┴──────────┐
         ┌────┴────┐           ┌────┴────┐
         │ Witness │           │Refinery │  ← Per-rig
         └────┬────┘           └────┬────┘
              │                     │
         (watches)            (merges PRs)
              │
    ┌─────────┼──────────┐
    │         │          │
┌───┴──┐  ┌──┴───┐  ┌──┴───┐
│Toast │  │Furio.│  │ Nux  │  ← Polecats (ephemeral workers)
└──────┘  └──────┘  └──────┘

         ┌──────────┐
         │  claudio │  ← Crew (persistent, human-managed)
         └──────────┘
```

**Who does what:**
- **Mayor** — coordinates across rigs, receives escalations
- **Deacon** — background Go daemon, health checks every 3 minutes, manages Dogs
- **Witness** — watches polecats in one rig, nudges stalled ones, respawns crashed ones
- **Refinery** — processes the merge queue, merges polecat branches to main
- **Polecat** — does actual work, ephemeral (Toast, Furiosa, Nux are pool names)
- **Crew** — persistent workspace for you/me (claudio)
- **Dog** — Deacon's infrastructure helpers, NOT for user work

---

## Crew vs Polecats: The Critical Distinction

| | Crew | Polecat |
|--|------|---------|
| **Lifecycle** | Persistent, you control it | Transient, Witness controls it |
| **Git** | Full clone, pushes to main | Worktree on a branch, Refinery merges |
| **Work** | Human-directed, exploratory | Slung via `gt sling`, discrete tasks |
| **Monitoring** | None (you're watching) | Witness watches and nudges |
| **When to use** | Interactive pipelines, long-running, needs judgment | Well-defined tasks, batch work, parallelizable |

**Mental model:** Crew is where *you* work. Polecats are disposable workers you throw tasks at.

---

## The Propulsion Principle

This is the most important rule in Gas Town:

> **If you find something on your hook, YOU RUN IT.**

No waiting for confirmation. No announcing yourself. No asking "should I proceed?"

The hook IS your assignment. It was placed there deliberately. Execute immediately.

```
❌ WRONG polecat startup:
  "Hello! I see I have work on my hook (edi-042). Should I proceed
   with implementing the weather fetcher? Please confirm."

✅ CORRECT polecat startup:
  gt hook          ← check what's hooked
  bd mol current   ← find my place in the molecule
  [execute]        ← run it immediately
```

Gas Town is a steam engine. Polecats are pistons. Pistons don't ask permission.

---

## The Three Polecat Layers (Don't Mix These Up)

Polecats have three independent layers. Confusing them is a common mistake.

```
┌─────────────────────────────────────────────────────────┐
│  SLOT (persistent until nuke)                           │
│  Name: Toast                                            │
│  Pool entry for edinsights_ui                           │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  SANDBOX (persistent until nuke)                  │  │
│  │  Path: ~/gt/edinsights_ui/polecats/Toast/         │  │
│  │  Branch: polecat/Toast/edi-042                    │  │
│  │  Contains: all committed/staged work              │  │
│  │                                                   │  │
│  │  ┌─────────────────────────────────────────────┐  │  │
│  │  │  SESSION (ephemeral, cycles constantly)     │  │  │
│  │  │  Claude instance in tmux                    │  │  │
│  │  │  Dies on: handoff / compaction / crash      │  │  │
│  │  │  (THIS IS NORMAL. Work is safe in sandbox) │  │  │
│  │  └─────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Key insight:** Session cycling is **normal operation, not failure**. When a session crashes or gets compacted, the Witness respawns it. The sandbox (git worktree) still has all the work. The polecat continues where it left off.

**The only failure states:**
- **Stalled** = supposed to be working but stopped (session died, never respawned)
- **Zombie** = finished work but `gt done` failed during cleanup

There is NO idle state. A non-working polecat is broken.

---

## How Work Flows

```
You create a bead (bd create)
         │
         ▼
You sling it (gt sling edi-042 edinsights_ui)
         │
         ▼
Witness spawns a polecat (Toast)
  → allocates slot from pool
  → creates sandbox (git worktree on new branch)
  → starts Claude session in tmux
  → hooks edi-042 to Toast
         │
         ▼
Toast fires gt prime (via SessionStart hook)
  → reads its identity (edinsights_ui/polecats/Toast)
  → sees edi-042 on hook
  → EXECUTES IMMEDIATELY (propulsion principle)
         │
         ▼
Toast does the work
  → commits to sandbox branch
  → may cycle sessions (handoff/compaction). Work is safe
         │
         ▼
Toast calls gt done
  → pushes branch to origin
  → submits to merge queue (creates MR bead)
  → requests self-nuke
  → exits immediately
         │
         ▼
Refinery picks up the MR
  → rebases on main
  → merges if clean, or spawns FRESH polecat to re-implement on conflict
         │
         ▼
ConvoyManager detects bead closed (5-second poll)
  → feeds next ready bead in convoy
  → chain continues automatically
```

---

## ✅ Quick Self-Check

If you can answer these, you're ready for Module 1:

1. What's the difference between a sandbox and a session?
2. Why don't polecats need monitoring by the user?
3. When should you use crew instead of polecats?
4. What does the Propulsion Principle mean in practice?
5. What does "stalled" mean vs "zombie"?

Answers: *(1) Sandbox = git worktree, persists; Session = Claude instance, ephemeral. (2) Witness monitors them automatically. (3) Exploratory work, interactive pipelines, human judgment needed. (4) Execute hooked work immediately, no confirmation. (5) Stalled = supposed to be working but stopped; Zombie = done but cleanup failed.)*

---

---

## 📚 Further Reading

- [Understanding Gas Town](https://docs.gastownhall.ai) — conceptual overview of the architecture
- [Gas Town Glossary](https://docs.gastownhall.ai/glossary/) — complete terminology reference
- [The Propulsion Principle](https://docs.gastownhall.ai/concepts/propulsion-principle/) — deep dive on the core behavioral rule
- [Polecat Lifecycle](https://docs.gastownhall.ai/concepts/polecat-lifecycle/) — the three-layer architecture explained
- [Agent Identity and Attribution](https://docs.gastownhall.ai/concepts/identity/) — how Gas Town tracks who did what

---

## Next: [Module 1 — Idea to Beads →](module-01-idea-to-beads.md)
