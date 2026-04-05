---
description: Translate design.md or work-item verbiage into a Gas Town bead plan (bd create commands + dep graph)
argument-hint: <design-path | slug | verbiage> [--slug=name] [--yolo] [--force]
allowed-tools: Read, Write, Glob, Grep
---

Produce `docs/<slug>.bead.md` — a **bead plan** with context, reasoning, `bd create` heredocs, dependency declarations, and convoy launch commands. The payoff command: translates thinking into slingable work.

Arguments: $ARGUMENTS

## Inputs Accepted

| Argument form | Mode | Example |
|---|---|---|
| `docs/design.md` or `design` | **design-driven** — initial full-product plan | `/plan docs/design.md` |
| free-text verbiage | **verbiage-driven** — work-item plan | `/plan "add --forecast flag"` |

The command detects mode automatically: if the argument resolves to an existing file, it's design-driven; otherwise verbiage-driven.

## Output & Guards

- Writes to `docs/<slug>.bead.md`.
- **Slug resolution:**
  - Design-driven: slug = `initial-plan` (or `--slug=name` override).
  - Verbiage-driven: slug = 2-4 content words from verbiage (drop stopwords: add, fix, refactor, and, the, a, an, to, for, in, on). Override with `--slug=name`.
- If output file exists and `--force` not set → refuse, report path, stop.
- `--yolo`: skip the review gate; draft + write in one shot, flag assumptions.

## Output Format

```markdown
# Plan: <title>

> **Source:** <docs/design.md | verbiage quoted>
> **Generated:** <YYYY-MM-DD>
> **Type:** initial | feature | bug | chore
> **Summary:** <N> beads across <W> waves · max parallelism <P> · suggested convoy `<slug>`

## Context

<Quote the verbiage OR link the design doc. One paragraph of what was asked.>

## Reasoning

- **Touches:** <files/modules>
- **Key decisions applied:** <list — either lifted from design.md or made inline>
- **Decomposition rationale:** <why these beads, this order, these deps>
- **Assumptions:** <anything inferred that user should verify>

## Wave Diagram

```
Wave 1 (parallel):    <bead-1>  <bead-2>
Wave 2 (sequential):  <bead-3>
Wave 3 (sequential):  <bead-4>
```

## Beads

### Bead 1: <title>

**Type:** task · **Priority:** P2 · **Depends on:** —

```bash
bd create "<title>" -t task -p P2 --stdin << 'EOF'
<concrete body — files, constants, signatures, literal values from decisions>
EOF
```

```bash
# After creation, capture the returned ID (e.g. edi-001) and add acceptance:
bd update <id> --acceptance "- [ ] <criterion 1>
- [ ] <criterion 2>
- [ ] <criterion 3>"
```

### Bead 2: <title>
...

## Dependencies

After creating all beads, capture their IDs and wire dependencies:

```bash
# Substitute <bead-N> with the actual edi-xxx ID from each bd create
bd dep add <bead-2> <bead-1>   # Bead 2 imports X from Bead 1
bd dep add <bead-4> <bead-2>   # Bead 4 depends on Bead 2's output shape
bd dep cycles                   # verify no cycles
```

## Launch

```bash
gt convoy create "<slug description>" <bead-1> <bead-2> <bead-3> --notify
gt convoy stage <bead-1> <bead-2> <bead-3>
gt convoy launch <convoy-id>
```

## Plan Notes

<any oversized-bead warnings, dep-ambiguity flags, vague-acceptance concerns>
```

---

## Stage 1: Understand Input

Parse `$ARGUMENTS`.

- If it resolves to an existing file (check `docs/<arg>` and `<arg>` directly) → **design-driven mode**, read the file.
- Else treat as **verbiage-driven** — the string IS the work-item description.

Extract or generate slug:
- Design-driven: default `initial-plan`, or use `--slug` if provided, or extract from design doc title.
- Verbiage-driven: slugify the verbiage (2-4 content words, stopwords dropped, hyphenated).

Determine type:
- Design-driven: `initial`
- Verbiage-driven: infer from verb — "add/implement/support" → `feature`, "fix/resolve/repair" → `bug`, "refactor/clean/reorganize" → `chore`, default → `task`

---

## Stage 2: Gather Context

**Always read the brief and design if they exist:**
- `docs/product-brief.md` — what the product is
- `docs/design.md` — decisions + architecture + bead breakdown

**Glance at existing source** to understand the codebase:
- `weatherly/` (or equivalent package dir)
- Entry-point file, recent modules
- Test layout

**Pattern-extract** what's already been built — the bead plan should respect existing conventions (naming, structure, imports).

---

## Stage 3: Clarify (verbiage-driven only, skip if `--yolo`)

If verbiage is terse or key decisions aren't derivable from design.md + existing source, ask targeted questions.

**Ask when:**
- Scope is genuinely ambiguous ("add logging" — to file? to stderr? what level?)
- A concrete value is needed and not in design.md ("forecast window" — 3 days? 5 days?)
- User might prefer one of several reasonable approaches

**Don't ask when:**
- You can infer from design.md + existing code
- The answer is obvious from context
- The question is about style (fill in sensibly, flag as assumption)

**Batch, numbered, one round max.** If gaps remain, fill with best inference and flag in Plan Notes.

---

## Stage 4: Decompose into Beads

**Design-driven:** Each row in design.md's Bead Breakdown table → one bead. Use Key Decisions as literal values in bead bodies.

**Verbiage-driven:** Decompose work into modules/concerns. Each concern → one bead. Apply design.md decisions where relevant.

For each bead, produce:

### Required fields

- **Title** — imperative, short (under ~60 chars). "Add X", "Fix Y", "Refactor Z".
- **Type** — `task` (default), `feature`, `bug`, or `chore`.
- **Priority** — P2 default; escalate P1 if it blocks Wave 1.
- **Body** (the heredoc content) — **concrete, literal, no placeholders**:
  - Exact file path to create or modify
  - Specific constants with values (pulled from design.md decisions)
  - Function signatures with types
  - Field names + types for dataclasses
  - Implementation hints from design doc or brief
- **Acceptance criteria** — 3-5 bullets, each verifiable:
  - "File exists at path"
  - "Import works: `python -c 'from X import Y'`"
  - "Function signature matches: `def f(x: int) -> str`"
  - "Value equals: `DEFAULT_UNITS == 'metric'`"

### Size discipline — flag a bead that:

- Touches more than ~2 files
- Has vague acceptance ("works correctly", "handles errors")
- Mixes unrelated concerns
- Would plausibly exceed a single polecat session

### Dependency inference

Declare a dep when:
- Bead B **imports** a symbol from a file Bead A creates
- Bead B **modifies** a file Bead A creates
- Bead B depends on a **signature/shape** Bead A defines

Don't declare a dep for aesthetic ordering. **False deps kill parallelism.** Record justification for each dep.

### Wave computation

- Wave 1: beads with no blockers
- Wave N: beads whose blockers all resolve in waves 1..N-1

Max parallelism = largest wave size.

---

## Stage 5: Draft

Synthesize everything into the canonical output format. Write the Context and Reasoning sections to explain the plan to a future reader.

Quality rules:
- **Every literal value in a bead body must trace to a decision** — either lifted from design.md or inferred and flagged in Assumptions.
- **No "TBD", no placeholders inside bead bodies.** Polecats don't clarify.
- **Each bead's acceptance is verifiable via a shell command or import check.**

---

## Stage 6: Review (skip if `--yolo`)

Present a summary to the user (NOT the full document):

```
Drafted: docs/<slug>.bead.md
  Type: <type> · <N> beads · <W> waves · max parallelism <P>

Beads:
  Wave 1: Bead 1 (title), Bead 2 (title), ...
  Wave 2: Bead 3 (title)
  Wave 3: Bead 4 (title)

Flags:
  - Bead N: <warning>
  - Dep (X → Y): <justification weak?>

Assumptions:
  - <thing inferred>: <what was chosen and why>

Look right, or want me to revise any bead before saving?
```

If the user requests changes, revise and re-present. When the user confirms, write to `docs/<slug>.bead.md`.

---

## Stage 7: Report

Print a concise summary:

```
Wrote docs/<slug>.bead.md — <N> beads, <W> waves, max parallelism <P>.
Flags: <count> oversized, <count> dep-ambiguous, <count> vague-acceptance.
Next: review the file, then run the bd create block.
```

If flags exist, list them with one-line reasons.

---

## Quality Principles

1. **Literal values, not placeholders.** If design.md says `DEFAULT_UNITS = 'metric'`, the bead body says exactly that.

2. **Beads fit in one polecat session.** One module, one concern, clear output. Oversized beads get flagged.

3. **Acceptance must be verifiable.** `python -c 'from X import Y'` > "module works".

4. **Deps are mechanical, not aesthetic.** Add a dep only when B literally cannot run without A's output.

5. **The .bead.md is a reviewable artifact.** Readable top-to-bottom. Context + Reasoning + Beads + Launch. Committed to git alongside the spec history.
