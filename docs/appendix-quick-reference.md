# Appendix A: Quick Reference Card

## The Core Loop

```
bd create → gt sling → polecat works → gt done → Refinery merges → bd closes
```

## The Pipeline Loop

```
gt sling spec-workflow → plan-workflow → beads-workflow → gt convoy stage → launch
```

## Bead Operations

```bash
# Create: use heredoc for long descriptions (no shell escaping)
bd create "Title" -t [epic|task|bug|chore] -p [P0-P4] \
  --parent $PARENT_ID \
  --deps "$BLOCKER1,$BLOCKER2" \
  --stdin << 'EOF'
Your description here. Multiple lines, no escaping needed.
EOF

# Add acceptance criteria after creation
bd update <id> --acceptance "- [ ] criterion 1
- [ ] criterion 2"

# Or use a file for the description
bd create "Title" -t task -p P2 --body-file ./description.md

# Inspect
bd show <id>               # details
bd list --json             # all beads
bd ready                   # unblocked, ready to work
bd dep cycles              # check for circular deps

# Update
bd update <id> --status=open    # reopen
bd close <id>                   # close
bd close <id> --continue        # close + advance molecule step
```

## Convoy Operations

```bash
gt convoy stage <epic-id>        # validate dep graph + wave plan (INERT)
gt convoy launch <convoy-id>     # dispatch Wave 1, daemon feeds rest

gt convoy create "Name" edi-abc edi-def --notify   # --notify alone = notify mayor/
                                                    # --notify addr = notify specific address
gt convoy status hq-cv-abc
gt convoy list                   # active
gt convoy list --all             # include landed
gt convoy stranded               # work queued, nothing running
```

## Polecat Operations

```bash
gt sling <bead-id> <rig>                     # assign to polecat
gt sling <bead-id> <rig> --model claude-sonnet
gt polecat list <rig>                        # active polecats (POSITIONAL, no --rig flag)
gt peek <rig>/<name>                         # see polecat output (FULL ADDRESS required)
gt polecat nuke <name>                       # destroy polecat
```

## Crew Operations

```bash
gt crew start human           # start session (creates if needed)
gt crew at human              # attach terminal
gt crew list                    # status of all crew workspaces
gt crew stop human            # stop session
gt crew refresh human         # context cycle with handoff
gt crew restart human         # kill + restart fresh
```

## Molecule Navigation (inside agent)

```bash
gt hook                          # what's on my hook?
gt prime                         # re-read identity + hooked work
bd mol current                   # where am I in the molecule?
bd close <step> --continue       # close step + auto-advance
```

## Visibility

```bash
gt status                        # overall health
gt feed                          # real-time activity feed
gt rig status <rig>              # rig-level view
gt polecat list --rig <rig>      # active polecats
gt doctor                        # health checks
gt doctor --fix                  # auto-fix
tmux list-sessions               # ground truth
bd audit --actor=<rig>/polecats/* # work history
bd stats --actor=...             # performance metrics
```

## Communication

```bash
gt nudge <actor> "message"       # lightweight (no bead created)
gt mail send <actor> "message"   # persistent (creates bead)
gt broadcast "message"           # nudge all workers
gt escalate -s HIGH "..."        # escalate to Mayor
```

## Recovery

```bash
gt orphans                       # beads with dead owners
bd update <id> --status=open     # reset stuck bead
gt polecat nuke <name>           # destroy polecat
gt sling <id> <rig>              # re-dispatch
gt dolt status                   # DB health
gt dolt cleanup                  # remove orphan test DBs
```

## Formula Pipeline

```bash
# Install (one-time)
cp ~/source/gt-toolkit/formulas/*.formula.toml ~/gt/.beads/formulas/

# Run
gt sling spec-workflow <rig>/crew/<name> --var feature="X" --var brief="Y"
gt sling plan-workflow <rig>/crew/<name> --var feature="X"
gt sling beads-workflow <rig>/crew/<name> --var feature="X"
```

---

## Mental Model Quick-Check

| Term | What It Is |
|------|-----------|
| Bead | Unit of work (like an issue, but richer) |
| Polecat | Ephemeral Claude Code session in a git worktree |
| Crew | Persistent git clone for human/interactive work |
| Convoy | Tracking unit for batched work |
| Molecule | Structured multi-step workflow |
| Witness | Watches polecats, respawns crashed ones |
| Refinery | Merges polecat branches to main |
| Deacon | Background Go daemon, every 3 min heartbeat |
| ConvoyManager | Goroutine, polls beads every 5s, auto-feeds next ready bead |

| State | Meaning |
|-------|---------|
| Working | Normal |
| Stalled | Supposed to work, stopped (session died, not respawned) |
| Zombie | Work done, `gt done` cleanup failed |
| (no idle) | Idle state doesn't exist |
