# Module 5: The Full Pipeline

> **Goal:** Run the complete design-to-delivery pipeline using the gt-toolkit formula workflow. Experience how spec → plan → beads → swarm works as an integrated system, run interactively in a crew session.

---

## What We've Been Doing vs What We Should Be Doing

In Modules 1-4, you manually:
- Wrote bead descriptions
- Figured out dependencies yourself
- Created beads one at a time
- Set up convoys manually

This worked because you knew exactly what to build. In real projects, you often don't. You have a brief and a codebase, and you need to figure out:
- What are the actual scope questions?
- What are the right phases?
- Which files does this touch?
- What are the acceptance criteria for each task?
- What depends on what?

**The gt-toolkit pipeline does this for you** — with multi-LLM review at every stage.

---

## The Pipeline

```
Your idea (1 sentence)
         │
         ▼
┌─────────────────────────────┐
│  SPEC PHASE (Stages 1-4)    │  ← runs in crew session
│                             │
│  1. Scope Questions         │  → 3x3 LLM matrix surfaces blind spots
│  2. Brainstorm              │  → interactive dialogue → validated spec
│  3. Questions Interview     │  → completeness check, loops until clean
│  4. Multimodal Review       │  → 3 models review in parallel, you gate "go"
└────────────┬────────────────┘
             │ outputs: plans/{feature}/02-spec/spec.md
             ▼
┌─────────────────────────────┐
│  PLAN PHASE (Stages 5-6)    │  ← runs in crew session
│                             │
│  5. Plan Writing            │  → deep codebase analysis → phased plan
│  6. Plan Review             │  → 3-directional review
└────────────┬────────────────┘
             │ outputs: plans/{feature}/03-plan/plan.md
             ▼
┌─────────────────────────────┐
│  BEADS PHASE (Stages 7-8)   │  ← runs in crew session
│                             │
│  7. Beads Creation          │  → 3 review passes → creates beads with deps
│  8. Beads Review            │  → bidirectional plan↔beads verification
└────────────┬────────────────┘
             │ outputs: verified beads hierarchy
             ▼
┌─────────────────────────────┐
│  DELIVERY (Stage 9)         │  ← you launch, polecats execute
│                             │
│  gt convoy stage → launch   │  → swarm of polecats in parallel waves
└─────────────────────────────┘
```

---

## Why This Runs in a Crew Session

Stages 2, 3, 4, 5, 6 are **interactive** — they need a human in the loop:
- Stage 2 asks you to make scope decisions
- Stage 3 asks clarifying questions if it finds gaps
- Stage 4 presents findings and asks "go or fix?"
- Stage 5 asks architecture questions
- Stage 6 may escalate ambiguities

A polecat can't do this — it's ephemeral and headless. A crew session is persistent and interactive. That's why crew exists.

---

## Step 1: Start (or Attach to) Your Crew Session

```bash
# Start the session (creates a tmux window with Claude Code running inside)
gt crew start claudio

# Attach your terminal to it
gt crew at claudio
```

> 💡 **`gt crew start` vs `gt crew at`:**
> - `start` creates a new tmux session with Claude Code running inside it
> - `at` attaches your terminal to an already-running session
>
> After `gt crew start`, you'll see a Claude Code session open. This is your crew agent — it has already run `gt prime` and knows its identity as `YOUR_RIG/crew/claudio`.

You're now inside the crew session. Your identity: `YOUR_RIG/crew/claudio`. Working directory: `~/gt/YOUR_RIG/crew/claudio/`.

> 💡 **The crew session is interactive.** Unlike polecats (which run headless), crew sessions are attached to your terminal. The formula workflows have dialogue steps that require your input — you'll read the output and respond directly in the session.

---

## Step 2: Install the Formulas (One-Time)

If you haven't already:

```bash
cp ~/source/gt-toolkit/formulas/*.formula.toml ~/gt/.beads/formulas/
```

Verify:
```bash
gt formula list
```

You should see `spec-workflow`, `plan-workflow`, `beads-workflow`, and the expansion formulas.

---

## Step 3: Run the Spec Pipeline

We're going to add a **v2 feature**: add a 5-day forecast to weatherly.

**From your terminal** (not from inside the crew session — sling TO the crew session):
```bash
cd ~/gt
gt sling spec-workflow YOUR_RIG/crew/claudio \
  --var feature="5-day-forecast" \
  --var brief="Add a 5-day weather forecast to weatherly. Show each day's high/low temps, precipitation probability, and conditions. Display in the same terminal-friendly format as current weather."
```

> ⚠️ **Where to run this:** Run `gt sling` from `~/gt` in a separate terminal window. The crew session receives the sling and starts working. Then `gt crew at claudio` to attach and interact with the running workflow.

This slinging kicks off a molecule in your crew session. Because you're in the crew session, you'll see it start immediately (Propulsion Principle).

**What you'll experience interactively:**

### Stage 1: Scope Questions (automated)
The formula dispatches Opus/GPT/Gemini in a 3x3 matrix. You wait ~2 minutes while 9 parallel analyses run. Output: `plans/5-day-forecast/01-scope/questions.md`

### Stage 2: Brainstorm (interactive)
The crew session presents you with a triaged list of scope questions:
```
AUTO-ANSWERABLE (I'll handle these):
  • Should use existing Config dataclass ✓
  • Should reuse existing display patterns ✓
  • ...

BRANCH POINTS (your decision needed):
  1. Forecast data structure: separate ForecastDay dataclass, or extend WeatherData?
  2. Display format: side-by-side columns or stacked days?
  3. API endpoint: wttr.in supports forecast=3, forecast=7 — which default?
```

You answer each one. The spec gets written incrementally.

### Stage 3: Questions Interview (semi-interactive)
Reviews the spec for completeness. May ask 1-2 clarifying questions. Usually clean after stage 2.

### Stage 4: Multimodal Review (interactive gate)
Three models review the spec in parallel. You see findings:
```
P0 Issues (must fix before proceeding):
  • Spec doesn't mention how to handle missing forecast data from API

P1 Issues (recommend fixing):
  • Acceptance criteria for 'precipitation probability' are vague

P2 (suggestions):
  • Consider adding a --days flag to control forecast depth
```

You choose: fix them, accept them, or skip. Spec updates. You gate "go."

**Output:** `plans/5-day-forecast/02-spec/spec.md` — a reviewed, complete specification.

---

## Step 4: Run the Plan Pipeline

```bash
gt sling plan-workflow YOUR_RIG/crew/claudio \
  --var feature="5-day-forecast"
```

**What you'll experience:**

### Stage 5: Plan Writing (interactive)
Three Sonnet agents run parallel codebase analysis:
- Agent 1: architecture and existing patterns
- Agent 2: integration points (what weatherly/models.py looks like, what parser.py does)
- Agent 3: conventions and style

They consolidate. Then an interactive session builds the implementation plan:
```
Based on codebase analysis, I'm proposing:

Phase 1: Data layer
  • Extend models.py with ForecastDay dataclass
  • Extend parser.py with parse_forecast() function

Phase 2: Display layer  
  • Extend display.py with display_forecast() function

Phase 3: Wire up
  • Update cli.py with --forecast flag
  • Update __main__.py to conditionally call forecast functions

Does this phasing make sense? Any concerns?
```

You respond. Plan gets written.

### Stage 6: Plan Review (automated + escalation)
Three agents review: spec→plan coverage, plan→spec traceability, plan→codebase alignment. Auto-applies fixes, only escalates genuine ambiguities.

**Output:** `plans/5-day-forecast/03-plan/plan.md` — deep, codebase-aware implementation plan.

---

## Step 5: Run the Beads Pipeline

```bash
gt sling beads-workflow YOUR_RIG/crew/claudio \
  --var feature="5-day-forecast"
```

**What you'll experience:**

### Stage 7: Beads Creation (interactive + automated)
The formula reads the plan and builds a draft hierarchy:
```
Feature Epic: 5-day-forecast
├── Phase 1: Data Layer
│   ├── Add ForecastDay dataclass to models.py
│   └── Add parse_forecast() to parser.py (blocked by ForecastDay)
├── Phase 2: Display Layer
│   └── Add display_forecast() to display.py
└── Phase 3: Wire Up
    ├── Update cli.py with --forecast flag
    └── Update __main__.py to use forecast (blocked by all above)
```

Then 3 automated review passes:
1. **Completeness** — every plan task has a bead? All ACs preserved?
2. **Dependencies** — false blockers? Missing blockers? Circular deps?
3. **Clarity** — each bead implementable by a fresh agent?

Fixes applied. Then beads are created via `bd create` with `--deps` at creation time.

### Stage 8: Beads Review (automated)
Bidirectional verification. Plan→Beads: every plan task covered? Beads→Plan: every bead traces to the plan? Dep integrity: graph matches plan phasing?

**Output:** Verified beads hierarchy with IDs mapped in `plans/5-day-forecast/04-beads/beads-report.md`.

---

## Step 6: Stage and Launch

```bash
# Get the feature epic ID from beads-report.md
cat plans/5-day-forecast/04-beads/beads-report.md | grep "Feature epic:"

# Stage
gt convoy stage <epic-id>

# Review the wave plan, then launch
gt convoy launch <convoy-id>
```

Walk away. The ConvoyManager handles the rest.

---

## The Output Structure

After the pipeline completes:

```
plans/5-day-forecast/
  01-scope/
    context.md           ← codebase snapshot used for analysis
    questions.md         ← synthesized P0-P3 question backlog
    question-triage.md   ← auto vs interactive decisions
  02-spec/
    spec.md              ← reviewed design specification
    spec-review.md       ← multi-model review findings
  03-plan/
    plan.md              ← phased implementation plan with file-level mapping
    plan-context.md      ← deep codebase analysis
    plan-review.md       ← 3-directional review findings
  04-beads/
    beads-draft.md       ← full structure before creation
    beads-report.md      ← creation report with ID mapping
    beads-review.md      ← bidirectional review findings
```

This is the audit trail. For any future question of "why was this built this way?" — it's all here, timestamped and attributed.

---

## What the Pipeline Gives You That Manual Bead Creation Doesn't

| | Manual (Modules 1-4) | Pipeline (Module 5) |
|--|---|---|
| Scope analysis | You figure it out | 3x3 LLM matrix, P0-P3 priority |
| Spec quality | As good as your first draft | Multi-model reviewed, completeness-checked |
| Codebase awareness | You read the code | 3 parallel agents analyze patterns, integration points, conventions |
| Bead descriptions | You write them | Generated from plan + 3 quality passes |
| Dependency graph | You reason about it | Topological sort from explicit plan phases |
| False blockers | Easy to miss | Automated review pass removes them |
| Vague criteria | Common | Clarity pass flags and fixes vague language |

---

## 📝 Key Commands Learned

```bash
gt crew start claudio                   # start crew session
gt crew at claudio                      # attach terminal
gt formula list                         # see available formulas
gt sling spec-workflow RIG/crew/name \  # full spec pipeline
  --var feature="X" --var brief="Y"
gt sling plan-workflow RIG/crew/name \  # plan pipeline
  --var feature="X"
gt sling beads-workflow RIG/crew/name \ # beads pipeline
  --var feature="X"
```

---

## Next: [Module 6 — Recovery →](module-06-recovery.md)
