# Plan: weatherly initial build

> **Source:** docs/design.md
> **Generated:** 2026-04-05
> **Type:** initial
> **Summary:** 5 beads across 3 waves · max parallelism 2 · suggested convoy `initial-plan`

## Context

Build the `weatherly` CLI per `docs/product-brief.md` and `docs/design.md`: a one-command terminal weather lookup (`weatherly <city>`) that fetches from wttr.in, transforms the JSON into a `Weather` dataclass, and renders a rich-styled panel. Zero config, no API key, sub-2-second response.

## Reasoning

- **Touches:** `weatherly/config.py`, `weatherly/processor.py`, `weatherly/fetcher.py`, `weatherly/display.py`, `weatherly/__main__.py`, `pyproject.toml`
- **Key decisions applied (from design.md):**
  - Data source: **wttr.in** — `BASE_URL = "https://wttr.in"`, URL shape `{BASE_URL}/{city}?format=j1`
  - Output library: **rich** — add `rich>=13` to `pyproject.toml`
  - Units: default **Fahrenheit**, `--celsius` flag flips to metric
  - Error posture: **fail loud**, single attempt, `TIMEOUT_SECONDS = 5`, exit 1 on failure
- **Decomposition rationale:** one module per bead (5 beads). `config` and `processor` have no sibling imports → Wave 1 in parallel. `fetcher` imports from `config`; `display` imports from `processor` → Wave 2 in parallel. `__main__` imports all four → Wave 3.
- **Assumptions (inferred, not in design.md):**
  - `Weather` dataclass fields: `location`, `temp`, `feels_like`, `condition`, `wind_speed`, `wind_dir`, `humidity`, `units`
  - wttr.in j1 JSON paths for each field (see Bead 2 body)
  - `FetchError` custom exception lives in `fetcher.py`
  - Bead 4 also edits `pyproject.toml` (one-line dep add) — minor size flag

## Wave Diagram

```
Wave 1 (parallel):    Bead 1 (config)     Bead 2 (processor)
Wave 2 (parallel):    Bead 3 (fetcher)    Bead 4 (display)
Wave 3 (sequential):  Bead 5 (__main__)
```

## Beads

### Bead 1: Add config constants and Config dataclass

**Type:** task · **Priority:** P1 · **Depends on:** —

```bash
bd create "Add config constants and Config dataclass" -t task -p P1 --stdin << 'EOF'
Create weatherly/config.py with constants and a Config dataclass.

File: weatherly/config.py

Constants (module-level):
  BASE_URL = "https://wttr.in"
  TIMEOUT_SECONDS = 5

Dataclass:
  @dataclass
  class Config:
      celsius: bool = False

Imports: from dataclasses import dataclass

No sibling imports. This bead is a leaf — fetcher (Bead 3) and __main__
(Bead 5) will import from here.
EOF
```

```bash
# After creation, capture the returned ID and add acceptance:
bd update <id> --acceptance "- [ ] File weatherly/config.py exists
- [ ] python -c 'from weatherly.config import BASE_URL, TIMEOUT_SECONDS, Config' succeeds
- [ ] BASE_URL == 'https://wttr.in'
- [ ] TIMEOUT_SECONDS == 5
- [ ] Config() instantiates with default celsius=False
- [ ] Config(celsius=True).celsius is True"
```

### Bead 2: Add Weather dataclass and parse function

**Type:** task · **Priority:** P1 · **Depends on:** —

```bash
bd create "Add Weather dataclass and parse function" -t task -p P1 --stdin << 'EOF'
Create weatherly/processor.py with the Weather dataclass and a parse()
function that transforms a wttr.in j1 JSON dict into a Weather instance.

File: weatherly/processor.py

Dataclass:
  @dataclass
  class Weather:
      location: str       # "Dallas, Texas"
      temp: int           # current temperature
      feels_like: int     # feels-like temperature
      condition: str      # "Sunny", "Partly cloudy", etc.
      wind_speed: int     # mph or kph depending on celsius flag
      wind_dir: str       # "SW", "NNE", etc.
      humidity: int       # percent
      units: str          # "°F" or "°C"

Function signature:
  def parse(raw: dict, celsius: bool) -> Weather

wttr.in j1 JSON access paths:
  current = raw["current_condition"][0]
  nearest = raw["nearest_area"][0]

  When celsius=False (default):
    temp        = int(current["temp_F"])
    feels_like  = int(current["FeelsLikeF"])
    wind_speed  = int(current["windspeedMiles"])
    units       = "°F"

  When celsius=True:
    temp        = int(current["temp_C"])
    feels_like  = int(current["FeelsLikeC"])
    wind_speed  = int(current["windspeedKmph"])
    units       = "°C"

  Always:
    condition   = current["weatherDesc"][0]["value"]
    wind_dir    = current["winddir16Point"]
    humidity    = int(current["humidity"])
    location    = nearest["areaName"][0]["value"] + ", " + nearest["region"][0]["value"]

Imports: from dataclasses import dataclass

No sibling imports — parse() takes a plain dict in, returns Weather out.
EOF
```

```bash
bd update <id> --acceptance "- [ ] File weatherly/processor.py exists
- [ ] python -c 'from weatherly.processor import Weather, parse' succeeds
- [ ] Weather has all 8 fields (location, temp, feels_like, condition, wind_speed, wind_dir, humidity, units)
- [ ] parse(sample_dict, celsius=False) returns Weather with units == '°F'
- [ ] parse(sample_dict, celsius=True) returns Weather with units == '°C'
- [ ] parse(sample_dict, celsius=False).temp is int"
```

### Bead 3: Add wttr.in fetcher with FetchError

**Type:** task · **Priority:** P2 · **Depends on:** Bead 1

```bash
bd create "Add wttr.in fetcher with FetchError" -t task -p P2 --stdin << 'EOF'
Create weatherly/fetcher.py — a single HTTP call to wttr.in with
fail-loud error handling.

File: weatherly/fetcher.py

Imports:
  import requests
  from weatherly.config import BASE_URL, TIMEOUT_SECONDS, Config

Exception class:
  class FetchError(Exception):
      '''Raised when the wttr.in request fails.'''

Function signature:
  def fetch(city: str, config: Config) -> dict

Behavior:
  1. url = f"{BASE_URL}/{city}?format=j1"
  2. Single attempt: requests.get(url, timeout=TIMEOUT_SECONDS)
  3. On requests.Timeout → raise FetchError(f"Request timed out after {TIMEOUT_SECONDS}s")
  4. On requests.ConnectionError → raise FetchError(f"Cannot reach {BASE_URL}")
  5. On response.status_code != 200 → raise FetchError(f"HTTP {response.status_code} from wttr.in")
  6. Parse JSON: response.json()
  7. If the response lacks "current_condition" key → raise FetchError(f"City not found: {city}")
  8. Return the parsed dict

No retries. Fail loud.
EOF
```

```bash
bd update <id> --acceptance "- [ ] File weatherly/fetcher.py exists
- [ ] python -c 'from weatherly.fetcher import fetch, FetchError' succeeds
- [ ] FetchError is a subclass of Exception
- [ ] fetch signature is 'def fetch(city: str, config: Config) -> dict'
- [ ] fetch('dallas', Config()) returns a dict containing 'current_condition' key (live call)
- [ ] fetch('xyznotacity123', Config()) raises FetchError"
```

### Bead 4: Add rich display renderer

**Type:** task · **Priority:** P2 · **Depends on:** Bead 2

```bash
bd create "Add rich display renderer" -t task -p P2 --stdin << 'EOF'
Create weatherly/display.py to render a Weather instance as a styled
rich Panel, and add the rich dependency.

Files:
  1. pyproject.toml — add "rich>=13" to [project] dependencies list
  2. weatherly/display.py — new file

pyproject.toml change:
  Existing dependencies list:
    dependencies = [
        "requests>=2.31",
    ]
  Update to:
    dependencies = [
        "requests>=2.31",
        "rich>=13",
    ]

weatherly/display.py:

Imports:
  from rich.console import Console
  from rich.panel import Panel
  from rich.text import Text
  from weatherly.processor import Weather

Function signature:
  def render(weather: Weather) -> None

Behavior:
  - Build a multi-line body showing:
      {temp}{units}  (feels like {feels_like}{units})
      {condition}
      Wind: {wind_speed} {wind_unit} {wind_dir} · Humidity: {humidity}%
    where wind_unit is "mph" if units == "°F" else "kph"
  - Wrap in rich.panel.Panel with title=weather.location
  - Print with Console().print(panel)

Example output should resemble the brief's panel:
  ┌─ Dallas, Texas ──────────────────────┐
  │  72°F  (feels like 74°F)             │
  │  Sunny                               │
  │  Wind: 8 mph SW · Humidity: 45%      │
  └──────────────────────────────────────┘

Does not catch exceptions — caller handles errors.
EOF
```

```bash
bd update <id> --acceptance "- [ ] 'rich>=13' appears in pyproject.toml dependencies
- [ ] File weatherly/display.py exists
- [ ] python -c 'from weatherly.display import render' succeeds (after pip install -e .)
- [ ] render signature is 'def render(weather: Weather) -> None'
- [ ] render(Weather(location='Test, TX', temp=72, feels_like=74, condition='Sunny', wind_speed=8, wind_dir='SW', humidity=45, units='°F')) prints a panel with 'Test, TX' in the title
- [ ] wind unit switches: 'mph' when units='°F', 'kph' when units='°C'"
```

### Bead 5: Wire __main__ entry point

**Type:** task · **Priority:** P2 · **Depends on:** Beads 1, 2, 3, 4

```bash
bd create "Wire __main__ entry point" -t task -p P2 --stdin << 'EOF'
Create weatherly/__main__.py — the CLI entry point. Parses argv, wires
config → fetch → parse → render, handles FetchError, returns exit code.

File: weatherly/__main__.py

Imports:
  import argparse
  import sys
  from rich.console import Console
  from weatherly.config import Config
  from weatherly.fetcher import fetch, FetchError
  from weatherly.processor import parse
  from weatherly.display import render

Function signature:
  def main() -> int

Behavior:
  1. Build argparse parser:
       prog: "weatherly"
       description: "Check the current weather in a city."
       positional: city (str, required)
       optional: --celsius (store_true, default False)
  2. args = parser.parse_args()
  3. config = Config(celsius=args.celsius)
  4. try:
         raw = fetch(args.city, config)
         weather = parse(raw, config.celsius)
         render(weather)
         return 0
     except FetchError as e:
         Console(stderr=True).print(f"[red]weatherly:[/red] {e}")
         return 1

Module footer:
  if __name__ == "__main__":
      sys.exit(main())

pyproject.toml already registers the console script:
  [project.scripts]
  weatherly = "weatherly.__main__:main"
EOF
```

```bash
bd update <id> --acceptance "- [ ] File weatherly/__main__.py exists
- [ ] python -c 'from weatherly.__main__ import main' succeeds
- [ ] main signature is 'def main() -> int'
- [ ] python -m weatherly dallas exits 0 and prints a panel (live call)
- [ ] python -m weatherly dallas --celsius prints a panel with '°C' (live call)
- [ ] python -m weatherly xyznotacity123 exits 1 and prints a red error to stderr"
```

## Dependencies

After creating all beads, capture their IDs and wire dependencies:

```bash
# Substitute <bead-N> with the actual edi-xxx ID from each bd create above
bd dep add <bead-3> <bead-1>   # fetcher imports BASE_URL, TIMEOUT_SECONDS, Config from config
bd dep add <bead-4> <bead-2>   # display imports Weather from processor
bd dep add <bead-5> <bead-1>   # __main__ imports Config from config
bd dep add <bead-5> <bead-2>   # __main__ imports parse from processor
bd dep add <bead-5> <bead-3>   # __main__ imports fetch, FetchError from fetcher
bd dep add <bead-5> <bead-4>   # __main__ imports render from display
bd dep cycles                   # verify no cycles
```

## Launch

```bash
gt convoy create "weatherly initial build" <bead-1> <bead-2> <bead-3> <bead-4> <bead-5> --notify
gt convoy stage <bead-1> <bead-2> <bead-3> <bead-4> <bead-5>
gt convoy launch <convoy-id>
```

## Plan Notes

- **Bead 4 touches 2 files** (`weatherly/display.py` + `pyproject.toml`). Minor: the pyproject change is a one-line dep add. Alternative: move the pyproject edit to Bead 5. Kept in Bead 4 because the module that needs `rich` should declare it.
- **Beads 3 and 5 acceptance criteria include live wttr.in calls.** If offline, substitute mocked fixtures or skip those checks.
- **Assumptions flagged:** `Weather` dataclass fields and wttr.in JSON paths were inferred from wttr.in's j1 format, not stated in design.md. Verify field names match the live API response.
