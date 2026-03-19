# Setup: Getting Your Town Ready

> **Do this before Module 0.** If Gas Town isn't wired up, nothing in the workshop will work.

---

## 1. Verify the Basics

All Gas Town commands must run from inside your town root (`~/gt`) or a crew/polecat workspace inside it. Running from your project repo (`~/source/...`) won't work.

```bash
cd ~/gt
gt doctor
```

You'll likely see some warnings — that's normal. What you need to NOT see:
- `✖ dolt-binary` (Dolt not installed)
- `✖ beads-binary` (bd not installed)
- Anything about Claude Code not found

Warnings about custom types, stale PIDs, routing mode — ignore those for now.

---

## 2. Bring Up All Services

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

## 3. Check Your Status

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
   claudio      ○ [claude]
```

---

## 4. Find Your Rig Name

```bash
gt rig list
```

You'll see something like:
```
● your_rig
   Witness: ● running  Refinery: ● running
   Polecats: 0  Crew: 1
```

**Write this down.** You'll use `YOUR_RIG` as a placeholder throughout the workshop. In the examples below, we use `edinsights_ui` — replace it with your actual rig name.

---

## 5. Set Up a Crew Workspace (Optional but Recommended)

For Modules 1-4, you can run `bd create` from any directory *inside* your town. The easiest place is your crew workspace:

```bash
cd ~/gt/YOUR_RIG/crew/claudio
```

> 💡 **Why the crew directory?** Gas Town detects your identity from your current working directory. Being in `crew/claudio` sets `BD_ACTOR=YOUR_RIG/crew/claudio` — so beads you create are attributed to you correctly.

If you don't have a crew workspace yet:
```bash
cd ~/gt
gt crew add claudio --rig YOUR_RIG
cd ~/gt/YOUR_RIG/crew/claudio
```

---

## 6. Fix the Dolt Fingerprint (If Needed)

If `bd create` fails with:
```
Error: failed to open database: database "your_rig" not found on Dolt server
```

Run `bd doctor` to diagnose:
```bash
cd ~/gt/YOUR_RIG/crew/claudio
bd doctor | head -20
```

If you see `Repo Fingerprint: Database belongs to different repository`:
```bash
echo "y" | bd migrate --update-repo-id
```

Then try `bd create` again.

---

## 7. Confirm Everything Works

```bash
cd ~/gt/YOUR_RIG/crew/claudio
bd ready
```

You should get a list of open beads (possibly some pre-existing ones — that's fine). If this runs without errors, you're ready.

---

## 8. Install the gt-toolkit Formulas (For Module 5)

Do this now so Module 5 is ready when you get there:

```bash
# Clone if you haven't already
git clone https://github.com/Xexr/gt-toolkit.git ~/source/gt-toolkit

# Install formulas to your town
cp ~/source/gt-toolkit/formulas/*.formula.toml ~/gt/.beads/formulas/

# Verify
gt formula list
```

---

## ✅ You're Ready When:

- [ ] `gt status` shows Witness + Refinery running for your rig
- [ ] `cd ~/gt/YOUR_RIG/crew/claudio && bd ready` runs without errors
- [ ] You know your rig name from `gt rig list`
- [ ] `gt formula list` shows spec-workflow, plan-workflow, beads-workflow

**→ [Module 0: The Mental Model](module-00-mental-model.md)**
