# Module 3: Dependency Chains

> **Goal:** Create two beads where B can't start until A finishes. Understand how Gas Town enforces ordering without you managing it.

> **All commands run from:** `~/gt/YOUR_RIG/crew/human`

> 💡 **Your bead IDs will differ from these examples.** Gas Town generates unique IDs each time. The examples use names like BEAD_A, BEAD_B, FETCHER_ID, etc. to make it clear where to substitute your actual IDs. Keep a note of each ID as you create beads.

---

## Why We're Still Doing This Manually

Like Module 2, we're creating beads by hand here to learn how dependency enforcement works. Your Module 1 plan already has the dep structure mapped out. Understanding the mechanics now means you can confidently read convoy wave plans later.

---

## The Problem Dependency Chains Solve

Imagine you need to:
1. Create a `WeatherData` dataclass (it doesn't exist yet)
2. Write a parser that populates `WeatherData` from JSON

If you sling both at once, the parser polecat might start before the dataclass exists and write code that imports something that isn't there yet. Dependencies tell Gas Town: **"Don't start B until A is done."**

---

## The Dependency Model

```
bd dep add <blocked> <blocker>
            │           │
            │           └── This must complete FIRST
            └────────────── This cannot start until blocker closes
```

When `edi-002` closes, the ConvoyManager automatically unblocks and dispatches `edi-003` within 5 seconds. **You don't manually sling the second bead.**

---

## What We're Building

```
edi-002: Add WeatherData dataclass    (no deps, can start immediately)
         │
         ▼ blocks
edi-003: Add weather data parser      (blocked until edi-002 closes)
```

---

## Step 1: Create the First Bead (no dependencies)

```bash
bd create "Add WeatherData dataclass" -t task -p P2 --stdin << 'EOF'
Create weatherly/models.py with a WeatherData dataclass.

Fields needed:
- location: str (city name as returned by API)
- temperature_c: float
- temperature_f: float
- feels_like_c: float
- humidity: int (percentage, 0-100)
- description: str (e.g. 'Partly cloudy')
- wind_speed_kph: float
- wind_direction: str (e.g. 'NW')
- is_day: bool

All fields should be type-annotated. Add a __str__ method that returns a
human-readable one-liner summary.
EOF
```

```bash
bd update <BEAD_A> --acceptance "- [ ] File exists at weatherly/models.py
- [ ] WeatherData dataclass defined with all 9 fields, correct types
- [ ] __str__ method returns readable summary string
- [ ] No import errors (python -c 'from weatherly.models import WeatherData')"
```

Note the ID. We'll call it **BEAD_A** (your actual ID will be something like `edi-a3x`).

---

## Step 2: Create the Second Bead

```bash
bd create "Add weather data parser" -t task -p P2 --stdin << 'EOF'
Create weatherly/parser.py that converts wttr.in JSON response to WeatherData.

The wttr.in API (format=j1) returns nested JSON. The relevant fields:
- current_condition[0].temp_C → temperature_c
- current_condition[0].temp_F → temperature_f
- current_condition[0].FeelsLikeC → feels_like_c
- current_condition[0].humidity → humidity (int)
- current_condition[0].weatherDesc[0].value → description
- current_condition[0].windspeedKmph → wind_speed_kph
- current_condition[0].winddir16Point → wind_direction
- current_condition[0].isDay → is_day (bool)
- nearest_area[0].areaName[0].value → location

Import WeatherData from weatherly.models.
Function signature: def parse_weather(json_data: dict) -> WeatherData

Add error handling for missing fields (KeyError → raise ValueError with
descriptive message).
EOF
```

```bash
bd update <BEAD_B> --acceptance "- [ ] File exists at weatherly/parser.py
- [ ] parse_weather function defined with correct signature
- [ ] All 9 fields mapped correctly
- [ ] ValueError raised with helpful message on malformed input
- [ ] No import errors"
```

Note the ID. We'll call it **BEAD_B**.

---

## Step 3: Declare the Dependency

```bash
bd dep add <BEAD_B> <BEAD_A>
```

**Read this as:** "BEAD_B is blocked by BEAD_A"

Verify it:
```bash
bd show <BEAD_B>   # should show "blocked by: <BEAD_A>"
bd ready           # BEAD_B should NOT appear here (it's blocked)
```

---

## Step 4: Create the Convoy

```bash
gt convoy create "weatherly data layer" <BEAD_A> <BEAD_B> --notify
```

---

## Step 5: Stage the Convoy

```bash
gt convoy status <CONVOY_ID>
```

```
🚚 <CONVOY_ID>: weatherly data layer
  Status: ●
  Progress: 0/0 completed
```

> 💡 **0/0 is normal** until beads start closing. See Module 1.

---

## Step 6: Sling Only the First Bead

**You only sling what's unblocked.** The ConvoyManager handles the rest.

```bash
gt sling <BEAD_A> YOUR_RIG_NAME
```

Watch it work:
```bash
gt feed
gt polecat list YOUR_RIG_NAME     # see which polecat picked it up
gt peek YOUR_RIG_NAME/<polecat>   # use the actual polecat name from above
gt convoy status <CONVOY_ID>
```

---

## Step 7: Watch the Chain Execute Automatically

When `edi-002` closes:

```
[20:31:12] furiosa closed edi-002: Add WeatherData dataclass
[20:31:13] ConvoyManager: edi-002 closed. Checking convoy hq-cv-xyz
[20:31:13] ConvoyManager: edi-003 is now unblocked
[20:31:13] ConvoyManager: slinging edi-003 to YOUR_RIG
[20:31:14] nux hooked edi-003: Add weather data parser
```

**You didn't sling edi-003.** The ConvoyManager did it automatically within 5 seconds.

---

## The Dependency Graph Visualized

```
edi-002 [WeatherData dataclass]
   │
   │  blocks
   ▼
edi-003 [weather data parser]
   │
   │  imports from
   ▼
weatherly/models.py  ←──  weatherly/parser.py
```

---

## 🔍 Dependency Rules

**Add a blocker when:**
- Bead B imports code created by Bead A
- Bead B modifies a file Bead A is also modifying
- The plan explicitly states "X must complete before Y"

**Don't add a blocker when:**
- You think it would be cleaner to do them in order (but they're actually independent)
- They're in the same module but don't depend on each other

**False blockers kill parallelism.** When in doubt, leave it out.

---

## Check the Dependency Graph

```bash
bd dep cycles   # should return empty (no circular deps)
```

---

## 📝 Key Commands Learned

```bash
bd dep add <blocked> <blocker>   # declare dependency
bd dep cycles                     # verify no circular deps
bd ready                          # see what's unblocked right now
```

---

---

## 📚 Further Reading

- [Convoy Lifecycle Design](https://docs.gastownhall.ai/design/convoy-lifecycle/) — how the ConvoyManager auto-dispatches on bead close
- [Work Management Commands](https://docs.gastownhall.ai/usage/work-management/) — `bd dep add`, `bd dep cycles`, and more

---

## Next: [Module 4 — Parallel Lanes →](module-04-parallel-lanes.md)
