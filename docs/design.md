# Design Document: weatherly

> **Purpose:** This document captures the design decisions made after
> reading the product brief and before writing beads. It answers the
> questions an agent can't answer for you — what data source, what
> shape, what boundaries.

---

## From Brief to Design

The brief describes a one-command terminal weather lookup with zero config and a rich styled panel. This document picks the data source, the libraries, the module boundaries, and the bead breakdown so every downstream bead can cite literal values instead of guessing.

---

## Key Decisions

### 1. Weather Data Source

**Options considered:**
- **wttr.in** — free, keyless, JSON via `?format=j1`, built for terminals, city name directly in URL
- **Open-Meteo** — free, keyless, but requires a geocoding step (city → lat/lon) first
- **OpenWeatherMap** — requires API key registration

**Decision:** wttr.in. One HTTP call, no API key, no geocoding — matches the brief's "zero config, no API key setup".

**Impact:** `BASE_URL = "https://wttr.in"`, request URL is `{BASE_URL}/{city}?format=j1`

### 2. Rich Output Library

**Options considered:**
- **rich** — `Console` + `Panel`, styled terminal output, matches the brief's example panel
- **Plain ANSI escapes** — no dep, but tedious and fragile

**Decision:** rich. The brief's example is literally a rich Panel. Worth the dependency.

**Impact:** Add `rich>=13` to `pyproject.toml` dependencies.

### 3. Units

**Options considered:**
- Fahrenheit + mph (hardcoded)
- Celsius + kph (hardcoded)
- `--celsius` boolean flag, default Fahrenheit

**Decision:** default Fahrenheit/mph, `--celsius` flag switches to metric.

**Impact:** CLI flag `--celsius` (bool), `Config.celsius: bool = False`, `processor.parse()` reads the flag and picks fields from the wttr.in JSON accordingly.

### 4. Error Handling Posture

**Options considered:**
- Fail loud with a short styled error, exit non-zero
- Retry silently 2-3 times, then fail

**Decision:** fail loud, no retries. Sub-2s response budget + CLI convention (user can re-run).

**Impact:** Single `requests.get(..., timeout=TIMEOUT_SECONDS)` with `TIMEOUT_SECONDS = 5`. On HTTP error, timeout, or city-not-found: print a styled error via rich, exit 1.

---

## Architecture

```
weatherly/
  __init__.py       (exists)
  __main__.py       ← entry point: argv parsing + orchestration
  config.py         ← constants + Config dataclass
  fetcher.py        ← HTTP call to wttr.in → raw JSON dict
  processor.py      ← wttr.in dict + celsius flag → Weather dataclass
  display.py        ← Weather dataclass → rich Panel → stdout
```

**Data flow:**
```
__main__ (parse argv: city, --celsius)
    │
    ▼
config.Config  ← constants + args
    │
    ▼
fetcher.fetch(city, config) ─► raw dict
    │
    ▼
processor.parse(raw, celsius) ─► Weather
    │
    ▼
display.render(weather) ─► rich Panel ─► stdout
```

Each module has one job. Dependencies flow one direction: config ← fetcher, processor ← display, all ← __main__. No circular imports, no sibling reach-arounds.

---

## Bead Breakdown

| Bead | Module | Depends On | Notes |
|------|--------|------------|-------|
| 1 | config | nothing | Defines `BASE_URL`, `TIMEOUT_SECONDS`, `Config` dataclass. Pure constants + dataclass, no sibling imports. |
| 2 | processor | nothing | Defines `Weather` dataclass + `parse(raw: dict, celsius: bool) -> Weather`. Takes a plain dict, returns a dataclass — independent of fetcher's implementation. |
| 3 | fetcher | 1 | Imports `BASE_URL`, `TIMEOUT_SECONDS`, `Config` from config. Exposes `fetch(city, config) -> dict` with explicit error on HTTP/timeout/not-found. |
| 4 | display | 2 | Imports `Weather` from processor. Exposes `render(weather) -> None` using rich. |
| 5 | __main__ | 1, 2, 3, 4 | Wires everything: argparse, build Config, fetch → parse → render, handle errors, exit codes. |

**Wave structure:**
- Wave 1 (parallel): config, processor
- Wave 2 (parallel): fetcher, display
- Wave 3: __main__

**Why this order matters:** fetcher imports from config, so config must land first. display imports `Weather` from processor, so processor must land first. __main__ imports all four. Running __main__ before its deps exist would hit `ImportError` immediately. The parallelism in waves 1-2 is real — config and processor share no code, and fetcher and display touch different modules.

---

## What This Document Is Not

This is not a spec. It doesn't tell an agent exactly what to write line by line — that's the bead body's job. This document captures the *reasoning* behind the decisions so when you write a bead, you're not making it up as you go.

---

## Next Step

Run `/plan` to translate this design into a bead plan:

```bash
/plan docs/design.md
```
