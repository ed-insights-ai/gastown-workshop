# Module 5: The Full Pipeline

> **Goal:** Use Gas Town's native formula workflows — `mol-idea-to-plan` for design and `shiny` for implementation — instead of manually creating beads. Experience how the full pipeline works end-to-end in a crew session.

---

## Two Workflows, One Pipeline

Gas Town ships with two key formulas that handle the full lifecycle:

```
Your idea (1 sentence)
         │
         ▼
┌─────────────────────────────────────┐
│  mol-idea-to-plan                   │  ← runs in crew session
│                                     │
│  intake:         structure PRD      │
│  prd-review:     6 polecats review  │  autonomous
│  human-clarify:  you answer Qs      │  ← your input
│  generate-plan:  6 polecats design  │  autonomous
│  plan-review:    5 polecats review  │  autonomous
│  human-approve:  you greenlight     │  ← your input
│  create-beads:   beads created      │  autonomous
└────────────────────────────────────-┘
         │ outputs: beads hierarchy with deps
         ▼
┌──────────────────────────────────────┐
│  gt convoy stage → launch            │  you do this
│                                      │
│  Polecats execute each bead using    │
│  the `shiny` formula:                │
│    design → implement → review       │
│           → test → submit           │
└──────────────────────────────────────┘
```

**Two human gates** in the whole process:
1. After PRD review — you answer clarifying questions
2. After plan review — you approve before beads are created

Everything else is autonomous.

---

## The `shiny` Formula: What Polecats Actually Do

Every bead a polecat picks up runs the `shiny` formula under the hood — "Engineer in a Box":

```
design     → think about architecture, write design doc
implement  → write the code following the design
review     → self-review: does it match the design? any bugs?
test       → write and run tests, fix regressions
submit     → final check, commit, push to feature branch
```

This is why polecats consistently produce better output than raw "write this code" instructions — they're following a structured workflow with acceptance criteria at each step. You can also sling `shiny` directly to a polecat for any single bead.

---

## Why This Runs in a Crew Session

The `mol-idea-to-plan` workflow has two interactive steps where it pauses and waits for you. A polecat can't do this — it's headless and ephemeral. A crew session is persistent and interactive — you attach to it, answer the questions, and the workflow continues.

---

## Step 1: Start Your Crew Session

```bash
# Start the tmux session with Claude Code inside
gt crew start claudio

# In a separate terminal, attach to it
gt crew at claudio
```

Once attached, you'll see a Claude Code prompt inside `~/gt/YOUR_RIG/crew/claudio/`. This is your crew agent — it has already run `gt prime` and knows its identity.

> 💡 **Two windows:** Keep two terminal windows open. Window 1: your normal shell for running `gt` commands. Window 2: attached to the crew session via `gt crew at claudio`. The crew session is where the interactive pipeline runs.

---

## Step 2: Sling `mol-idea-to-plan` to the Crew Session

From your **normal shell** (Window 1):

```bash
cd ~/gt
gt sling mol-idea-to-plan YOUR_RIG/crew/claudio \
  --var problem="Add a 5-day weather forecast to weatherly. Show each day's high/low temps, precipitation probability, and conditions summary. Should integrate with the existing display module and be triggered by a --forecast flag." \
  --var context="weatherly is a Python CLI that calls wttr.in API. Existing modules: config.py, models.py, parser.py, fetcher.py, display.py, cli.py, __main__.py"
```

Then **attach to the crew session** (Window 2) to watch and interact:

```bash
gt crew at claudio
```

---

## Step 3: The Autonomous Phases

The crew agent picks up the sling immediately (Propulsion Principle) and starts. **You don't need to watch** — but you can:

```bash
tmux capture-pane -t edi-crew-claudio -p | tail -30   # watch raw output
gt feed                                                 # town-wide event stream
```

### intake — PRD Drafting (autonomous, ~2 min)
Agent reads the codebase and structures your problem statement into a PRD draft at `.prd-reviews/{slug}/prd-draft.md`. No input needed.

### prd-review — 6-Dimensional Review (autonomous, ~5 min)
6 parallel subagents review the PRD from different angles: requirements, gaps, ambiguity, feasibility, scope, stakeholders. Results synthesized into a consolidated question list.

> 💡 **Note on `mol-prd-review`:** If the formula is installed, Gas Town spins up polecats for each leg. If not (it may be missing from your install), the crew agent runs the review itself using parallel subagents. Either way the output is the same — you won't notice the difference.

---

## Step 4: Your First Gate — `human-clarify`

**The human gates use mail, not terminal input.** The crew agent pauses and sends you a mail message with the questions. You read it, reply, then nudge to continue.

```bash
# Check your inbox
gt mail inbox

# Read the questions (message 1 is the newest)
gt mail read 1
```

You'll see something like:
```
Subject: PRD Questions: weatherly 5-day forecast
From: edinsights_ui/claudio

## Overall PRD Health: B-

## Questions Needing Your Input

### Must-Answer (Blocks Implementation)
1. Output format: (a) table (b) stacked blocks (c) compact single-line?
2. Forecast window: (a) today+4 days (b) tomorrow+4 days?
3. Precipitation: (a) max hourly (b) average (c) daily summary?
4. Flag behavior: (a) forecast only (b) current + forecast?
5. API limit: (a) use whatever wttr.in supports (b) hard-require 5?

### Should-Answer (Prevents Rework)
6-10. [recommendations included, your call]

Reply with numbered answers.
```

**Reply via mail and nudge to continue:**
```bash
gt mail send edinsights_ui/claudio \
  --subject "Re: PRD Questions: weatherly 5-day forecast" \
  --reply-to <message-id-from-inbox> \
  --stdin << 'EOF'
1. (b) Stacked blocks, one per day
2. (a) Today + 4 future days
3. (a) Maximum hourly value (worst-case)
4. (b) Show current weather THEN forecast below
5. (a) Use whatever wttr.in supports
6-10. Accept recommendations.
Proceed to plan generation.
EOF

gt nudge edinsights_ui/claudio "Answers sent. Proceed with plan generation."
```

---

## Step 5: The Plan Generation Phase

### generate-plan — 6-Dimensional Design (autonomous, ~8 min)
6 parallel subagents design the implementation from different angles: API, data model, UX/display, integration, error handling, testing. Each writes design artifacts to disk.

### plan-review — 5-Legged Review (autonomous, ~5 min)
5 reviewers check: completeness, sequencing, risk, scope creep, testability. Verdict: GO or REVISE.

---

## Step 6: Your Second Gate — `human-approve`

Same pattern — mail arrives, you read and reply.

```bash
gt mail inbox       # new message from claudio
gt mail read 1
```

You'll see:
```
Subject: Plan Ready for Approval: weatherly 5-day forecast

Plan Review Verdict: GO (all 5 dimensions)

## Must-Fix Items
1. Verify wttr.in field names before coding parser
2. Guard empty hourly arrays (max() on empty crashes)
3. Guard missing conditions with fallback

## Implementation Plan (4 Waves)
Wave 1: models.py + cli.py (--forecast flag)
Wave 2: fetcher.py + parser.py (parse_forecast)
Wave 3: display.py (display_forecast, stacked blocks)
Wave 4: __main__.py (integration) + tests

Reply: APPROVE / APPROVE WITH NOTES / REVISE
```

```bash
gt mail send edinsights_ui/claudio \
  --subject "Re: Plan Ready for Approval: weatherly 5-day forecast" \
  --reply-to <message-id> \
  --stdin << 'EOF'
APPROVE

Proceed to bead creation.
EOF

gt nudge edinsights_ui/claudio "Approved. Create the beads."
```

---

## Step 7: Automatic Bead Creation

The agent creates the full bead hierarchy autonomously. Watch `gt feed` or just wait — it takes about 1-2 minutes. When done, the crew session goes idle and reports:

```
Ready to dispatch: edi-d0x and edi-7hm are unblocked (Wave 1).
Awaiting your next instruction.
```

Check what was created:
```bash
cd ~/gt/edinsights_ui/crew/claudio
bd list | grep -v "wisp\|Patrol\|Refinery"
```

You'll see something like:
```
○ edi-d0x ● P2  Add ForecastDay and Forecast dataclasses to models.py
○ edi-7hm ● P2  Add --forecast flag to CLI argument parser
○ edi-ig4 ● P2  Implement fetch_weather() for wttr.in API
○ edi-izs ● P2  Implement parse_forecast() for daily forecast extraction
○ edi-8me ● P2  Implement display_forecast() with stacked blocks output
○ edi-rs6 ● P2  Wire --forecast through main() pipeline
○ edi-csx ● P2  Add unit and integration tests for forecast feature
```

Real beads, real dependencies, created from an approved plan. Total time from idea to beads: ~20 minutes. Human time invested: answering ~15 questions across 2 gates.

---

## Step 8: Stage and Launch

From Window 1:

```bash
cd ~/gt
gt convoy stage edi-010
```

You'll see the real wave output:

```
Wave   ID       Title                           Blocked By
───────────────────────────────────────────────────────────────
1      edi-011  Add ForecastDay dataclass        —
1      edi-014  Update cli.py --forecast flag    —
2      edi-012  Add parse_forecast()             edi-011
2      edi-013  Add display_forecast()           edi-011
3      edi-015  Wire forecast into __main__.py   edi-012, 013, 014
3      edi-016  Add forecast parser tests        edi-011, 012
4      edi-017  Add forecast integration test    edi-015

7 tasks across 4 waves (max parallelism: 2 in wave 1)
Convoy created: hq-cv-forecast (status: staged_ready)
```

Launch it:
```bash
gt convoy launch hq-cv-forecast
```

Then monitor:
```bash
gt convoy -i     # interactive dashboard
gt feed          # event stream
```

Walk away. The ConvoyManager handles waves 2, 3, and 4 automatically.

---

## The `shiny` Formula in Action

Each polecat picks up its bead and runs `shiny` steps:

```
[Wave 1] furiosa picks up edi-011 (ForecastDay dataclass)
  → design:    writes design doc for ForecastDay structure
  → implement: creates models.py additions
  → review:    checks against design doc
  → test:      writes/runs unit tests
  → submit:    commits, pushes branch

[Wave 1] nux picks up edi-014 (cli.py --forecast flag)  
  → same shiny loop, simultaneously
```

You can peek at any step:
```bash
gt peek YOUR_RIG/furiosa    # see what step furiosa is on
```

---

## Running `shiny` Directly on a Single Bead

For any single bead where you want the full design-implement-review-test-submit lifecycle:

```bash
gt sling shiny YOUR_RIG --var feature="edi-042" --var assignee="edinsights_ui/crew/claudio"
```

Or sling a bead to a rig and `shiny` applies automatically via `mol-polecat-work`:
```bash
gt sling edi-042 YOUR_RIG
# shiny runs automatically as part of mol-polecat-work
```

---

## Pipeline vs Manual: What You Gain

| | Manual (Modules 1-4) | Pipeline (Module 5) |
|--|---|---|
| Spec quality | Your first draft | 6-leg PRD review, you answer gaps |
| Implementation plan | You reason about it | 6-dimensional parallel design |
| Plan validation | Your gut | 5-leg review (completeness, risk, scope) |
| Bead descriptions | You write them | Generated from approved plan |
| Dependency graph | You declare it | Agent computes from plan phases |
| Polecat workflow | raw bead | structured: design→implement→review→test→submit |
| Human time required | High (write everything) | Low (answer 2 gates) |

---

## ⏱️ Realistic Timing

From `gt sling mol-idea-to-plan` to beads ready:
- intake + PRD draft: ~2 min
- 6-leg PRD review: ~5 min
- human-clarify gate (you): 2-5 min to read + reply
- 6-dimensional plan design: ~8 min
- 5-leg plan review: ~5 min
- human-approve gate (you): 2-5 min to read + approve
- bead creation: ~2 min
- **Total: ~20-30 min, ~2-5 min of your time**

## 📝 Key Commands Learned

```bash
gt crew start claudio --rig YOUR_RIG    # start crew session
gt crew list YOUR_RIG                   # verify it's running
gt formula list                         # see all available formulas

# Sling the pipeline (from ~/gt, NOT inside crew session)
gt sling mol-idea-to-plan YOUR_RIG/crew/claudio \
  --var problem="..." \
  --var context="..."

# Monitor progress
tmux capture-pane -t edi-crew-claudio -p | tail -30
gt feed

# Human gates (mail-based)
gt mail inbox                           # check for questions/approval requests
gt mail read 1                          # read the message
gt mail send edinsights_ui/claudio \
  --subject "Re: ..." \
  --reply-to <message-id> \
  --stdin << 'EOF'
your answers here
EOF
gt nudge edinsights_ui/claudio "..."    # wake the crew agent to continue

# After bead creation
bd list | grep -v "wisp\|Patrol"        # see created beads
gt convoy stage <epic-id>               # validate + wave plan
gt convoy launch <convoy-id>            # kick off implementation
gt convoy -i                            # watch progress
```

---

## Next: [Module 6 — Recovery →](module-06-recovery.md)
