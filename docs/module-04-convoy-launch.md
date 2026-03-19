# Module 4: Convoy Launch — Stage, Validate, Launch

> **Goal:** Use the proper `gt convoy stage → launch` flow. Understand what staging gives you that direct slinging doesn't.

> **All commands run from:** `~/gt/YOUR_RIG/crew/claudio`

---

## The Problem with Slinging Directly

When you `gt sling` directly without staging, you're flying blind:

- No dep graph validation (circular deps go undetected until runtime confusion)
- No wave preview (you don't know what will dispatch when)
- No pre-flight abort (work starts immediately, can't cancel)

For small 2-3 bead chains, this is fine. For anything larger, you want the pre-flight.

---

## Stage → Launch: The Two-Phase Flow

```
gt convoy stage <epic-id>
         │
         ▼
   STAGED status (INERT — nothing dispatches)
   Shows:
     ✓ dependency validation
     ✓ wave computation
     ✓ warnings (parked rigs, orphans, etc.)
         │
    user reviews
         │
         ▼
gt convoy launch <convoy-id>
         │
         ▼
   OPEN status
   Wave 1 dispatches immediately (all in parallel)
   ConvoyManager feeds Wave 2+ automatically
```

**Staged convoys are completely inert.** The daemon skips them in both the event poll and the stranded scan. Nothing runs until you explicitly launch.

---

## Setting Up: Add Tests (The Real Wave 3)

Let's add a test layer to weatherly that depends on everything else:

```bash
# Unit tests for the parser (depends on models + parser)
bd create "Add parser unit tests" \
  -t task -p P2 \
  --description "Create tests/test_parser.py with unit tests for the weather parser.

Test cases:
1. test_parse_valid_response: create a minimal valid wttr.in JSON structure, verify all fields parse correctly
2. test_parse_missing_field: pass JSON missing 'current_condition', verify ValueError raised
3. test_parse_invalid_nested: pass JSON with wrong nested structure, verify ValueError

Use Python's unittest.TestCase. Include a sample_response fixture at the top of the file.

Create tests/__init__.py (empty)." \
  --acceptance "- [ ] tests/test_parser.py exists
- [ ] All 3 test cases present
- [ ] python -m pytest tests/test_parser.py passes"

# Integration test (depends on everything)
bd create "Add integration smoke test" \
  -t task -p P2 \
  --description "Create tests/test_integration.py with an integration test that exercises the full stack.

Mock the HTTP call (use unittest.mock.patch on weatherly.fetcher.requests.get).
Return a realistic wttr.in JSON response fixture.
Call the full chain: fetch → parse → display (capture stdout).
Verify output contains temperature and location strings." \
  --acceptance "- [ ] tests/test_integration.py exists
- [ ] HTTP call is mocked (no real network calls)
- [ ] Full chain executes without errors
- [ ] python -m pytest tests/test_integration.py passes"
```

Note IDs: `edi-008`, `edi-009`

---

## Declare the Test Dependencies

```bash
bd dep add edi-008 edi-002   # test_parser needs models
bd dep add edi-008 edi-003   # test_parser needs parser
bd dep add edi-009 edi-007   # integration test needs full wired app
```

---

## Create an Epic to Stage

For `gt convoy stage` to compute waves, you need a parent epic that owns all the work:

```bash
bd create "weatherly MVP" \
  -t epic -p P1 \
  --description "Complete working weatherly CLI weather dashboard"
```

Note ID: `edi-000`

Then make everything a child of the epic using `--type parent-child`:
```bash
bd dep add edi-000 edi-002 --type parent-child
bd dep add edi-000 edi-003 --type parent-child
bd dep add edi-000 edi-004 --type parent-child
bd dep add edi-000 edi-005 --type parent-child
bd dep add edi-000 edi-006 --type parent-child
bd dep add edi-000 edi-007 --type parent-child
bd dep add edi-000 edi-008 --type parent-child
bd dep add edi-000 edi-009 --type parent-child
```

> 💡 **`parent-child` vs `blocks`:** These are completely different relationship types.
> - `parent-child` = organizational hierarchy only. Does **not** affect execution order.
> - `blocks` (default) = execution blocker. Blocked bead cannot start until blocker closes.
>
> The wave computation uses **only** `blocks`-type deps. Parent-child is just for grouping and display.

---

## Stage the Convoy

```bash
gt convoy stage edi-000
```

Expected output:

```
🚚 Staging: weatherly MVP (edi-000)

Dependency Analysis:
  ✓ No circular dependencies detected
  ✓ All rigs available
  ✓ 9 beads analyzed

Wave Plan:
  Wave 1 (3 tasks — dispatch on launch):
    ● edi-002: Add WeatherData dataclass
    ● edi-004: Add weather fetcher
    ● edi-005: Add terminal display
    ● edi-006: Add CLI argument parser
                                            ← edi-003 blocked by edi-002

  Wave 2 (2 tasks — dispatch when Wave 1 resolves):
    ● edi-003: Add weather data parser      ← unblocked when edi-002 closes
    ● edi-008: Add parser unit tests        ← unblocked when edi-002+003 close

  Wave 3 (2 tasks — dispatch when Wave 2 resolves):
    ● edi-007: Wire weatherly together      ← unblocked when edi-003-006 close
    ● edi-009: Add integration smoke test   ← unblocked when edi-007 closes

Convoy: hq-cv-wxyz (staged:ready)

Launch when ready: gt convoy launch hq-cv-wxyz
```

---

## Reading the Wave Plan

```
WAVE 1: The starting gun
┌─────────────────────────────────────────────────────┐
│  edi-002 (models)                                    │ ─┐
│  edi-004 (fetcher)                                   │  │ All parallel
│  edi-005 (display)                                   │  │
│  edi-006 (cli)                                       │ ─┘
└─────────────────────────────────────────────────────┘
                         │ closes trigger...
WAVE 2: Dependencies satisfied
┌─────────────────────────────────────────────────────┐
│  edi-003 (parser)     ← needs edi-002               │ ─┐ Parallel
│  edi-008 (unit tests) ← needs edi-002 + edi-003     │ ─┘
└─────────────────────────────────────────────────────┘
                         │ closes trigger...
WAVE 3: Final integration
┌─────────────────────────────────────────────────────┐
│  edi-007 (main.py)    ← needs edi-003-006            │ ─┐ Parallel
│  edi-009 (int. tests) ← needs edi-007                │ ─┘
└─────────────────────────────────────────────────────┘
```

---

## Launch

```bash
gt convoy launch hq-cv-wxyz
```

Wave 1 dispatches immediately — 4 polecats spawn in parallel. You walk away. The ConvoyManager handles the rest.

---

## Monitor Progress

```bash
# Overall progress
gt convoy status hq-cv-wxyz

# Real-time feed
gt feed

# Who's running (positional arg, not --rig flag)
gt polecat list YOUR_RIG

# Peek at a specific polecat (full address required)
gt peek YOUR_RIG/furiosa

# Rig-level view
gt rig status YOUR_RIG
```

---

## After It Lands

```bash
# Check everything merged
git log --oneline -10

# All attributions
git log --format="%s | Author: %an" -10

# Bead audit
bd audit --actor=YOUR_RIG/polecats/* | head -20

# Polecat performance
bd stats --actor=YOUR_RIG/polecats/* --metric=cycle-time
```

You'll see every commit attributed to the specific polecat that wrote it. Five different polecats, all traceable.

---

## ⚠️ The Staged Convoy Safety Net

Imagine you stage, see warnings, and want to fix before launching:

```bash
gt convoy stage edi-000
# Output: "⚠ WARNING: edi-008 has no clear blocker on edi-003 — may start before parser exists"

# Fix the dep
bd dep add edi-008 edi-003

# Re-stage with updated graph
gt convoy stage edi-000
# Output: "✓ No issues"

gt convoy launch hq-cv-wxyz
```

This is exactly what staging is for — catching issues before any polecat burns tokens on broken work.

---

## 📝 Key Commands Learned

```bash
gt convoy stage <epic-id>       # validate + wave plan (INERT)
gt convoy launch <convoy-id>    # dispatch Wave 1, daemon feeds rest
gt rig status YOUR_RIG          # rig-level view of all workers
bd audit --actor=RIG/polecats/* # full attribution history
bd stats --actor=...            # performance metrics
```

---

## Next: [Module 5 — The Full Pipeline →](module-05-full-pipeline.md)
