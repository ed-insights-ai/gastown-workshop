# Appendix C: Common Errors & Fixes

Quick lookup for error messages you'll actually see.

---

## `bd` Errors

### `Error: database not initialized: issue_prefix config is missing`
**You're running `bd create` from the wrong directory.**
Gas Town commands need to run from inside `~/gt` or a crew/polecat workspace.
```bash
cd ~/gt/YOUR_RIG/crew/human
bd create ...
```

### `Error: failed to open database: database "rig_name" not found on Dolt server`
**Dolt fingerprint mismatch.** Usually happens after repo URL changes.
```bash
bd doctor | head -20    # look for "Repo Fingerprint" error
echo "y" | bd migrate --update-repo-id
```

### `warning: beads.role not configured. Run 'bd init' to set.`
**Harmless warning.** Your beads still work correctly.
Silence it:
```bash
cd ~/gt/YOUR_RIG/crew/human
bd config set beads.role maintainer
```

### `Error: unknown flag: --type` (on `bd dep remove`)
**`bd dep remove` doesn't support `--type`.** Just pass the two IDs:
```bash
bd dep remove <blocked-id> <blocker-id>    # removes the blocks dep
```
To remove a parent-child dep, same syntax. It finds and removes the right one.

---

## `gt` Errors

### `Error: not in a Gas Town workspace`
**You're running `gt` from outside `~/gt`.** Always `cd ~/gt` first.
```bash
cd ~/gt
gt status
```

### `Error: unknown flag: --rig` (on `gt polecat list`)
**`gt polecat list` takes a positional argument, not a flag.**
```bash
gt polecat list YOUR_RIG       # ✅ correct
gt polecat list --rig YOUR_RIG # ❌ wrong
```

### `Error: not in a rig directory. Use full address format: gt peek <rig>/<polecat>`
**`gt peek` needs the full address.** Get the polecat name from `gt polecat list YOUR_RIG` first.
```bash
gt peek YOUR_RIG/furiosa    # ✅ correct
gt peek furiosa             # ❌ wrong
```

### `Error: unknown flag: --human` (on `gt convoy create`)
**`--human` doesn't exist.** Use `--notify` alone (notifies mayor/) or with an address.
```bash
gt convoy create "name" edi-xxx --notify                    # notify mayor/
gt convoy create "name" edi-xxx --notify YOUR_RIG/crew/me   # notify yourself
```

### `Error: no slingable tasks in DAG` (on `gt convoy stage`)
**The epic has no task/bug/feature/chore children**, OR the parent-child deps are backwards.
Check:
```bash
bd show <epic-id>    # look for CHILDREN ↳ section
```
If you see `PARENT ↑` instead of `CHILDREN ↳`, your deps are reversed. Fix:
```bash
# Correct direction: child depends on parent
bd dep add <task-id> <epic-id> --type parent-child
```

### `gt convoy stage` hangs indefinitely
**Likely a circular dependency in the dep graph.** Kill it and check:
```bash
# Kill the hung command (Ctrl+C)
bd dep cycles    # check for cycles
```
Also can happen with bidirectional parent-child deps (a → b AND b → a).

### `gt up` fails with "port 3307 already in use"
**Dolt is already running** from a previous session. This is fine, it's a false alarm.
```bash
ps aux | grep dolt | grep -v grep    # confirm Dolt process exists
# If it's there, proceed. Dolt is running fine
```

---

## Polecat Behavior

### Polecat output shows `Auto-applying mol-polecat-work for polecat work...`
**This is expected and good.** Gas Town is attaching a structured work molecule that guides the polecat through design → implement → review → test → submit steps. No action needed.

### `gt polecat list YOUR_RIG` shows polecat as "idle" for a long time
**Idle means it hasn't been slung work**, not a failure state. Check if it picked up a bead:
```bash
gt peek YOUR_RIG/furiosa    # if it's working, you'll see output
```
If the polecat was working and is now idle but the bead is still `in_progress`:
```bash
bd show <bead-id>           # check status
gt orphans                  # check if bead is orphaned
```

### Convoy shows `Progress: 0/0` after creation
**Normal.** The counter in `gt convoy status` doesn't reflect what `gt convoy create` says about "Tracking: N issues". They're showing different things. The `0/0` counter activates once beads start closing. Not a bug, just confusing display.

### Bead stays in `hooked` state after polecat session ends
**The Deacon will unhook it after 1 hour.** If you want to recover it faster:
```bash
bd update <id> --status=open
gt sling <id> YOUR_RIG
```

---

## Dolt / Data Issues

### `bd` commands hang or timeout
**Dolt server issue.** Diagnose before restarting:
```bash
kill -QUIT $(cat ~/gt/.dolt-data/dolt.pid)    # dumps goroutine trace
gt dolt status
gt escalate -s HIGH "Dolt: commands hanging"
```
Only restart if completely unreachable:
```bash
gt dolt stop && gt dolt start
```

### Orphan databases accumulating
```bash
gt dolt cleanup    # safe: removes test/orphan DBs, protects production
gt dolt status     # shows orphan count
```

---

## Mail Commands

### `gt mail` with no subcommand gives "requires a subcommand"
```bash
gt mail inbox    # ✅ list messages
gt mail read 1   # ✅ read by index
```

### `gt mail send`: `--thread` flag doesn't exist
Use `--reply-to <message-id>` instead:
```bash
gt mail send YOUR_RIG/human \
  --subject "Re: ..." \
  --reply-to hq-wisp-xxxxx \    # message ID from gt mail inbox
  --message "your reply"
```

### `gt mail inbox` shows old messages mixed with new
Messages stay in inbox until archived. The newest is always index 1. Use `gt mail read 1` to get the latest.

### After replying, crew agent doesn't continue
You need to nudge it. Mail delivery alone doesn't wake the agent:
```bash
gt nudge YOUR_RIG/human "Answers sent. Continue."
```

---

## Formula / Molecule Issues

### `gt formula list` doesn't show spec-workflow, plan-workflow, beads-workflow
**gt-toolkit formulas aren't installed.** These are community formulas, not built-in.
```bash
git clone https://github.com/Xexr/gt-toolkit.git ~/source/gt-toolkit
cp ~/source/gt-toolkit/formulas/*.formula.toml ~/gt/.beads/formulas/
```

### `mol-idea-to-plan` slung but crew session doesn't react
**Check if the crew session is actually running:**
```bash
gt crew list        # is human running?
gt crew start human    # start it if not
gt crew at human       # attach to watch it
```

### Molecule steps showing 0/N complete, nothing happening
**Check if the polecat is actually running steps:**
```bash
bd mol current <molecule-id>    # see which step is active
gt peek YOUR_RIG/polecat-name   # see what polecat is doing
```
