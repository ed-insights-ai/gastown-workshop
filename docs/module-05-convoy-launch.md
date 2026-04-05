# Module 5: Convoy Launch: Stage, Validate, Launch

> **Goal:** Use the proper `gt convoy stage → launch` flow. See what wave computation actually looks like, and understand what staging gives you that direct slinging doesn't.

> **All commands run from:** `~/gt/YOUR_RIG/crew/claudio`

---

## Connecting Back to Your Plan

In Modules 2-4, you created beads by hand to learn the mechanics. But your `docs/initial-plan.bead.md` from Module 1 already had all of this mapped out.

Now that you understand beads, dependencies, and parallel waves, you can let automation do the heavy lifting. You have two options:

1. **Run the plan yourself:** Copy the `bd create` commands from `docs/initial-plan.bead.md` and paste them into your shell
2. **Let your crew agent do it:** Open a crew session and ask it to read the plan and execute the bead creation commands

```bash
# Option 2: crew agent reads your plan and creates beads
gt crew at claudio
# Then inside the session:
# "Read docs/initial-plan.bead.md and run all the bd create and bd dep add commands in it."
```

Either way, you end up with beads and deps in the system. What matters next is **validating the wave plan before anything runs**.

---

## The Problem with Slinging Directly

When you `gt sling` directly without staging, you're flying blind:

- No dep graph validation (circular deps go undetected until runtime)
- No wave preview (you don't know what will dispatch when)
- No pre-flight abort (work starts immediately, can't cancel)

For small 2-3 bead chains this is fine. For anything larger, use the pre-flight.

---

## Stage → Launch: The Two-Phase Flow

```
gt convoy stage <bead-id-list or epic-id>
         │
         ▼
   STAGED (status: staged_ready)
   INERT. Nothing dispatches yet
   Shows:
     ✓ dependency tree
     ✓ wave computation (Kahn's topological sort)
     ✓ parallelism analysis
         │
    you review it
         │
         ▼
gt convoy launch <convoy-id>
         │
         ▼
   OPEN status
   Wave 1 dispatches immediately (all in parallel)
   ConvoyManager feeds Wave 2+ automatically as beads close
```

**Staged convoys are completely inert.** The daemon skips them in both the event poll and the stranded scan. Nothing runs until you explicitly launch.

---

## What `gt convoy stage` Actually Looks Like

Here's real output from staging 4 beads with a dependency graph:

```
edi-0dm [task] task B - no deps (rig: YOUR_RIG) [open]
edi-6tq [task] task A - no deps (rig: YOUR_RIG) [open]
edi-77a [task] task C - needs A (rig: YOUR_RIG) [open] ← blocked by: edi-6tq
edi-qn8 [task] task D - needs A+B (rig: YOUR_RIG) [open] ← blocked by: edi-0dm, edi-6tq

Wave   ID       Title               Rig            Blocked By
────────────────────────────────────────────────────────────────
1      edi-0dm  task B - no deps    YOUR_RIG  —
1      edi-6tq  task A - no deps    YOUR_RIG  —
2      edi-77a  task C - needs A    YOUR_RIG  edi-6tq
2      edi-qn8  task D - needs A+B  YOUR_RIG  edi-0dm, edi-6tq

4 tasks across 2 waves (max parallelism: 2 in wave 1)
Convoy created: hq-cv-dnxwn (status: staged_ready)
```

And the launch output:

```
Convoy launched: hq-cv-dnxwn (status: open)

  Monitor: gt convoy status hq-cv-dnxwn

Wave summary:
  2 waves, 4 tasks total
  Wave 1: 2 tasks (dispatched)
  Wave 2: 2 tasks (pending)

Dispatched (Wave 1):
  ✓ edi-0dm  task B - no deps  (rig: YOUR_RIG)
  ✓ edi-6tq  task A - no deps  (rig: YOUR_RIG)

Subsequent waves will be dispatched automatically by the daemon as tasks complete.
```

Clean. You see exactly what's launching and what's waiting.

---

## Setting Up: Add Tests (The Real Wave 3)

Let's add a test layer to weatherly that depends on everything else.

```bash
# Unit tests for the parser
bd create "Add parser unit tests" -t task -p P2 --stdin << 'EOF'
Create tests/test_parser.py with unit tests for the weather parser.

Test cases:
1. test_parse_valid_response: create a minimal valid wttr.in JSON structure,
   verify all fields parse correctly
2. test_parse_missing_field: pass JSON missing 'current_condition',
   verify ValueError raised
3. test_parse_invalid_nested: pass JSON with wrong nested structure,
   verify ValueError

Use Python's unittest.TestCase. Include a sample_response fixture at the top.
Create tests/__init__.py (empty).
EOF
```
```bash
bd update <TEST_PARSER_ID> --acceptance "- [ ] tests/test_parser.py exists
- [ ] All 3 test cases present
- [ ] python -m pytest tests/test_parser.py passes"
```

Note the ID. We'll call it **TEST_PARSER_ID**.

```bash
# Integration test
bd create "Add integration smoke test" -t task -p P2 --stdin << 'EOF'
Create tests/test_integration.py with an integration test that exercises
the full stack.

Mock the HTTP call (use unittest.mock.patch on weatherly.fetcher.requests.get).
Return a realistic wttr.in JSON response fixture.
Call the full chain: fetch → parse → display (capture stdout).
Verify output contains temperature and location strings.
EOF
```
```bash
bd update <TEST_INTEG_ID> --acceptance "- [ ] tests/test_integration.py exists
- [ ] HTTP call is mocked (no real network calls)
- [ ] Full chain executes without errors
- [ ] python -m pytest tests/test_integration.py passes"
```

Note the ID. We'll call it **TEST_INTEG_ID**.

---

## Declare Dependencies

```bash
bd dep add <TEST_PARSER_ID> <BEAD_A>      # test_parser needs models (from Module 3)
bd dep add <TEST_PARSER_ID> <BEAD_B>      # test_parser needs parser (from Module 3)
bd dep add <TEST_INTEG_ID> <WIRING_ID>    # integration test needs full wired app (from Module 4)
```

---

## Stage the Convoy (No Epic Needed)

You can pass bead IDs directly to `gt convoy stage`. No need for a parent epic:

```bash
gt convoy stage <FETCHER_ID> <DISPLAY_ID> <CLI_ID> <WIRING_ID> <TEST_PARSER_ID> <TEST_INTEG_ID>
```

> 💡 **You can also stage an epic** to pick up all its children:
> ```bash
> gt convoy stage edi-000   # stages all child tasks
> ```
> But passing IDs directly works too.

**You'll see real output like:**

```
edi-004 [task] Add weather fetcher (rig: YOUR_RIG) [open]
edi-005 [task] Add terminal display (rig: YOUR_RIG) [open]
edi-006 [task] Add CLI argument parser (rig: YOUR_RIG) [open]
edi-007 [task] Wire weatherly together (rig: YOUR_RIG) [open] ← blocked by: edi-003, edi-004, edi-005, edi-006
edi-008 [task] Add parser unit tests (rig: YOUR_RIG) [open] ← blocked by: edi-002, edi-003
edi-009 [task] Add integration smoke test (rig: YOUR_RIG) [open] ← blocked by: edi-007

Wave   ID       Title                        Rig            Blocked By
─────────────────────────────────────────────────────────────────────────────
1      edi-004  Add weather fetcher           YOUR_RIG  —
1      edi-005  Add terminal display          YOUR_RIG  —
1      edi-006  Add CLI argument parser       YOUR_RIG  —
2      edi-007  Wire weatherly together       YOUR_RIG  edi-003..006
2      edi-008  Add parser unit tests         YOUR_RIG  edi-002, edi-003
3      edi-009  Add integration smoke test    YOUR_RIG  edi-007

6 tasks across 3 waves (max parallelism: 3 in wave 1)
Convoy created: hq-cv-wxyz (status: staged_ready)
```

---

## Reading the Wave Plan

```
WAVE 1 — dispatch immediately on launch (all parallel)
  edi-004  Add weather fetcher         ──┐
  edi-005  Add terminal display          │  all at once
  edi-006  Add CLI argument parser     ──┘

WAVE 2 — dispatch as Wave 1 beads close
  edi-007  Wire weatherly together      ← waits for 003+004+005+006
  edi-008  Add parser unit tests        ← waits for 002+003

WAVE 3 — dispatch when Wave 2 resolves
  edi-009  Add integration smoke test   ← waits for 007
```

**This wave plan is telling you:**
- 3 polecats will spin up immediately on launch
- edi-007 unblocks when all 4 of its blockers close (edi-003 from Module 2 + the three Wave 1 beads)
- edi-008 may run in parallel with edi-007 if edi-002 and edi-003 close first
- edi-009 can't start until the full app is wired

---

## The Staging Safety Net

Imagine you stage and see a problem:

```
⚠ WARNING: edi-008 blocked by edi-003 but edi-003 is not in the staged set
   — dependency on out-of-scope bead may cause edi-008 to never unblock
```

You can fix the dep, then re-stage:

```bash
# Fix the issue
bd dep add <TEST_PARSER_ID> <BEAD_B>

# Re-stage (creates a new staged convoy)
gt convoy stage <FETCHER_ID> <DISPLAY_ID> <CLI_ID> <WIRING_ID> <TEST_PARSER_ID> <TEST_INTEG_ID>
```

Nothing ran, nothing broke. You caught it in the pre-flight.

---

## Launch

```bash
gt convoy launch <CONVOY_ID>
```

Wave 1 dispatches immediately. Polecats spin up in parallel. Walk away. The ConvoyManager handles the rest.

> ⚠️ **Don't run `gt convoy launch` twice on the same convoy.** If it gets interrupted and you re-run it, Gas Town re-stages and creates a NEW convoy tracking the same beads. Check `gt convoy list`. If you see two convoys tracking the same work, close the duplicate: `bd close hq-cv-old -r "duplicate"`. The beads will already be hooked from the first launch.

---

## Monitor Progress

```bash
# Overall convoy progress
gt convoy status <CONVOY_ID>

# Interactive monitoring (updates automatically)
gt convoy -i

# Real-time feed of all events
gt feed

# Who's running right now
gt polecat list YOUR_RIG

# Rig-level view
gt rig status YOUR_RIG
```

---

## After It Lands

```bash
# Check all commits with full attribution
git log --format="%s | %an" -15

# All polecat work history
bd audit --actor=YOUR_RIG/polecats/*

# Performance stats
bd stats --actor=YOUR_RIG/polecats/* --metric=cycle-time
```

---

## ⚠️ One `bd dep add` Gotcha: Parent-Child Direction

When linking tasks to epics with `parent-child`, the direction matters and is easy to get backwards.

**The correct direction:**
```bash
bd dep add <child-id> <parent-id> --type parent-child
# "child depends on parent" = child lives under parent
```

**A quick check:**
```bash
bd show <epic-id>
```
Should show `CHILDREN ↳` pointing to the tasks. If you see `PARENT ↑` there, you've got it backwards.

> 💡 **`parent-child` doesn't affect execution order.** It's purely organizational: for grouping, display, and `gt convoy stage <epic-id>` discovery. Only `blocks` deps control wave order.

---

## 📝 Key Commands Learned

```bash
gt convoy stage <id> [id...]   # validate dep graph + wave plan (INERT)
gt convoy launch <convoy-id>   # dispatch Wave 1, daemon feeds rest
gt convoy -i                   # interactive convoy monitoring
gt rig status YOUR_RIG         # rig-level view of all workers
bd audit --actor=RIG/polecats/* # full attribution history
bd stats --actor=...           # performance metrics
```

---

---

## 📚 Further Reading

- [Convoys](https://docs.gastownhall.ai/concepts/convoy/) — convoy lifecycle, stranded detection
- [Convoy Lifecycle Design](https://docs.gastownhall.ai/design/convoy-lifecycle/) — how wave computation (Kahn's sort) works internally
- [Work Management Commands](https://docs.gastownhall.ai/usage/work-management/) — full `gt convoy` CLI reference

---

## Next: [Module 6 — The Full Pipeline →](module-06-full-pipeline.md)
