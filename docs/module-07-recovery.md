# Module 7: When Things Break

> **Goal:** Recognize failure states and know how to recover. Understand what the Witness and Deacon do automatically, and what requires your intervention.

---

## The Reality

Polecats crash. Sessions time out. Dolt hiccups. The Refinery hits a merge conflict. Gas Town is designed for this. Most failures recover automatically. Your job is to know the difference between "wait, Gas Town is handling it" and "I need to step in."

---

## Failure State Reference

```
Working     ← normal, doing its job
    │
    │  session crashes/compacts. Witness sees no output
    ▼
Stalled     ← supposed to be working, isn't
             Witness detects: nudges first, then respawns
             You see: polecat "working" but gt peek shows nothing

Working     ← normal
    │
    │  gt done called, cleanup failed
    ▼
Zombie      ← work done, session should be dead but isn't
             Witness/Deacon clean these up on patrol
```

> ⚠️ **There is no "idle" state.** A non-working polecat is in a failure state, not resting. Call it what it is.

---

## What Recovers Automatically

| Failure | Who detects it | Auto-recovery |
|---------|---------------|---------------|
| Session crash (no work lost) | Witness | Respawns session; polecat resumes from sandbox |
| Stalled >30 min | Deacon (GUPP check) | Notifies Witness; Witness nudges or respawns |
| Dead polecat with hooked work | Deacon (3-min heartbeat) | Auto-restarts session |
| Mass death (>3 in 30s) | Deacon | Sends alert, escalates to Mayor |
| Zombie cleanup | Witness patrol | Returns slot to pool |
| Merge conflict | Refinery | Spawns fresh polecat to re-implement on new baseline |
| Bead stuck in `hooked` >1h | Deacon | Unhooks → available for redispatch |
| Stale bead stuck `in_progress` | Deacon `stale-hooks` | Releases back to open |

**Most of the time: wait and watch `gt feed`.** The system recovers itself.

---

## When to Intervene

### 1. Polecat Stuck (Not Just Slow)

```bash
# Check status
gt polecat list YOUR_RIG

# See what it's doing (or not doing)
gt peek YOUR_RIG/furiosa

# If no output for 15+ minutes and Witness hasn't nudged it:
gt polecat nuke furiosa      # destroy it
bd update <bead-id> --status=open  # reset bead if needed
gt sling <bead-id> YOUR_RIG  # re-sling
```

> 💡 **"Stuck" vs "slow":** `gt peek` shows no output for 10+ minutes, AND `bd show <bead-id>` shows it's been `in_progress` an unreasonably long time. Normal tasks take 1-5 minutes. Complex tasks can take 10-15. 20+ with no output = probably stuck.

### 2. Bead Orphaned (Polecat Gone, Bead Still Hooked)

```bash
gt orphans                     # find beads with dead owners
bd update <id> --status=open   # reset to unblocked
gt sling <id> YOUR_RIG         # re-dispatch
```

### 3. Convoy Stranded (Work Queued, Nothing Running)

```bash
gt convoy stranded             # find stalled convoys
gt convoy status hq-cv-xyz     # inspect the specific convoy
bd show <bead-id>              # check blocker statuses
bd dep cycles                  # any circular deps?
```

### 4. Dolt Issues

If `bd` commands hang or timeout:

```bash
# Diagnose FIRST (don't just restart)
kill -QUIT $(cat ~/gt/.dolt-data/dolt.pid)   # dumps goroutine trace to stderr log
gt dolt status                                 # check connectivity

# Escalate with evidence
gt escalate -s HIGH "Dolt: <describe symptom>"

# Only if completely unreachable:
gt dolt stop && gt dolt start
```

**Never `rm -rf` the Dolt data directory.** Use `gt dolt cleanup` for orphan databases.

---

## Hands-On: Watching the Witness Work

Let's observe the automatic recovery system without breaking anything.

### Watch Your Town's Patrol Activity

```bash
gt feed    # watch events flow by in real-time
gt log     # recent town activity log
```

Look for events like:
```
[21:14:02] witness nudged edinsights_ui/furiosa (idle 8m)
[21:14:32] furiosa resumed work on edi-042
```

The Witness polls polecats every ~3 minutes. If a polecat is idle without having called `gt done`, it gets nudged.

### Check What the Daemon is Doing

```bash
gt boot status
```

This shows the last Boot triage result: what the Deacon's watchdog found on its most recent health check:

```
Boot Status:
  Last run: 2 minutes ago
  Action: nothing (Deacon healthy)
  Deacon: alive, active output
```

### Simulate a Slow Task

Create a bead with a long but realistic implementation:

```bash
cd ~/gt/YOUR_RIG/crew/claudio
bd create "Add request retry logic to fetcher" -t task -p P3 --stdin << 'EOF'
Add exponential backoff retry to weatherly/fetcher.py.

On requests.exceptions.Timeout or requests.exceptions.ConnectionError:
- Retry up to 3 times
- Wait 1s, then 2s, then 4s between retries (exponential backoff)
- Log each retry attempt to stderr
- Raise the original exception if all retries fail

Use a simple loop, not a library like tenacity.
EOF
```
```bash
bd update <bead-id> --acceptance "- [ ] Retries 3 times on timeout/connection error
- [ ] Wait times are 1s, 2s, 4s (exponential)
- [ ] Logs retry attempts to stderr
- [ ] Raises original exception after all retries fail
- [ ] Unit test verifies retry behavior with mocked requests"

gt sling <bead-id> YOUR_RIG
```

Watch it work:
```bash
gt polecat list YOUR_RIG           # see it's working
gt peek YOUR_RIG/furiosa           # watch the shiny steps
gt convoy -i                       # if you have a convoy tracking it
```

After completion:
```bash
git log --format="%an: %s" -3     # see attribution
bd show <bead-id>                  # see the close reason
```

---

## The Merge Conflict Path

When a polecat finishes but its branch conflicts with main:

```
polecat pushes branch
        │
        ▼
Refinery picks up MR bead
        │
        ▼
   tries to rebase
        │
   CONFLICT DETECTED
        │
        ▼
Refinery spawns FRESH polecat
  → same bead description
  → fresh worktree on updated main
  → re-implements from scratch
        │
        ▼
Refinery merges fresh work
```

**You don't intervene.** The Refinery handles it. The original bead description is the source of truth. This is why clear descriptions matter. A vague description = a re-implementation that might drift.

---

## The Full Diagnostic Flow

When something seems wrong:

```
1. gt status
   ↓ (see overall health: are Witness/Refinery running?)

2. gt polecat list YOUR_RIG
   ↓ (see who's running, who's not)

3. gt feed
   ↓ (recent events: did things move recently?)

4. gt peek YOUR_RIG/polecat-name
   ↓ (what is that specific polecat doing?)

5. bd show <bead-id>
   ↓ (is the bead in the right state?)

6. gt convoy status <convoy-id>
   ↓ (is the convoy stuck? any beads still open?)

7. bd dep cycles
   ↓ (any circular deps blocking dispatch?)

8. gt doctor
   ↓ (system-level health check)

9. gt escalate -s HIGH "..."
   ↓ (if you can't fix it, Mayor gets involved)
```

---

## 📝 Recovery Command Reference

```bash
# Visibility
gt status                        # overall health
gt polecat list YOUR_RIG         # active polecats (positional, no --rig)
gt peek YOUR_RIG/name            # polecat output (full address required)
gt feed                          # real-time event stream
gt log                           # town activity log
gt orphans                       # beads with dead owners
gt convoy stranded               # stalled convoys
gt doctor                        # full health check

# Intervention
gt polecat nuke <name>           # destroy a stuck polecat
bd update <id> --status=open     # reset a stuck bead
gt sling <id> YOUR_RIG           # re-dispatch
gt escalate -s HIGH "..."        # escalate to Mayor

# Dolt
gt dolt status                   # check DB health
gt dolt cleanup                  # remove orphan test DBs (safe)
gt dolt stop && gt dolt start    # restart (diagnose first)
```

---

## 🎓 You've Completed the Workshop

You now know how to:
- ✅ Think in Gas Town's mental model (agents, beads, convoys, molecules, waves)
- ✅ Create beads with proper hierarchy, acceptance criteria, and deps
- ✅ Build dependency chains that the ConvoyManager auto-dispatches
- ✅ Launch parallel work lanes via convoy stage → launch
- ✅ Run the full `mol-idea-to-plan` → `shiny` pipeline in a crew session
- ✅ Diagnose and recover from failure states

**The insight to take away:**

Gas Town is a **work ledger**, not just a task runner. Every action is attributed, every bead timestamped, every polecat with a track record. The dependency graph you declare IS the parallelism you get. The quality of your bead descriptions IS the quality of what polecats build.

Six months from now: `git log --author="YOUR_RIG/polecats"` shows everything your agents ever built. `bd audit --actor=YOUR_RIG/polecats/*` shows how long it took and what they closed. That's the point.

Build thoughtfully. Launch confidently. Walk away while the swarm works.

⛽

---

---

## 📚 Further Reading

- [Daemon/Boot/Deacon Watchdog Chain](https://docs.gastownhall.ai/design/watchdog-chain/) — how automatic health monitoring works
- [Escalation System Design](https://docs.gastownhall.ai/design/escalation-system/) — what happens when you `gt escalate`
- [Gas Town Escalation Protocol](https://docs.gastownhall.ai/design/escalation/) — escalation paths reference
- [Diagnostics Commands](https://docs.gastownhall.ai/usage/diagnostics/) — `gt doctor`, `gt status`, `gt orphans` reference
- [Towers of Hanoi Demo](https://docs.gastownhall.ai/examples/hanoi-demo/) — a durability proof showing crash recovery in action

---

## Appendix

- [Quick Reference Card](appendix-quick-reference.md)
- [Common Errors & Fixes](appendix-common-errors.md)
