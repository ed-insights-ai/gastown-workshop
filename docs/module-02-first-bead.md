# Module 2: Your First Bead

> **Goal:** Create one bead, sling it to a polecat, and watch the full loop from creation to closed.

> **Before you start:** Make sure you've completed the [Setup](setup.md) and know your rig name. All commands in this module run from `~/gt/YOUR_RIG/crew/human`.

---

## The Core Loop

Every Gas Town workflow reduces to this:

```
bd create → gt sling → polecat works → gt done → Refinery merges → bead closes
```

This module walks through that loop with a single bead.

---

## Why We're Doing This Manually

Your `docs/initial-plan.bead.md` from Module 1 already has ready-to-run `bd create` commands for every bead. You could hand that file to your crew agent and let it create them all at once. And by Module 5, that's exactly what you'll do.

But first, you need to understand what happens inside the core loop. Creating one bead by hand, slinging it, and watching the full cycle gives you the mental model to debug problems and reason about what the automation is doing for you.

## What We're Building

A Python file: `weatherly/config.py`, a simple configuration module that holds API settings and defaults. Small enough to complete in one polecat session, clear enough to have real acceptance criteria.

---

## Step 1: Create the Bead

Long descriptions are easier with a heredoc. No shell escaping, just natural text:

```bash
bd create "Add weatherly config module" -t task -p P2 --stdin << 'EOF'
Create weatherly/config.py with API configuration and app defaults.

File should contain:
- API_BASE_URL = 'https://wttr.in'
- DEFAULT_FORMAT = 'j1' (JSON format)
- DEFAULT_UNITS = 'metric'
- REQUEST_TIMEOUT = 10 (seconds)
- A Config dataclass with location, units, and format fields

All values should be type-annotated. Add a module docstring.
EOF
```

Then add acceptance criteria separately:
```bash
# Use the bead ID returned above (e.g. edi-001)
bd update <BEAD_ID> --acceptance "- [ ] File exists at weatherly/config.py
- [ ] All constants defined with correct values and type annotations
- [ ] Config dataclass exists with location, units, format fields
- [ ] Module docstring present
- [ ] No import errors (python -c 'from weatherly.config import Config')"
```

> 💡 **Alternative:** Use `--body-file` to point at a markdown file:
> ```bash
> bd create "Title" -t task -p P2 --body-file ./my-description.md
> ```
> Great for pre-writing bead descriptions in your editor.

**You'll get back a bead ID** like `edi-001` (yours will be different). Write it down or copy it.

> 💡 **Your IDs will differ from these examples.** Gas Town generates unique IDs. Wherever you see `edi-001` below, substitute the actual ID you received.

---

## Step 2: Inspect the Bead

```bash
bd show <BEAD_ID>        # e.g. bd show edi-a3x
```

You should see the title, description, acceptance criteria, status (`open`), and `created_by` (your crew identity).

Also try:
```bash
bd list --json | jq '.[0]'   # see the raw structure
```

---

## Step 3: Check What's Ready

```bash
bd ready
```

This shows all beads with no unresolved blockers, things that can be picked up right now. Your bead should appear here since it has no dependencies.

---

## Step 4: Create a Convoy

Before slinging, create a convoy so you can track this work:

```bash
gt convoy create "weatherly config module" <BEAD_ID> --notify
```

**You'll get a convoy ID** like `hq-cv-abc` (yours will be different).

```bash
gt convoy list                   # see your new convoy in the dashboard
gt convoy status <CONVOY_ID>     # see the convoy details
```

> 💡 **"Progress: 0/0"?** Don't worry. The convoy shows `0/0` until the bead is actually slung to a polecat. The tracking link is there; the counter activates on dispatch. This is normal.

> 💡 **`--notify`** without an argument defaults to notifying `mayor/`. You can specify an address: `--notify YOUR_RIG/crew/human` to notify yourself directly.

---

## Step 5: Sling to a Polecat

First, confirm your rig name:
```bash
gt rig list
```

Then sling:
```bash
gt sling <BEAD_ID> YOUR_RIG_NAME
```

Replace `YOUR_RIG_NAME` with your actual rig name from above.

**Expected output (yours will look similar):**
```
Target is rig 'YOUR_RIG', spawning fresh polecat...
Created polecat: furiosa           ← if no idle polecats available
  (or)
Reusing idle polecat: furiosa      ← if an idle polecat exists
✓ Polecat furiosa spawned (or reused)
🎯 Slinging edi-001 to YOUR_RIG/polecats/furiosa...
○ Already tracked by convoy hq-cv-abc
  Auto-applying mol-polecat-work for polecat work...
  Instantiating formula mol-polecat-work...
✓ Formula wisp created: edi-wisp-xxxx
✓ Formula bonded to edi-001
✓ Work attached to hook (status=hooked)
Starting session for YOUR_RIG/furiosa...
```

**What this means:**
- `furiosa` is the polecat name allocated from the pool (yours may be different)
- `mol-polecat-work` is a built-in Gas Town formula that auto-attaches to polecat tasks. It creates a structured work molecule that guides the polecat through the task step-by-step (load context → implement → commit → done). You don't configure this; it's automatic.
- `status=hooked` means the bead is now assigned and the polecat is starting

**What just happened:**
- Gas Town allocated a polecat name from the pool (e.g., furiosa, nux, slit)
- Created a git worktree at `~/gt/YOUR_RIG/polecats/furiosa/`
- Started a Claude Code session in that directory
- Hooked `edi-001` to the polecat
- The polecat is now running the Propulsion Principle: `gt hook` → `bd mol current` → execute

---

## Step 6: Watch It Work

### See the polecat running
```bash
gt polecat list YOUR_RIG_NAME
```

Note: it's a positional argument, not a flag. No `--rig`.

### Peek at what it's doing
```bash
gt peek YOUR_RIG_NAME/furiosa
```

Use the full address format: `rig/polecat-name`. Get the polecat name from `gt polecat list`.

### Watch the live activity feed
```bash
gt feed
```

You'll see events like:
```
[20:15:33] furiosa hooked edi-001: Add weatherly config module
[20:15:34] furiosa → in_progress
[20:15:47] furiosa committed: feat: add weatherly config module
[20:15:48] furiosa → gt done
```

### Watch your convoy update
```bash
gt convoy status <CONVOY_ID>
```

---

## Step 7: After Completion

When the polecat is done:

1. `gt done` was called → branch pushed → submitted to merge queue
2. Polecat self-nuked (session + sandbox destroyed, slot returned to pool)
3. Refinery picks up the MR → rebases → merges to main
4. Bead closes automatically
5. Convoy lands (all tracked beads closed) → you get notified

Check the results:
```bash
bd show <BEAD_ID>         # status: closed
gt convoy list --all      # convoy: landed
git log --oneline -3      # see the commit with the polecat's attribution
```

Look at that git log entry. It'll show the polecat's identity:
```
abc1234 feat: add weatherly config module
Author: YOUR_RIG/polecats/furiosa <you@email.com>
```

That attribution is in the git history permanently. Six months from now you can run `git log --author="YOUR_RIG/polecats"` and see everything your polecats ever built.

---

## 🔍 What Just Happened (Annotated)

```
bd create edi-001
│  └─ Creates bead in Dolt DB with your identity as created_by
│
gt convoy create → hq-cv-abc
│  └─ Creates convoy bead in town-level (hq-) beads
│     Links edi-001 via "tracks" relationship
│
gt sling edi-001 YOUR_RIG
│  └─ Witness allocates "Toast" from name pool
│     Creates worktree: ~/gt/RIG/polecats/Toast/
│     Spawns: tmux session "gt-RIG-Toast" with Claude Code
│     Sets env: BD_ACTOR=RIG/polecats/Toast, GT_ROLE=polecat, etc.
│     Hooks edi-001 → Toast (bead status: hooked)
│
Toast runs gt prime
│  └─ Reads env variables → knows it's Toast in RIG
│     Checks hook → sees edi-001
│     Propulsion: execute immediately
│
Toast works
│  └─ Implements weatherly/config.py
│     Commits with gt commit (uses GIT_AUTHOR_NAME=RIG/polecats/Toast)
│     If session cycles (compaction): Witness respawns, work is safe in worktree
│
Toast calls gt done
│  └─ Pushes branch polecat/Toast/edi-001 to origin
│     Creates MR bead in merge queue
│     Requests self-nuke (session exits, worktree removed, slot returned to pool)
│
Refinery merges
│  └─ Rebases on main → merges
│     Closes edi-001
│
ConvoyManager detects close (within 5 seconds)
   └─ Checks if hq-cv-abc has all beads closed
      If yes: marks convoy as landed, sends notification
```

---

## ⚠️ Common Mistakes at This Stage

**"The polecat isn't doing anything"**
Run `gt polecat list YOUR_RIG_NAME`. Is it in "Working" state? Peek with `gt peek YOUR_RIG/polecat-name`. If it's stalled after 10+ minutes of no output, `gt polecat nuke polecat-name` and re-sling.

**"I don't see the bead in bd ready"**
Check if the bead was created correctly with `bd show <BEAD_ID>`. If it's already `hooked`, it's been picked up by the polecat.

**"The convoy shows 0/0. Is something broken?"**
Nope, normal. The counter shows 0/0 until dispatch. After slinging, it activates.

**"The convoy didn't close after the bead closed"**
Convoy auto-closes when ALL tracked beads close. Check `gt convoy status <CONVOY_ID>` to see which are still open.

**"I see `beads.role not configured` warning"**
This warning appears if you haven't run `bd init` to set your role. It's harmless for workshop purposes. Your beads still get created correctly. Suppress it by running `bd config set beads.role maintainer` from your crew directory.

---

## 📝 Key Commands Learned

```bash
bd create              # create a bead
bd show <id>           # inspect a bead
bd ready               # what can be worked on right now (shows ALL unblocked beads)
gt convoy create       # create a tracking convoy
gt convoy list         # dashboard of active convoys
gt convoy status <id>  # detailed convoy view
gt sling <id> <rig>    # assign bead to polecat
gt polecat list <rig>  # see active polecats (positional arg, not --rig)
gt peek <rig>/<name>   # watch polecat output (full address required)
gt feed                # real-time Gas Town event stream
git log --oneline      # see attributed commits
```

---

---

## 📚 Further Reading

- [Polecat Lifecycle](https://docs.gastownhall.ai/concepts/polecat-lifecycle/) — slot, sandbox, and session layers
- [Convoys](https://docs.gastownhall.ai/concepts/convoy/) — how convoy tracking works under the hood
- [Work Management Commands](https://docs.gastownhall.ai/usage/work-management/) — full `bd` and `gt sling` reference

---

## Next: [Module 3 — Dependency Chains →](module-03-dependency-chain.md)
