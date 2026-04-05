# Setup: Getting Your Town Ready

> **Do this before Module 0.** If Gas Town isn't wired up, nothing in the workshop will work.

---

## Quick Setup (Experienced Users)

If you already know your way around Gas Town:

```bash
cd YOUR_TOWN_ROOT          # e.g. ~/gt
gt enable
gt shell install
source ~/.zshrc

gt up
gt status                  # mayor + deacon + witness + refinery running

cd YOUR_TOWN_ROOT/YOUR_RIG/crew/human
bd ready                   # should list beads without errors
gt formula list            # should include mol-idea-to-plan and shiny
```

If anything fails, follow the full setup below.

---

## 1. Find Your Town Root & Enable Shell Integration

First, confirm where your Gas Town town root actually is. It's not always `~/gt`:

```bash
gt status 2>/dev/null | head -3
# OR look for the directory containing mayor/ and .beads/
ls ~/gt/         # common location
ls ~/gt/learn/   # another common location
```

The directory containing `mayor/` and `.beads/` is your town root. **Write it down.** You'll use it everywhere below as `~/gt` (substituting your actual path if different).

Now enable Gas Town and install shell integration. This is a one-time step. Without it, `GT_ROOT` and `GT_RIG` won't be set when you `cd` into crew directories, and `gt formula list` won't find anything.

```bash
cd YOUR_TOWN_ROOT    # e.g. ~/gt or ~/gt/learn
gt enable
gt shell install
source ~/.zshrc      # must be .zshrc, NOT .zshenv
```

> ⚠️ **`source ~/.zshrc` not `~/.zshenv`** — the shell hook is added to `.zshrc`. Sourcing `.zshenv` won't activate it.

Verify shell integration is active:
```bash
cd YOUR_TOWN_ROOT/YOUR_RIG/crew/human
echo $GT_ROOT     # should show your town root path
echo $GT_RIG      # should show your rig name
```

If those are empty, open a new terminal and `cd` back into the directory.

---

## 2. Verify the Basics

All Gas Town commands must run from inside your town root (`~/gt`) or a crew/polecat workspace inside it. Running from your project repo (`~/source/...`) will NOT work — Gas Town commands must run inside the town.

```bash
cd ~/gt
gt doctor
```

You may see warnings — that's normal. What you need to NOT see:
- `✖ dolt-binary` (Dolt not installed)
- `✖ beads-binary` (bd not installed)
- Anything about Claude Code not found

Warnings about custom types, stale PIDs, routing mode — ignore those for now.

---

## 3. Bring Up All Services

```bash
cd ~/gt
gt up
```

Expected output:
```
✓ Daemon: PID xxxxx
✓ Deacon: hq-deacon
✓ Mayor: hq-mayor
✓ Witness (your_rig): rig-witness
✓ Refinery (your_rig): rig-refinery
```

> ⚠️ **"port 3307 already in use"** — This is a false alarm if Dolt was already running from a previous session. Check with `ps aux | grep dolt`. If the process is there, you're fine — Gas Town's status display just doesn't detect it correctly sometimes. Proceed.

> ⚠️ **"daemon is not running"** in `gt doctor` — Run `gt up` to start everything.

---

## 4. Check Your Status

```bash
gt status
```

You should see your rig(s) with Witness and Refinery showing `●` (running). Something like:

```
Town: gt

Services: daemon (PID 38014)  dolt (:3307)  tmux (7 sessions)

🎩 mayor        ● [claude]
🐺 deacon       ● [claude]

─── your_rig/ ─────────────────────

🦉 witness      ● [claude]
🏭 refinery     ● [claude]
👷 Crew (1)
   human    ○ [claude]
```

---

## 5. Find Your Rig Name

```bash
gt rig list
```

You'll see something like:
```
● your_rig
   Witness: ● running  Refinery: ● running
   Polecats: 0  Crew: 1
```

**Write this down.** The workshop uses `YOUR_RIG` as a placeholder throughout. Always substitute your actual rig name. Common choices: `workshop`, `learning`, or your project name.

---

## 6. Set Up a Crew Workspace (Optional but Recommended)

For Modules 1-4, you can run `bd create` from any directory *inside* your town. The easiest place is your crew workspace.

> 💡 **This tutorial uses `human` as the crew name.** We recommend using it for the workshop. It reinforces the mental model: crew is where the human works, polecats are the ephemeral agents. If you choose a different crew name, substitute it wherever you see `human` in the commands below.

```bash
cd ~/gt/YOUR_RIG/crew/human
```

> 💡 **Why the crew directory?** Gas Town detects your identity from your current working directory. Being in `crew/human` sets `BD_ACTOR=YOUR_RIG/crew/human` — so beads you create are attributed to you correctly.

If you don't have a crew workspace yet:
```bash
cd ~/gt
gt crew add human --rig YOUR_RIG
cd ~/gt/YOUR_RIG/crew/human
```

---

## 7. Fix the Dolt Fingerprint (If Needed)

If `bd create` fails with:
```
Error: failed to open database: database "your_rig" not found on Dolt server
```

Run `bd doctor` to diagnose:
```bash
cd ~/gt/YOUR_RIG/crew/human
bd doctor | head -20
```

If you see `Repo Fingerprint: Database belongs to different repository`:
```bash
echo "y" | bd migrate --update-repo-id
```

Then try `bd create` again.

---

## 8. Confirm Everything Works

```bash
cd ~/gt/YOUR_RIG/crew/human
bd ready
```

You should get a list of open beads (possibly some pre-existing ones — that's fine). If this runs without errors, you're ready.

---

## 9. Verify Native Formulas Are Available

Gas Town ships with the formulas used in this workshop — no extra installation needed.

```bash
gt formula list
```

You should see (among others):
```
mol-idea-to-plan   Full pipeline from vague idea to approved, beads-ready plan
mol-polecat-work   Full polecat work lifecycle from assignment through completion
shiny              Engineer in a Box - design before you code, review before you ship
```

These are the native Gas Town formulas used in Module 5. If they're missing:
- Run `gt stale` to check for updates
- Update Gas Town if a newer version is available
- Restart with `gt down && gt up`

> 💡 **gt-toolkit (optional):** The community repo [Xexr/gt-toolkit](https://github.com/Xexr/gt-toolkit) has additional formulas including a more elaborate multi-LLM spec pipeline. It's worth exploring after you've completed this workshop, but it's not required — we use native formulas throughout.

---

## ✅ You're Ready When:

- [ ] `gt enable` + `gt shell install` done, `source ~/.zshrc` run
- [ ] `cd ~/gt/YOUR_RIG/crew/human && echo $GT_ROOT` shows `~/gt`
- [ ] `gt status` shows Witness + Refinery running for your rig
- [ ] `bd ready` runs without errors from the crew directory
- [ ] You know your rig name from `gt rig list`
- [ ] `gt formula list` shows `mol-idea-to-plan` and `shiny`

---

## 📚 Further Reading

- [Installing Gas Town](https://docs.gastownhall.ai/installing/) — official installation guide
- [Configuration Commands](https://docs.gastownhall.ai/usage/configuration/) — `gt enable`, `gt shell`, property layers
- [Workspace Commands](https://docs.gastownhall.ai/usage/workspace/) — `gt rig`, `gt crew` setup reference
- [Services Commands](https://docs.gastownhall.ai/usage/services/) — `gt up`, `gt dolt`, daemon management

---

**→ [Module 0: The Mental Model](module-00-mental-model.md)**
