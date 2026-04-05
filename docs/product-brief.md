# Project Brief: weather

## Vision
Check the weather the same way you check `git status` — one command, instant answer, no tabs opened.

## The Problem
Looking up the weather means context-switching out of the terminal: open a browser, dismiss a cookie banner, wait for a bloated weather site to load, squint at an ad-heavy page for the one number you wanted. Existing CLI alternatives either require configuration up front or dump raw JSON. For someone who lives in the terminal, there's no fast, pleasant way to just *see* the weather.

## What It Does
- Single-command lookup: `weather dallas`
- Prints current conditions in a rich, styled terminal panel — temperature, feels-like, conditions, wind, humidity
- Accepts any city name as a positional argument
- Zero configuration — install and run

Example:

```
$ weather dallas
┌─ Dallas, TX ─────────────────────────┐
│  ☀  72°F  (feels like 74°F)          │
│     Sunny                            │
│     Wind: 8 mph SW · Humidity: 45%   │
└──────────────────────────────────────┘
```

## Who It's For
Developers and power users who live in the terminal and want a fast weather glance without leaving it.

## Success Looks Like
From keystroke to answer in under two seconds, with no config file, no API key setup, and no browser tab.
