# Module 1: From Idea to Beads

> **Goal:** Understand the decision-making work that happens *before* the first bead is created. Learn how an idea becomes a product brief, a brief becomes a design, and a design becomes a concrete bead plan, with every value traced back to a decision.

## What You're Doing in This Module

In this module, you are not assigning work yet.

You are creating the human decision trail that later becomes executable beads.

---

## The Human Layer

Gas Town executes work. It doesn't define it.

Before a polecat can build anything, a human has to answer three questions:

1. **What are we building and why?** (the brief)
2. **How will it work? What decisions need to be made?** (the design)
3. **What units of work can an agent execute independently?** (the bead plan)

These decisions should be made before a polecat ever starts the work. Polecats pick up a bead with a clear body and acceptance criteria, execute, and close. **If the bead body is vague, the output is vague.** The human layer is what makes bead bodies concrete.

---

## The Project: `weatherly`

You want to build a terminal weather CLI. One command, clean output, no config required.

That's a product idea. It's not a bead. It only becomes useful to Gas Town when it is turned into explicit decisions and executable work units.

Let's trace how it becomes one.

---

## Before You Start This Module

This module uses **Claude Code slash commands**, not normal shell commands. The `/brief`, `/design`, and `/plan` commands only work from within an active Claude Code session.

**Where to run it:** Your Gas Town crew workspace. This is where you do human-directed, exploratory work before slinging beads.

```bash
# Open a Claude Code session in your crew workspace
cd ~/gt/YOUR_RIG/crew/YOUR_NAME
claude
```

The slash commands ship with this repo in `.claude/commands/`. No plugin installation needed. They're available automatically when you open Claude Code in your fork's directory.

> 📋 **These files live in your crew workspace, not in the tutorial repo.** The command writes them to `docs/` in your crew working directory. They're *your* artifacts, the decisions you made for your version of weatherly. Keep them separate from the authored workshop content.

---

## Step 1: The Product Brief

A brief answers: what, for who, and what does success look like. No implementation details. Those belong in design.

### Running the command

```bash
/brief "a terminal weather dashboard, one command, no config"
```

> ⚡ **What to expect:** The command doesn't just write a file. It interviews you. Expect 3–5 exchanges where it asks about your motivation, scope, constraints, and success criteria. It synthesizes your answers into a structured brief, then asks you to approve before writing.

### What the conversation feels like

The command's output isn't deterministic. It adapts to what you say. But the *shape* of the conversation is consistent. Here's roughly how it goes:

1. **Brain dump:** it asks you to describe the idea in your own words. What sparked it, what you're picturing, what "no config" means to you.
2. **Clarifying questions:** it identifies gaps: what happens with no arguments? What about units? What's explicitly *not* in v1?
3. **Scope fences:** it confirms what's in and what's out, so the brief has clear boundaries.
4. **Draft and review:** it writes a structured brief and asks if you're happy before saving.

Your exact questions will differ, but the flow is always: **your idea → targeted gaps → scope agreement → written artifact**. **The command is doing product thinking *with* you, not for you.** Every answer you give becomes a constraint that shapes decisions downstream.

> 💡 **Why this matters:** If you'd said "Celsius default" here, it would cascade. The design doc, bead bodies, and test expectations all change. The brief is the root of the decision tree.

### What a good brief captures

The output lands in `docs/product-brief.md`. The key sections:

```markdown
## Vision
Weather in your terminal, instantly. One command, zero config, zero context-switch.

## What It Does
- Looks up current conditions and a short forecast: weatherly dallas
- Auto-detects your location when run with no argument: weatherly
- Defaults to Fahrenheit; --celsius flag switches units

## Success Looks Like
A single command returns a styled forecast in under two seconds, with no
config file, no API key setup, and no prior run required.
```

**Notice what's not here:** no tech stack, no library choices, no file structure. Those are design decisions, not brief decisions.

> 💡 **The brief's job** is to make the *constraint* clear. For weatherly, the constraint is zero config. Everything downstream flows from that single word.

### Brief checkpoint

Before moving on, make sure your brief:
- states the core user experience clearly
- defines what is in scope for v1
- includes at least one concrete success criterion

---

## Step 2: The Design Document

The design answers: *how* will it work? This is where you make decisions: data sources, dependencies, failure modes, module shape. Each decision produces a **concrete value** that will appear verbatim in a bead body.

```bash
# With the command (reads brief, interactive decision elicitation):
/design

# Fast mode:
/design --yolo
```

> ⚠️ **Use `--yolo` only if you already understand the tradeoffs.** For this workshop, the interactive path is better because the decision trail is part of what you're learning.

Output: `docs/design.md`

### What decisions look like

Each decision in the design has the same shape:

```markdown
### 1. Weather Data Source

**Options considered:**
- OpenWeatherMap: requires API key ❌ (violates zero-config)
- WeatherAPI: requires API key ❌ (violates zero-config)
- wttr.in: keyless, JSON endpoint, built for terminals ✅

**Decision:** wttr.in. Only option that honors zero-config in a single call.

**Impact:** `API_BASE_URL = "https://wttr.in"`
```

The "Impact" line is what matters. That's the literal value a bead body will cite. Not "some weather API URL". Exactly `"https://wttr.in"`.

### weatherly's key decisions

| Decision | Options | Chosen | Impact |
|----------|---------|--------|--------|
| Data source | OWM, WeatherAPI, wttr.in | wttr.in | `API_BASE_URL = "https://wttr.in"` |
| Terminal rendering | plain print, ANSI, `rich` | `rich` | `rich>=13` in pyproject.toml |
| HTTP client | urllib, httpx, `requests` | `requests` | `requests>=2.31` in pyproject.toml |
| Units default | F only, F+flag, C+flag | F default, `--celsius` flag | `DEFAULT_UNITS = 'fahrenheit'` |
| Failure mode | retry, fail-fast, cache | fail-fast | fetcher raises, main catches |
| Module shape | monolith, 3-module, full split | full split | config / models / fetcher / parser / display / cli / \_\_main\_\_ |

> 💡 **The brief constrains the design.** Zero-config → no API keys → wttr.in. The decision didn't require a long debate. The constraint made it obvious.

### The architecture

Once the major decisions are made, the design should make the code boundaries obvious.

The design also produces a module layout:

```
weatherly/
  __init__.py    ← package marker
  config.py      ← constants: API_BASE_URL, TIMEOUT, Config dataclass
  models.py      ← WeatherData dataclass
  fetcher.py     ← HTTP GET wttr.in, returns raw dict
  parser.py      ← parses raw dict → WeatherData
  display.py     ← rich-formatted rendering
  cli.py         ← argparse, returns Config
  __main__.py    ← wires pipeline, handles errors
```

And a data flow:

```
__main__.py → cli.py → builds Config from args
            → fetcher.py → raw JSON from wttr.in
            → parser.py → structured WeatherData
            → display.py → printed output
```

Each module has one job. Dependencies flow one direction. This isn't aesthetic. It's what makes the bead breakdown clean.

### Design checkpoint

Before moving on, make sure your design:
- names the key decisions explicitly
- records the concrete impact of each decision
- makes module boundaries and dependency direction obvious

---

## Step 3: The Bead Plan

With decisions made and architecture clear, you can decompose into beads. One module = one bead. The design's dependency structure tells you the order.

```bash
# With the command (reads design.md, produces full bd create commands):
/plan docs/design.md

# Or for a smaller work item without a design doc:
/plan "add --forecast flag to show 5-day instead of 3-day"
```

Output: `docs/initial-plan.bead.md`

### What the bead plan produces

The plan is a reviewable markdown file containing ready-to-run `bd create` commands with heredocs, acceptance criteria, dependency wiring, and convoy launch:

```bash
bd create "Add config constants and rich dependency" -t task -p P1 --stdin << 'EOF'
Create weatherly/config.py and update pyproject.toml.

weatherly/config.py:
  - API_BASE_URL: str = "https://wttr.in"
  - DEFAULT_FORMAT: str = "j1"
  - DEFAULT_UNITS: str = "fahrenheit"
  - REQUEST_TIMEOUT: int = 10
  - A Config dataclass with location, units, and format fields

pyproject.toml:
  - Add "rich>=13" to [project] dependencies
EOF
```

Every value in that heredoc (`"https://wttr.in"`, `"j1"`, `"fahrenheit"`) traces back to a decision in the design doc. **The polecat doesn't invent these. You did.**

### The wave breakdown

The design's dependency structure maps directly to execution waves:

```
Wave 1:  config.py (no deps, everyone imports from this)
Wave 2:  fetcher.py + parser.py (parallel, both only need config)
Wave 3:  display.py (needs WeatherData from models)
Wave 4:  cli.py (wires everything, last)
```

Fetcher and parser run in parallel because they never import each other. They communicate through a raw dict. That's not an accident; the design explicitly kept them decoupled so they'd parallelize cleanly.

### Plan checkpoint

Before moving on, make sure your bead plan:
- maps each bead to a clear unit of work
- encodes dependencies in the same order implied by the design
- includes concrete values that trace back to design decisions

---

## The Connection

Here's why this matters:

```
Product Brief         "zero config"
      ↓
Design Decision       data source = wttr.in (no API key needed)
      ↓
Bead Body             API_BASE_URL = "https://wttr.in"
      ↓
Polecat Output        fetcher.py using that exact URL
```

The polecat never had to guess. Every literal value in the bead was decided by a human who read the brief and made a tradeoff. That's the chain.

---

## Manual vs Slash Commands

You don't need the slash commands. The documents they produce are just markdown files. You can write them by hand. The commands speed up the elicitation, but the *thinking* is the same either way.

What matters is that the documents exist **before** you write the first bead. Not as a formality, but as a decision record. Six weeks from now when a polecat touches fetcher.py, it will read the design doc and know exactly why `DEFAULT_UNITS = 'fahrenheit'` instead of `'metric'`.

---

## Before You Continue

You should now have these files in `docs/` in your current crew workspace:
- `docs/product-brief.md`: vision, problem, success criteria
- `docs/design.md`: key decisions with concrete impacts, architecture, bead breakdown
- `docs/initial-plan.bead.md`: ready-to-run `bd create` commands

> 📋 **Staying on track:** The rest of the tutorial assumes the core weatherly constraints: zero config, wttr.in, Fahrenheit default with `--celsius` flag. As long as your output kept those, you're good.

Take a few minutes to read them before moving on. The next module executes the first bead from that plan, and understanding where it came from is the point.

```bash
cat docs/product-brief.md
cat docs/design.md
cat docs/initial-plan.bead.md
```

---

## 📝 Key Concepts

| Concept | What it answers | Output |
|---------|----------------|--------|
| Brief | What + why | `docs/product-brief.md` |
| Design | How + what decisions | `docs/design.md` |
| Bead plan | What units of work | `docs/initial-plan.bead.md` |

**Slash commands:**
```bash
/brief "your idea"      # guided brief → docs/product-brief.md
/design                 # reads brief → docs/design.md
/plan docs/design.md    # reads design → docs/initial-plan.bead.md
```

---

---

## 📚 Further Reading

- [Molecules](https://docs.gastownhall.ai/concepts/molecules/) — how Gas Town structures multi-step workflows
- [Why These Features?](https://docs.gastownhall.ai/other/why-these-features/) — why accountability and traceability matter at scale
- [Gas Town Reference](https://docs.gastownhall.ai/reference/) — technical reference for Gas Town internals

---

## Next: [Module 2 — Your First Bead →](module-02-first-bead.md)
