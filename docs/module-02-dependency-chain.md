# Module 2: Dependency Chains

> **Goal:** Create two beads where B can't start until A finishes. Understand how Gas Town enforces ordering without you managing it.

> **All commands run from:** `~/gt/YOUR_RIG/crew/claudio`

---

## The Problem Dependency Chains Solve

Imagine you need to:
1. Create a `WeatherData` dataclass (it doesn't exist yet)
2. Write a parser that populates `WeatherData` from JSON

If you sling both at once, the parser polecat might start before the dataclass exists and write code that imports something that isn't there yet. Or it might guess at the structure wrong.

Dependencies are how you tell Gas Town: **"Don't start B until A is done."**

---

## The Dependency Model

```
bd dep add <blocked> <blocker>
            │           │
            │           └── This must complete FIRST
            └────────────── This cannot start until blocker closes
```

**Reading it:** `edi-002 depends on edi-001` = edi-002 is blocked by edi-001.

When `edi-001` closes, Gas Town automatically unblocks `edi-002` — and if it's tracked in a convoy, the ConvoyManager dispatches it within 5 seconds. **You don't manually sling the second bead.**

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
bd create "Add WeatherData dataclass" \
  -t task -p P2 \
  --description "Create weatherly/models.py with a WeatherData dataclass.

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

All fields should be type-annotated. Add a __str__ method that returns a human-readable one-liner summary." \
  --acceptance "- [ ] File exists at weatherly/models.py
- [ ] WeatherData dataclass defined with all 9 fields, correct types
- [ ] __str__ method returns readable summary string
- [ ] No import errors (python -c 'from weatherly.models import WeatherData')"
```

Note the ID: `edi-002`

---

## Step 2: Create the Second Bead

```bash
bd create "Add weather data parser" \
  -t task -p P2 \
  --description "Create weatherly/parser.py that converts wttr.in JSON response to WeatherData.

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

Import WeatherData from weatherly.models (created in the preceding task).
Function signature: def parse_weather(json_data: dict) -> WeatherData

Add error handling for missing fields (KeyError → raise ValueError with descriptive message)." \
  --acceptance "- [ ] File exists at weatherly/parser.py
- [ ] parse_weather function defined with correct signature
- [ ] All 9 fields mapped correctly
- [ ] ValueError raised with helpful message on malformed input
- [ ] No import errors"
```

Note the ID: `edi-003`

---

## Step 3: Declare the Dependency

```bash
bd dep add edi-003 edi-002
```

**Read this as:** "edi-003 is blocked by edi-002"

Verify it:
```bash
bd show edi-003   # should show "blocked by: edi-002"
bd ready          # edi-003 should NOT appear here — it's blocked
```

---

## Step 4: Create the Convoy

```bash
gt convoy create "weatherly data layer" edi-002 edi-003 --notify
```

This tracks both beads. When both close, the convoy lands.

---

## Step 5: Stage the Convoy (See the Waves)

```bash
gt convoy stage <your-epic-id-or-list-of-beads>
```

Actually, for an explicit list of beads without an epic, just create and launch directly:

```bash
gt convoy launch <convoy-id>
```

But let's first look at what `gt convoy status` shows us:

```bash
gt convoy status hq-cv-xyz
```

```
🚚 hq-cv-xyz: weatherly data layer
  Status: ●
  Progress: 0/2 completed

  Tracked Issues:
    ○ edi-002: Add WeatherData dataclass [task]  ← no blockers
    ○ edi-003: Add weather data parser [task]    ← blocked by edi-002
```

---

## Step 6: Sling Only the First Bead

Here's the key point: **you only sling what's unblocked.** The ConvoyManager handles the rest.

```bash
gt sling edi-002 YOUR_RIG_NAME
```

Watch it work:
```bash
gt feed
gt polecat list YOUR_RIG_NAME     # see which polecat picked it up
gt peek YOUR_RIG_NAME/furiosa     # use the actual polecat name from above
gt convoy status hq-cv-xyz
```

---

## Step 7: Watch the Chain Execute Automatically

When `edi-002` closes:

```
[20:31:12] Furiosa closed edi-002: Add WeatherData dataclass
[20:31:13] ConvoyManager: edi-002 closed — checking convoy hq-cv-xyz
[20:31:13] ConvoyManager: edi-003 is now unblocked
[20:31:13] ConvoyManager: slinging edi-003 to YOUR_RIG
[20:31:14] Nux hooked edi-003: Add weather data parser
```

**You didn't sling edi-003.** The ConvoyManager did it automatically within 5 seconds of edi-002 closing.

This is the power of dependency chains + convoys together.

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

The code dependency and the bead dependency are aligned. This isn't a coincidence — **good bead decomposition mirrors the actual dependency structure of the code.**

---

## 🔍 The Dependency Rules

### When to add a blocker:
- Bead B imports code created by Bead A
- Bead B modifies a file that Bead A is also modifying (conflict risk)
- The plan explicitly states "X must complete before Y"

### When NOT to add a blocker:
- You *think* it would be cleaner to do them in order
- They happen to be in the same module but are independent
- You're being overly cautious

**False blockers kill parallelism.** Every unnecessary dep means one bead sitting idle while another runs. If in doubt, leave it out — you can always add deps later, but removing them requires thought.

---

## Check the Dependency Graph

```bash
bd dep cycles   # should return empty — no circular deps
```

If you accidentally create a cycle (A blocks B blocks C blocks A), `bd dep cycles` will catch it before any work is dispatched.

---

## 📝 Key Commands Learned

```bash
bd dep add <blocked> <blocker>   # declare dependency
bd dep cycles                     # verify no circular deps
bd ready                          # see what's unblocked right now
# ConvoyManager auto-slinging: you don't manually sling blocked beads
```

---

## Next: [Module 3 — Parallel Lanes →](module-03-parallel-lanes.md)
