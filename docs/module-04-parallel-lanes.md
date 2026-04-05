# Module 4: Parallel Lanes

> **Goal:** Sling multiple independent beads simultaneously and watch them execute in parallel. Understand wave computation and when parallelism is safe.

> **All commands run from:** `~/gt/YOUR_RIG/crew/YOUR_CREW`

---

## The Problem: Sequential Work is Slow

What if three things are genuinely independent? Running them one after another wastes time. Gas Town's answer: **parallel lanes**. Multiple polecats working simultaneously.

---

## The Structure

Three independent modules (don't import each other, don't touch the same files), then one bead that wires them all together:

```
edi-004: Add weather fetcher        (independent)
edi-005: Add terminal display       (independent)
edi-006: Add CLI argument parser    (independent)

     ↓            ↓            ↓
 (all run in parallel, Wave 1)
     │
     └──────────────┐
                    ▼
edi-007: Wire it all together  (blocked by all three, Wave 2)
```

---

## Step 1: Create the Three Independent Beads

```bash
bd create "Add weather fetcher" -t task -p P2 --stdin << 'EOF'
Create weatherly/fetcher.py that makes HTTP requests to wttr.in.

Import Config from weatherly.config.
Function signature: def fetch_weather(config: Config) -> dict

Implementation:
- Use requests library
- URL: f'{config.api_base_url}/{config.location}?format={config.format}&lang=en'
- Timeout: config.request_timeout
- Return: parsed JSON (response.json())
- Raise: requests.exceptions.RequestException on network failure
- Raise: ValueError if response status is not 200
EOF
```

```bash
bd update <FETCHER_ID> --acceptance "- [ ] File exists at weatherly/fetcher.py
- [ ] fetch_weather function defined with correct signature
- [ ] Uses requests library with timeout
- [ ] Raises correct exception types
- [ ] Returns dict (parsed JSON)"
```

```bash
bd create "Add terminal display" -t task -p P2 --stdin << 'EOF'
Create weatherly/display.py that prints weather data to the terminal.

Import WeatherData from weatherly.models.
Function signature: def display_weather(data: WeatherData) -> None

Output format (example):
  📍 London, United Kingdom
  🌡  Temperature: 15°C (59°F), feels like 13°C
  💧  Humidity: 72%
  🌬  Wind: 18 km/h NW
  ☁   Partly cloudy

Use Unicode emoji for visual appeal. No external libraries required (just
print statements).
EOF
```

```bash
bd update <DISPLAY_ID> --acceptance "- [ ] File exists at weatherly/display.py
- [ ] display_weather function defined
- [ ] Outputs all WeatherData fields with emoji labels
- [ ] No import errors"
```

```bash
bd create "Add CLI argument parser" -t task -p P2 --stdin << 'EOF'
Create weatherly/cli.py that parses command-line arguments.

Use Python's argparse stdlib (no third-party CLI libs).
Function signature: def parse_args() -> Config

Arguments:
- location (positional): city name or 'auto' for IP-based detection
- --units: 'metric' or 'imperial' (default: 'metric')
- --format: output format string (default: 'j1')
- -v/--verbose: flag for verbose output (store_true)

Import Config from weatherly.config and return a populated Config instance.
EOF
```

```bash
bd update <CLI_ID> --acceptance "- [ ] File exists at weatherly/cli.py
- [ ] parse_args() returns Config instance
- [ ] All arguments defined correctly
- [ ] --help output is clear and includes all arguments"
```

Note the three IDs. We'll call them **FETCHER_ID**, **DISPLAY_ID**, and **CLI_ID** (yours will be different).

---

## Step 2: Create the Wiring Bead (blocked by all three)

```bash
bd create "Wire weatherly together in main.py" -t task -p P2 --stdin << 'EOF'
Create weatherly/__main__.py that wires all modules together.

Import and call:
- parse_args() from weatherly.cli → Config
- fetch_weather(config) from weatherly.fetcher → dict
- parse_weather(json_data) from weatherly.parser → WeatherData
- display_weather(data) from weatherly.display → None

Add top-level error handling:
- requests.exceptions.RequestException → print 'Network error: ...' + exit(1)
- ValueError → print 'Data error: ...' + exit(1)

Entry point: if __name__ == '__main__': main()

Also create weatherly/__init__.py (can be empty).
EOF
```

```bash
bd update <WIRING_ID> --acceptance "- [ ] File exists at weatherly/__main__.py
- [ ] All modules imported and called in correct order
- [ ] Error handling for network and data errors
- [ ] python -m weatherly London runs without import errors
- [ ] weatherly/__init__.py exists"
```

Note the ID. We'll call it **WIRING_ID**.

---

## Step 3: Declare Dependencies

The wiring bead needs all three parallel beads plus the parser from Module 3:

```bash
bd dep add <WIRING_ID> <FETCHER_ID>    # blocked by fetcher
bd dep add <WIRING_ID> <DISPLAY_ID>    # blocked by display
bd dep add <WIRING_ID> <CLI_ID>        # blocked by CLI
bd dep add <WIRING_ID> <BEAD_B>        # blocked by parser (from Module 3)
```

Verify:
```bash
bd show <WIRING_ID>    # shows 4 blockers
bd ready               # fetcher, display, CLI appear; wiring does NOT
bd dep cycles      # must be clean
```

---

## Step 4: Create the Convoy

```bash
gt convoy create "weatherly full implementation" \
  <FETCHER_ID> <DISPLAY_ID> <CLI_ID> <WIRING_ID> --notify
```

---

## Step 5: Sling and Watch Three Polecats Work in Parallel

Sling the three independent beads:

```bash
gt sling <FETCHER_ID> YOUR_RIG_NAME
gt sling <DISPLAY_ID> YOUR_RIG_NAME
gt sling <CLI_ID> YOUR_RIG_NAME
```

> 💡 **Why sling manually here?** We're learning what parallel execution looks like. In Module 5, you'll use `gt convoy stage` and `gt convoy launch` to automate this. But first, see it with your own eyes.

```bash
gt polecat list YOUR_RIG_NAME
```

```
● YOUR_RIG/furiosa  working   edi-004   Add weather fetcher
● YOUR_RIG/nux      working   edi-005   Add terminal display
● YOUR_RIG/slit     working   edi-006   Add CLI argument parser
```

> 💡 **Polecat names come from a themed pool** (Mad Max by default: furiosa, nux, slit, etc.). Check available themes with `gt namepool themes`.

Peek at any one:
```bash
gt peek YOUR_RIG/furiosa    # full rig/name address
```

Watch the feed:
```bash
gt feed
```

When all three Wave 1 beads close, the ConvoyManager automatically slinging `edi-007` to a fresh polecat. You walk away after `gt convoy launch`.

---

## The Wave Diagram

```
t=0                    t≈2min                t≈4min
│                      │                     │
├── furiosa (edi-004) ──┤                     │
├── nux     (edi-005) ──┤  edi-007 unblocked  │
├── slit    (edi-006) ──┤──── chrome ────────►│ done
│                      │                     │
│   WAVE 1             │      WAVE 2          │
│   (parallel)         │   (sequential)       │
```

**Total ~4 min vs ~8 min sequential. 2x speedup from parallelism.**

---

## 🔍 When is Parallelism Safe?

**Safe:** Different files, no imports between them, different components with clean interfaces.

**Not safe:** B imports types from A, B modifies a file A is also modifying, B depends on a contract A is defining.

**Conservative rule:** If unsure, add the dependency. False parallelism causes merge conflicts. Missing parallelism just makes things slower.

---

## 📝 What You've Mastered So Far

```
Module 2: Single bead → polecat → done (the core loop)
Module 3: A → B (dependency chain, ConvoyManager auto-dispatches B)
Module 4: A+B+C → D (parallel Wave 1, auto-launches Wave 2)
```

---

---

## 📚 Further Reading

- [Convoys](https://docs.gastownhall.ai/concepts/convoy/) — convoy vs swarm, lifecycle states
- [Gas Town Architecture](https://docs.gastownhall.ai/design/architecture/) — how the ConvoyManager feeds waves

---

## Next: [Module 5 — Convoy Launch →](module-05-convoy-launch.md)
