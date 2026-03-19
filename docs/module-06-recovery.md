# Module 6: When Things Break

> **Goal:** Recognize failure states and know how to recover. Understand what the Witness and Deacon do automatically, and what requires your intervention.

---

## The Reality

Polecats crash. Sessions time out. Dolt gets unhappy. The Refinery hits a merge conflict. Networks drop. Claude gets confused and loops.

Gas Town is designed for this. Most failures are handled automatically. But you need to know the difference between "Gas Town is handling it" and "you need to intervene."

---

## Failure State Reference

```
Working     ← normal, doing its job
    │
    │  session crashes, never respawned
    ▼
Stalled     ← supposed to be working, isn't
             (Witness detects and nudges/respawns)

Working     ← normal
    │
    │  gt done called, cleanup failed
    ▼
Zombie      ← work done, cleanup stuck
             (Witness/Deacon clean these up)
```

**There is no "idle" state.** If a polecat exists but isn't working, something is wrong.

---

## What Recovers Automatically

The Witness and Deacon handle most failure cases without you:

| Failure | Detected By | Auto-Recovery |
|---------|------------|---------------|
| Session crash (no work lost) | Witness | Respawns session, polecat resumes from sandbox |
| Stalled polecat (stuck >30min) | Deacon (GUPP check) | Witness notified, Witness nudges or respawns |
| Dead polecat with hooked work | Deacon (crash detection) | Auto-restart; mass death detection if >3 in 30s |
| Orphaned work (dead polecat, bead still hooked) | Deacon | Sends to Deacon for redispatch |
| Zombie polecat | Witness on patrol | Cleans up, slot returned to pool |
| Merge conflict in Refinery | Refinery | Spawns FRESH polecat to re-implement on new baseline |
| Stale bead stuck in `hooked` >1h | Deacon | Unhooks it → available for redispatch |

**Most of the time, you don't need to do anything.** Watch `gt feed` and let Gas Town recover.

---

## When You Need to Intervene

These require manual action:

### 1. Stalled Polecat That Isn't Recovering

```bash
# Diagnose
gt polecat list YOUR_RIG            # see status (positional, no --rig flag)
gt peek YOUR_RIG/furiosa            # full address: rig/name
gt feed                             # check recent activity

# If it's genuinely stuck (not just slow):
gt polecat nuke furiosa             # destroy it (use actual polecat name)
gt sling <bead-id> YOUR_RIG         # re-sling the bead
```

**How to tell "stuck" from "slow":** `gt peek Toast` shows no output for 10+ minutes, and the bead has been `in_progress` for an unusually long time. Agents working on complex tasks can be quiet for 3-5 minutes. Quiet for 15+ is concerning.

### 2. Bead Stuck in `hooked` State After Polecat Is Gone

```bash
# Find orphaned beads
gt orphans

# Reset the bead
bd update <bead-id> --status=open

# Re-sling
gt sling <bead-id> YOUR_RIG
```

### 3. Convoy Stranded (work queued, nothing running)

```bash
# Find stranded convoys
gt convoy stranded

# Check what's blocking
gt convoy status hq-cv-xyz

# If it's a dep issue
bd dep cycles                 # check for circular deps
bd show <bead-id>             # inspect individual blockers
```

### 4. Dolt Issues

If `bd` commands hang, timeout, or give "connection refused":

```bash
# Diagnose FIRST (don't just restart)
kill -QUIT $(cat ~/gt/.dolt-data/dolt.pid)   # dumps goroutine trace
gt dolt status                                 # check health

# Then escalate
gt escalate -s HIGH "Dolt: <describe symptom>"

# Only if completely unreachable
gt dolt stop && gt dolt start
```

**⚠️ Never `rm -rf` the Dolt data directory.** Use `gt dolt cleanup` instead.

---

## Hands-On: Inducing and Recovering a Stall

Let's intentionally trigger a recovery scenario to practice:

### Scenario: The Overthinking Polecat

Create a bead designed to take a while:

```bash
bd create "Add weather data caching layer" \
  -t task -p P3 \
  --description "Add a simple file-based cache to weatherly that stores the last API response.
  
Cache should:
- Store response in ~/.weatherly/cache.json
- Include timestamp
- Expire after 10 minutes
- Fall back to live API if cache miss or expired

Create weatherly/cache.py with load_cache() and save_cache() functions." \
  --acceptance "- [ ] weatherly/cache.py exists
- [ ] Cache reads/writes to ~/.weatherly/cache.json
- [ ] Expiry logic works correctly
- [ ] Falls back gracefully on cache miss"
```

Sling it:
```bash
gt sling <bead-id> YOUR_RIG
```

Now watch it for a bit:
```bash
gt feed
gt peek <polecat-name>
```

If you want to practice forced recovery:
```bash
# Wait until it's in_progress, then nuke it
gt polecat nuke <name>

# Check what happened to the bead
bd show <bead-id>    # should be hooked or open after Witness recovery

# Re-sling if needed
gt sling <bead-id> YOUR_RIG
```

---

## The Escalation System

When agents encounter something they can't resolve:

```bash
# From any agent (polecat, witness, deacon)
gt escalate -s HIGH "Description of the issue"
gt escalate -s CRITICAL "Urgent — complete outage"
```

Levels: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`

- `HIGH` → Mayor notified
- `CRITICAL` → Mayor + Overseer (human) notified

You can also check for escalations:
```bash
gt mail                        # check your mail (if you're Mayor)
gt broadcast "status check"    # nudge all workers
```

---

## Health Checks

Run `gt doctor` regularly. Aim for 0 warnings, 0 failures:

```bash
gt doctor
```

Common warnings and fixes:
```bash
gt doctor --fix    # auto-fixes common issues
```

**Periodic check habit:**
```bash
gt doctor && gt status && gt convoy list
```

---

## The Full Diagnostic Flow

When something seems wrong:

```
1. gt status
   ↓ (see overall health)
2. gt polecat list YOUR_RIG
   ↓ (see what's running — positional arg, no --rig)
3. gt convoy list
   ↓ (see what's in flight)
4. gt feed (or gt log)
   ↓ (see recent events)
5. gt peek <polecat-name>
   ↓ (see what specific agent is doing)
6. bd show <bead-id>
   ↓ (inspect the work item)
7. gt doctor
   ↓ (run health checks)
8. gt escalate (if needed)
```

---

## Merge Conflicts: The Refinery Handles It

When a polecat's branch conflicts with main:

```
Polecat finishes → gt done → pushes branch → Refinery picks up MR
                                                      │
                                              tries to rebase
                                                      │
                                              CONFLICT!
                                                      │
                                    spawns FRESH polecat to re-implement
                                    on updated main baseline
                                              │
                                    fresh polecat has full context of original bead
                                    re-implements on clean base
                                              │
                                    Refinery merges fresh work
```

**You don't intervene.** The Refinery handles conflicts by spawning a fresh implementation. The original bead description is the source of truth — the new polecat re-implements from scratch on the new baseline.

This is why **clear, self-contained bead descriptions** matter so much. If the description is ambiguous, re-implementation produces something subtly different.

---

## 📝 Recovery Command Reference

```bash
# Diagnosis
gt status                              # overall health
gt polecat list YOUR_RIG               # active polecats (positional, no --rig)
gt peek YOUR_RIG/polecat-name          # polecat output (full address required)
gt feed                                # real-time activity
gt orphans                             # beads with dead owners
gt convoy stranded                     # stalled convoys
gt doctor                              # health checks

# Intervention
gt polecat nuke <name>                 # destroy a polecat
bd update <id> --status=open           # reset a stuck bead
gt sling <id> YOUR_RIG                 # re-dispatch
gt escalate -s HIGH "..."              # escalate to Mayor

# Dolt (careful!)
gt dolt status                         # check DB health
gt dolt cleanup                        # remove orphan test DBs (safe)
gt dolt stop && gt dolt start          # restart (last resort, diagnose first)
```

---

## 🎓 You've Completed the Workshop

You now know how to:
- ✅ Think in Gas Town's mental model
- ✅ Create beads with proper hierarchy and acceptance criteria
- ✅ Build dependency chains and parallel work lanes
- ✅ Use convoy stage → launch for validated dispatch
- ✅ Run the full spec → plan → beads → swarm pipeline in a crew session
- ✅ Diagnose and recover from failure states

**The key insight to take away:**

Gas Town isn't just a task tracker. It's a **work ledger** — every action attributed, every bead timestamped, every polecat with a track record. The dependency graph you design IS the parallelism you get. The quality of your bead descriptions IS the quality of what polecats build.

Build thoughtfully. Launch confidently. Walk away while the swarm works.

⛽

---

## Appendices

- [A. Quick Reference Card](appendix-quick-reference.md)
- [B. Bead Quality Rules](appendix-bead-quality.md)
- [C. Full gt CLI Reference](appendix-gt-reference.md)
