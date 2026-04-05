---
description: Interactive design document generator — reads the brief, captures decisions, produces docs/design.md
argument-hint: [--yolo] [--force]
allowed-tools: Read, Write, Glob, Grep
---

Create `docs/design.md` — the bridge between product brief and bead plan. This document captures **key decisions, architecture, and a bead breakdown** so downstream beads can be written with concrete literal values instead of guesses.

Arguments: $ARGUMENTS

## Output & Guards

- Reads `docs/product-brief.md` (run `/brief` first if it doesn't exist).
- Writes to `docs/design.md`.
- If `docs/design.md` exists and `--force` is not set → refuse, report path, stop.
- If `--yolo` is set → propose a full design draft from the brief + reasonable defaults, then walk user through refinement rather than interrogating decision-by-decision.

## What This Document Is

The design doc answers *how it will work* — just enough that when you write a bead, every literal value (URLs, timeouts, field names, file paths) traces back to a decision here. **Not a line-by-line spec.** It's the thinking that makes bead bodies concrete.

## Canonical Design Format

Match this shape:

```markdown
# Design Document: <product name>

> **Purpose:** This document captures the design decisions made after
> reading the product brief and before writing beads. It answers the
> questions an agent can't answer for you — what data source, what
> shape, what boundaries.

---

## From Brief to Design

<1-2 paragraph bridge — the brief tells us WHAT; this document answers HOW.>

---

## Key Decisions

### 1. <Decision Name>

**Options considered:**
- <Option A> — <brief pros/cons>
- <Option B> — <brief pros/cons>
- <Option C> — <brief pros/cons>

**Decision:** <chosen option>. <1-sentence rationale tied back to brief>.

**Impact:** <concrete value or code pattern that results — e.g., `API_BASE_URL = 'https://wttr.in'`>

### 2. <Next Decision>
...

---

## Architecture

```
<product>/
  module-a.py    ← what it does
  module-b.py    ← what it does
  ...
```

**Data flow:**
```
<flow diagram — arrows between modules>
```

<1-2 sentences on module philosophy — e.g., "each module has one job, deps
flow one direction".>

---

## Bead Breakdown

| Bead | Module | Depends On | Notes |
|------|--------|------------|-------|
| 1 | <name> | nothing | <why — no deps, clear contract> |
| 2 | <name> | 1 | <why — imports X from bead 1> |
| 3 | <name> | 1 | <why> |
| 4 | <name> | 2, 3 | <why> |

**Why this order matters:** <1 paragraph — what would break if these ran out of order>

---

## What This Document Is Not

This is not a spec. It doesn't tell an agent exactly what to write line by line — that's the bead body's job. This document captures the *reasoning* behind the decisions so when you write a bead, you're not making it up as you go.

---

## Next Step

Run `/plan` to translate this design into a bead plan:

```bash
/plan docs/design.md
```
```

---

## Stage 1: Understand Intent

**Always start by reading `docs/product-brief.md`.** If it doesn't exist, stop and tell the user to run `/brief` first.

Also glance at (lightly) for context:
- `pyproject.toml` / `package.json` / `go.mod` — tech stack signals
- Existing source files — patterns already in place
- `README.md` — how the user describes the project

**Summarize your understanding** back in 3-5 bullets: the product, the user, the success criterion, the tech signals you noticed.

Ask: *"Does that capture the brief correctly? Anything to clarify before I work through decisions?"*

---

## Stage 2: Elicit Decisions

**Identify the decisions that need making** — the ones a polecat cannot answer for itself. Typical categories:

### Category A: External Dependencies
- Data sources, APIs, libraries, services
- Authentication / credentials / API keys
- Third-party tools the project relies on

### Category B: Formats & Protocols
- Response/request formats (JSON shape, CSV columns, etc.)
- File formats (config, data, state)
- Wire protocols, encoding, serialization

### Category C: Defaults & Constraints
- Default values (units, timeouts, retries, page sizes)
- Limits (file size, rate limits, timeouts)
- Failure modes (fail-fast vs retry, silent vs loud)

### Category D: Shape of State
- Config shape (dataclass? dict? env vars?)
- In-memory models (dataclasses? records?)
- Persistence (none? file? database?)

### Dialog Rules (same as /brief)

1. **Lead with what you know.** "The brief says zero-config — that suggests no API key registration. Should we prefer a free/keyless API?"

2. **Propose options with tradeoffs.** Don't ask "what data source?" — instead research and present: *"Three options for weather data: (a) OpenWeatherMap — free tier, requires API key; (b) WeatherAPI — requires key; (c) wttr.in — no key, JSON format, built for terminals. Recommend wttr.in — matches zero-config goal. Accept?"*

3. **Capture the impact** as a literal value. If user picks wttr.in, immediately note: `API_BASE_URL = 'https://wttr.in'`. This is what beads will cite later.

4. **Don't invent decisions the user didn't ask for.** If the brief says nothing about persistence and the scope is CLI-with-no-state, don't propose a database.

5. **Soft gate between categories:** *"That covers data sources and formats. Ready to move to defaults and constraints, or anything else to revisit?"*

6. **`--yolo` mode**: propose the whole decision table upfront with defaults chosen, then invite user to correct any line. Flag assumptions explicitly.

---

## Stage 3: Elicit Architecture

Propose a module layout that reflects the decisions. Keep it tight:

- **One module = one job.** "config holds constants; fetcher does HTTP; parser transforms; display prints."
- **Dependencies flow one direction.** Draw the data flow diagram.
- **Each module is an independent unit of work.** This is what makes beads parallelizable later.

**Present the architecture** and ask: *"Does this module layout match your thinking, or do you want to split/merge/rename anything?"*

Watch for anti-patterns:
- **Modules that touch each other's internals** — bad boundaries
- **Modules that do two unrelated things** — bead sizing problem
- **Circular imports** — will cause dep cycles in beads later

---

## Stage 4: Elicit Bead Breakdown

Now decompose into beads. Default heuristic: **one module = one bead**, unless a module is too big (then split) or two tiny modules naturally pair (then merge).

For each bead, record:
- **Module** (or file) it produces
- **Depends On** — which other beads must finish first (with justification: "imports X from bead N")
- **Notes** — why this bead has the shape it does

**Present the breakdown table** and ask: *"This gives N beads across W waves. Any sizing concerns — beads that look too big, or deps that look aesthetic rather than mechanical?"*

### Bead sizing rules (from the workshop)

- **Good size**: one file, one concern, 3-5 clear acceptance criteria, fits a single polecat session.
- **Flag if**: touches more than 2 files, has vague acceptance, mixes unrelated work.
- **Dep rule**: add a dep only when B literally cannot run without A's output. False deps kill parallelism.

---

## Stage 5: Draft

Synthesize Stages 1-4 into the canonical design format.

**Writing principles:**
- Every Key Decision has **options considered** (even if one is "do nothing"), a decision, and an **impact** stated as a literal value.
- Architecture diagram uses ASCII, fits in the file, shows data flow clearly.
- Bead breakdown is a table, not prose — it's a contract for `/plan`.
- Keep the doc under 2 pages.

---

## Stage 6: Review & Write

Read the draft back to the user. Ask: *"Does this capture the decisions and decomposition? Anything to revise before I save?"*

Iterate until satisfied, then write to `docs/design.md`.

---

## Stage 7: Report

```
Wrote docs/design.md — <N> decisions, <M> modules, <B> beads across <W> waves.
Next: run /plan docs/design.md to produce the bead plan.
```

If any decisions were filled by inference (user punted, `--yolo` used), list them:

```
Assumed decisions:
  - <decision name>: chose <option> because <reason>
  - <decision name>: chose <option> because <reason>
```

Review any flagged deps or sizing concerns at the bottom:

```
Flagged:
  - Bead N: touches 3 files, consider splitting
  - Dep (Bead X → Bead Y): justification is aesthetic, may kill parallelism
```
