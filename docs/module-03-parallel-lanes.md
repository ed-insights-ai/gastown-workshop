# Module 3: Parallel Lanes

> **Goal:** Sling multiple independent beads simultaneously and watch them execute in parallel. Understand wave computation and when parallelism is safe.

> **All commands run from:** `~/gt/YOUR_RIG/crew/claudio`

---

## The Problem: Sequential Work is Slow

In Module 2, work ran sequentially because of a real dependency. But what if three things are genuinely independent? Running them one after another wastes time — they could all run at once.

Gas Town's answer: **parallel lanes**. Multiple polecats working simultaneously on independent beads.

---

## The Structure

We need three more weatherly modules, all independent of each other (they don't import each other, don't modify the same files):

```
edi-004: Add weather fetcher        (HTTP calls to wttr.in API)
edi-005: Add terminal display       (rich/colorama output)
edi-006: Add CLI argument parser    (argparse setup)

     ↓            ↓            ↓
 (independent) (independent) (independent)
     │            │            │
     └────────────┴────────────┘
                  │
                  ▼ all blocked by:
edi-007: Wire it all together       (main.py imports fetcher, parser, display, CLI)
```

---

## Step 1: Create the Three Independent Beads

```bash
# Fetcher
bd create "Add weather fetcher" \
  -t task -p P2 \
  --description "Create weatherly/fetcher.py that makes HTTP requests to wttr.in.

Import Config from weatherly.config.
Function signature: def fetch_weather(config: Config) -> dict

Implementation:
- Use requests library
- URL: f'{config.api_base_url}/{config.location}?format={config.format}&lang=en'
- Timeout: config.request_timeout
- Return: parsed JSON (response.json())
- Raise: requests.exceptions.RequestException on network failure
- Raise: ValueError if response status is not 200" \
  --acceptance "- [ ] File exists at weatherly/fetcher.py
- [ ] fetch_weather function defined with correct signature
- [ ] Uses requests library with timeout
- [ ] Raises correct exception types
- [ ] Returns dict (parsed JSON)"

# Display
bd create "Add terminal display" \
  -t task -p P2 \
  --description "Create weatherly/display.py that prints weather data to the terminal.

Import WeatherData from weatherly.models.
Function signature: def display_weather(data: WeatherData) -> None

Output format (example):
  📍 London, United Kingdom
  🌡  Temperature: 15°C (59°F), feels like 13°C
  💧  Humidity: 72%
  🌬  Wind: 18 km/h NW
  ☁   Partly cloudy

Use Unicode emoji for visual appeal. No external libraries required (just print statements)." \
  --acceptance "- [ ] File exists at weatherly/display.py
- [ ] display_weather function defined
- [ ] Outputs all WeatherData fields with emoji labels
- [ ] No import errors"

# CLI
bd create "Add CLI argument parser" \
  -t task -p P2 \
  --description "Create weatherly/cli.py that parses command-line arguments.

Use Python's argparse stdlib (no third-party CLI libs).
Function signature: def parse_args() -> Config

Arguments:
- location (positional): city name or 'auto' for IP-based detection
- --units: 'metric' or 'imperial' (default: 'metric')
- --format: output format string (default: 'j1')
- -v/--verbose: flag for verbose output (store_true)

Import Config from weatherly.config and return a populated Config instance." \
  --acceptance "- [ ] File exists at weatherly/cli.py
- [ ] parse_args() returns Config instance
- [ ] All arguments defined correctly
- [ ] --help output is clear and includes all arguments"
```

Note the IDs: `edi-004`, `edi-005`, `edi-006`

---

## Step 2: Create the Wiring Bead (blocked by all three)

```bash
bd create "Wire weatherly together in main.py" \
  -t task -p P2 \
  --description "Create weatherly/__main__.py that wires all modules together.

Import and call:
- parse_args() from weatherly.cli → Config
- fetch_weather(config) from weatherly.fetcher → dict
- parse_weather(json_data) from weatherly.parser → WeatherData
- display_weather(data) from weatherly.display → None

Add top-level error handling:
- requests.exceptions.RequestException → print 'Network error: ...' + exit(1)
- ValueError → print 'Data error: ...' + exit(1)

Entry point: if __name__ == '__main__': main()

Also create weatherly/__init__.py (can be empty)." \
  --acceptance "- [ ] File exists at weatherly/__main__.py
- [ ] All modules imported and called in correct order
- [ ] Error handling for network and data errors
- [ ] python -m weatherly London runs without import errors
- [ ] weatherly/__init__.py exists"
```

Note the ID: `edi-007`

---

## Step 3: Declare Dependencies

`edi-007` needs all three:

```bash
bd dep add edi-007 edi-004   # blocked by fetcher
bd dep add edi-007 edi-005   # blocked by display
bd dep add edi-007 edi-006   # blocked by CLI
```

**Also** add the data layer from Module 2:
```bash
bd dep add edi-007 edi-003   # blocked by parser (which needed models)
```

Verify:
```bash
bd show edi-007    # shows 4 blockers
bd ready           # edi-004, edi-005, edi-006 appear; edi-007 does NOT
```

---

## Step 4: Create the Convoy and Stage It

```bash
gt convoy create "weatherly full implementation" \
  edi-004 edi-005 edi-006 edi-007 --notify
```

Now stage to see the wave computation:

```bash
gt convoy stage hq-cv-main_convoy_id
```

You should see something like:

```
🚚 weatherly full implementation

Dependency Analysis:
  ✓ No circular dependencies
  ✓ All rigs available

Wave Plan:
  Wave 1 (3 tasks — dispatch immediately):
    ● edi-004: Add weather fetcher
    ● edi-005: Add terminal display
    ● edi-006: Add CLI argument parser

  Wave 2 (1 task — waits for all of Wave 1):
    ● edi-007: Wire weatherly together

Status: ready to launch
```

**This is the key output.** Gas Town computed that 3 tasks can run in parallel (Wave 1), then 1 task runs after all three complete (Wave 2). You didn't figure this out — the topological sort did.

---

## Step 5: Launch

```bash
gt convoy launch hq-cv-main_convoy_id
```

This dispatches **all three Wave 1 beads simultaneously**.

---

## Step 6: Watch Three Polecats Work in Parallel

```bash
gt polecat list YOUR_RIG_NAME
```

```
● YOUR_RIG/furiosa  working   edi-004   Add weather fetcher
● YOUR_RIG/nux      working   edi-005   Add terminal display
● YOUR_RIG/slit     working   edi-006   Add CLI argument parser
```

> 💡 **Polecat names come from a themed pool** (Mad Max universe by default: furiosa, nux, slit, etc.). You don't choose them — Gas Town allocates from the pool. Check available themes with `gt namepool themes`.

Three polecats, three git worktrees, three Claude sessions — all running simultaneously.

Watch the feed:
```bash
gt feed
```

```
[20:45:11] furiosa  → in_progress (edi-004)
[20:45:12] nux      → in_progress (edi-005)
[20:45:12] slit     → in_progress (edi-006)
... (parallel work happening) ...
[20:47:33] furiosa  closed edi-004 ✓
[20:47:41] nux      closed edi-005 ✓
[20:47:58] slit     closed edi-006 ✓
[20:47:59] ConvoyManager: edi-007 unblocked → slinging to YOUR_RIG
[20:48:00] chrome   hooked edi-007: Wire weatherly together
```

Peek at any one of them while they're working:
```bash
gt peek YOUR_RIG/furiosa    # use full rig/name address
```

The three completed in roughly the same timeframe (parallelism!), and edi-007 dispatched automatically the moment all its blockers closed.

---

## The Wave Diagram

```
t=0                    t≈2min                t≈4min
│                      │                     │
├── Toast (edi-004) ────┤                     │
│                      │                     │
├── Furiosa (edi-005) ──┤                     │
│                      │  edi-007 unblocked  │
├── Nux (edi-006) ──────┤──── Slit ──────────►│ done
│                      │                     │
│   WAVE 1             │        WAVE 2        │
│   (parallel)         │     (sequential)     │
```

**Total time: ~4 min** (2 min Wave 1 + 2 min Wave 2)

Without parallelism: **~8 min** (2 + 2 + 2 + 2 sequential)

**2x speedup from parallelism.** On larger features, the gains compound.

---

## 🔍 When is Parallelism Safe?

**Safe to parallelize:**
- Different files, no imports between them
- Different components with a clean interface boundary
- Different test suites

**Not safe to parallelize:**
- Bead B imports types from Bead A (add blocker)
- Bead B modifies a file Bead A also modifies (merge conflict risk)
- Bead B depends on a contract Bead A is defining

**The conservative rule:** If you're unsure, add the dependency. False parallelism causes merge conflicts and broken code. Missing parallelism just makes things slower. Slower is recoverable; broken is not.

---

## 📝 What You've Mastered So Far

```
Module 1: Single bead → polecat → done (the core loop)
Module 2: A → B (dependency chain, ConvoyManager auto-dispatches B)
Module 3: A+B+C → D (parallel Wave 1, auto-launches Wave 2)
```

You can now model almost any software project as beads with the right dependency graph. That graph determines your parallelism automatically.

---

## Next: [Module 4 — Convoy Launch →](module-04-convoy-launch.md)
