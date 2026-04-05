---
description: Interactive product brief generator — conducts a dialog, then writes docs/product-brief.md
argument-hint: <verbiage> [--yolo] [--force]
allowed-tools: Read, Write
---

Create `docs/product-brief.md` — a concise one-page brief capturing vision, problem, capabilities, users, and success. This command **conducts a collaborative dialog** before writing. The user is the domain expert; your job is to ask good questions, synthesize, and write a crisp brief.

Arguments: $ARGUMENTS

## Output & Guards

- Writes to `docs/product-brief.md`.
- If file exists and `--force` is not set → refuse, report existing path, stop.
- If `--yolo` is set → skip dialog, draft from whatever input was given, flag assumptions in the report.

## Canonical Brief Format

Match this shape (under one page, no implementation details):

```markdown
# Project Brief: <product name>

## Vision
<1-2 sentences — the "why we exist" line. Crisp, quotable.>

## The Problem
<A paragraph. What pain does this address? Who feels it? Name the existing
alternative being replaced.>

## What It Does
<Bulleted list of specific capabilities. Optionally include a short
example output block (terminal transcript, sample UI, etc.) if it sharpens
the picture.>

## Who It's For
<One sentence. Concrete user type, not "everyone".>

## Success Looks Like
<One sentence. Observable terms (speed, zero-config, single-command, etc.)
— not aspirational.>
```

No HOW. Tech stack, architecture, and implementation decisions belong in `/design`, not here.

---

## Stage 1: Understand Intent

**Goal:** know WHAT is being briefed before asking anything substantive.

Read `$ARGUMENTS`. Identify:
- **Product name** (may be inferred; if absent, ask for it)
- **Core concept** — what the user is trying to build in one sentence
- **Type** — consumer product / internal tool / developer tool / research project / etc. (affects emphasis)

**If the user supplied substantial verbiage**, summarize your understanding back in 3-5 bullets and ask: *"Did I get the core idea right? Anything else you want to add before I dig in?"*

**If the user supplied only a terse phrase** ("CLI weather dashboard"), ask what the idea is about in their own words — invite a brain-dump. Don't start a structured questionnaire yet.

**Multi-idea disambiguation:** if the user presents several competing ideas, help them pick ONE focus for this brief. Note the others can be briefed separately.

---

## Stage 2: Guided Elicitation

**Skip this stage entirely if `--yolo` flag is set.**

You have the brain-dump. Now fill gaps — but **not as a rigid section-by-section interrogation**. Use these **topics** as a mental checklist, not a script:

### Topic A: Vision & Problem
- What core problem does this solve? For whom?
- How do people solve this today? What's annoying about current approaches?
- What's the insight or angle that makes this different?

### Topic B: Users & Value
- Who experiences this problem most acutely?
- When does a user realize this is what they needed (the "aha moment")?
- How does it fit into their existing workflow?

### Topic C: Scope & Success
- How do we know this is working? What does "good" look like in observable terms?
- What's the minimum version that creates real value?
- What's explicitly NOT in scope for v1?

### Dialog Rules

1. **Lead with what you know.** "Based on your input, it sounds like [X]. Is that right?" — then ask the gap question. Don't re-ask what's already clear.

2. **Targeted questions with options.** Not "who's it for?" — instead "Is the primary user: backend developers, data scientists, sysadmins, or someone else?"

3. **Skip covered topics.** If the brain-dump already nailed Users & Value, don't ask about it.

4. **Capture-don't-interrupt.** If the user volunteers detail beyond brief scope (architecture, tech stack, timelines, pricing), acknowledge briefly ("Good — I'll note that for the design doc") but don't derail into it. Capture it mentally for the eventual `/design` conversation.

5. **Soft gate at every natural pause:** *"Anything else on this, or shall we move on?"* This consistently draws out context users didn't know they had.

6. **Draft early when coverage is good.** If the user is giving confident, complete answers and you've covered all three topics after fewer than 4 exchanges, proactively offer: *"I think I have enough to draft something solid. Ready for me to write it, or is there more you want to add?"*

7. **One round minimum, two rounds maximum.** If critical gaps remain after a second round, proceed to draft and flag assumptions.

**Transition line:** *"I think I have a solid picture. I'll draft the brief now."*

---

## Stage 3: Draft

Write the brief using the canonical format.

**Writing principles:**
- **Crisp voice.** This is a pitch, not a hedge. No "might," "could," "may eventually."
- **Concrete over abstract.** Real user types, real frustrations, observable success.
- **Lead with problem pain.** Make the reader feel it before presenting the solution.
- **Short.** Under one page.
- **No HOW.** No tech stack, no architecture, no implementation.

---

## Stage 4: Review & Write

Before writing to disk, read the draft back to the user and ask:

*"Here's the draft. Does this capture it? Anything to revise before I save?"*

Iterate with the user until they're satisfied. Use the soft gate: *"Happy with this, or want another pass?"*

When user confirms, write the final brief to `docs/product-brief.md`.

---

## Stage 5: Report

Print a one-line summary:

```
Wrote docs/product-brief.md — <product name>.
Next: run /design to work out architecture and decisions.
```

If any sections were filled by inference (user declined to answer, `--yolo` mode, or second-round gaps remained), list them:

```
Assumed:
  - <section>: <what was assumed and why>
  - <section>: <what was assumed and why>
```

If the user volunteered detail that belongs in `/design` (architecture hints, tech choices, implementation notes), list it at the bottom for handoff:

```
Captured for /design:
  - <topic>: <detail>
  - <topic>: <detail>
```
