# Tutorial Issues Found (Student Run — March 2026)

Issues discovered by walking through the tutorial as a student. Each section maps to a fix needed.

---

## 🔴 Blockers (would stop a student cold)

### 1. `gt doctor` / `bd create` require being in `~/gt` (the town root)
**Where:** README Prerequisites / Module 1 Step 1  
**Problem:** Running `bd create` from anywhere outside the Gas Town workspace (`~/gt`) gives:
```
Error: database not initialized: issue_prefix config is missing
```
Running from the project repo (`~/source/gastown-workshop`) doesn't work.  
**Fix needed:** Add explicit "you must run Gas Town commands from `~/gt` or a crew workspace" note. The prereqs section should say: `cd ~/gt` before `gt doctor`.

### 2. `--notify --human` flag doesn't exist
**Where:** Module 1 Step 4, Module 3 Step 4, Module 4  
**Problem:** Tutorial says `--notify --human` but the real flag is just `--notify` (notifies mayor/) or `--notify <address>`.  
```
Error: unknown flag: --human
```
**Fix needed:** Replace all `--notify --human` with `--notify` throughout.

### 3. `gt polecat list --rig <name>` flag doesn't exist
**Where:** Module 1 Step 6, Module 3 Step 6, Module 6  
**Problem:** Tutorial uses `gt polecat list --rig edinsights_ui` but the real syntax is positional:
```
Error: unknown flag: --rig
```
Correct: `gt polecat list edinsights_ui`  
**Fix needed:** Fix all `--rig` flag references to positional argument.

### 4. `gt peek <name>` doesn't work outside a rig directory
**Where:** Module 1 Step 6  
**Problem:** `gt peek Toast` gives:
```
Error: not in a rig directory. Use full address format: gt peek <rig>/<polecat>
```
Correct: `gt peek edinsights_ui/furiosa`  
**Fix needed:** All `gt peek` examples need full address format `gt peek <rig>/<name>`.

### 5. `bd migrate --update-repo-id` required (not documented anywhere)
**Where:** Module 1 Step 1 (before bead creation works)  
**Problem:** On a fresh setup or after the rig's repo changed, `bd create` fails with:
```
Error: failed to open database: database "edinsights_ui" not found on Dolt server
```
`bd doctor` reveals `Repo Fingerprint: Database belongs to different repository` requiring `bd migrate --update-repo-id`.  
**Fix needed:** Add a "Setup Check" step before Module 1 that runs `bd doctor` and explains common errors. Or add to prereqs.

---

## 🟡 Confusing / Misleading (student would be confused but could recover)

### 6. Convoy not showing tracked beads in status
**Where:** Module 1 Step 4-5  
**Problem:** After `gt convoy create "name" edi-xxx`, `gt convoy status` shows `Progress: 0/0` — the bead doesn't appear as tracked. The docs say to use `bd dep add hq-cv-xxx edi-xxx --type=tracks` as a workaround, but that also didn't update the status display in testing. The bead WAS auto-linked (as shown by `○ Already tracked by convoy hq-cv-dsqp8` appearing on sling), but the status display is confusing.  
**Fix needed:** Note that `Progress: 0/0` is a display quirk until the bead is actually slung. Mention the auto-link behavior happens on `gt sling`.

### 7. `gt convoy create` progress counter shows 0/0 not 0/N
**Where:** Module 1 Step 5, Module 4  
**Problem:** Related to above — students expect to see `0/1 completed` after creating convoy with an issue. They see `0/0` which looks wrong.  
**Fix needed:** Explain this is normal; the counter updates once work is dispatched.

### 8. Tutorial uses generic `YOUR_RIG_NAME` but doesn't show how to find it
**Where:** Module 1 Step 5, Module 3 Step 4  
**Problem:** Students are told to run `gt sling edi-001 YOUR_RIG_NAME` without knowing their rig name. `gt rig list` is listed in prereqs but not called out at this step.  
**Fix needed:** Add `gt rig list` as the first command in Module 1 Step 5 with an explanation.

### 9. `gt feed` and `bd activity --follow` listed as equivalent but are different commands
**Where:** Module 1 Step 6  
**Problem:** Tutorial says `gt feed` for real-time activity. The cheatsheet lists both `gt feed` and `bd activity --follow`. They're different — `gt feed` is the Gas Town event stream, `bd activity` is the beads-level stream. Students don't know which to use or the difference.  
**Fix needed:** Clarify: `gt feed` for agent/system events (slings, handoffs, done signals); `bd activity --follow` for bead state changes.

### 10. `bd ready` shows pre-existing unrelated beads  
**Where:** Module 1 Step 3  
**Problem:** A real student's `bd ready` will show existing beads from prior work (like `edi-8nf` and `edi-rig-edinsights_ui`), not just the bead they just created. This is confusing.  
**Fix needed:** Add a note: "You'll see other existing beads here too — that's normal. Look for yours by ID."

### 11. `gt convoy stage` behavior not clear on what to pass (epic vs bead list)
**Where:** Module 4  
**Problem:** Tutorial says `gt convoy stage <epic-id>` but students at that point may not have an epic. The stage command expects a specific format.  
**Fix needed:** Show the actual command output more explicitly. Confirm whether `gt convoy stage` can take a convoy ID instead of an epic ID.

### 12. `bd create` priority format: tutorial says `-p P2` but earlier cheatsheet says `-p 2`
**Where:** Module 1 Step 1 (description uses "P2" format, older cheatsheet used "0-4")  
**Problem:** Inconsistency between "P2" and "2" in different places.  
**Fix needed:** Standardize on `P2` format throughout (what actually works).

---

## 🟢 Missing Content (gaps a student would hit)

### 13. No mention of `bd init` / `beads.role not configured` warning
**Where:** Prerequisites  
**Problem:** Students see `warning: beads.role not configured. Run 'bd init' to set.` on every `bd create`. Not explained anywhere.  
**Fix needed:** Add to prereqs: `cd ~/gt/YOUR_RIG/crew/YOUR_NAME && bd init` (or explain to ignore the warning for workshop purposes).

### 14. No prereq for Dolt being already running
**Where:** Prerequisites  
**Problem:** `gt doctor` shows "Daemon is not running" and `gt dolt status` may say stopped even if Dolt is running (process vs. server tracking issue). Students need to know to run `gt up` first.  
**Fix needed:** Add to Quick Start: `gt up` (bring up all services) before any other commands.

### 15. Module 1 "Try It" section referenced in README but doesn't exist
**Where:** README and each module  
**Problem:** README says "each module has a `## Try It` section" — but the modules use different section names (Step 1, Step 2, etc.). No `## Try It` section exists.  
**Fix needed:** Either rename the steps to "Try It" or fix the README claim.

### 16. No explanation of the `mol-polecat-work` formula that auto-applies
**Where:** Module 1 (happens automatically on sling)  
**Problem:** When slinging, students see:
```
Auto-applying mol-polecat-work for polecat work...
Instantiating formula mol-polecat-work...
✓ Formula wisp created: edi-wisp-8u18
```
This is unexpected and unexplained. What is `mol-polecat-work`? Why did it auto-apply?  
**Fix needed:** Brief explanation in Module 1 that Gas Town auto-attaches a work molecule to guide the polecat through the task. Reference molecules concept and point forward to Module 5.

### 17. The workshop repo needs to be linked to a rig (or students need their own rig)
**Where:** Module 1 and beyond  
**Problem:** The tutorial creates beads in `edinsights_ui` (Daniel's existing rig) but the workshop project lives in `~/source/gastown-workshop`. Students need to understand they're either (a) using an existing rig or (b) creating a new rig for the workshop.  
**Fix needed:** Add a "Setup" section explaining how to either use an existing rig or create a new one: `gt rig add gastown_workshop https://github.com/USERNAME/gastown-workshop`.

---

## 📋 Summary: Priority Fixes

| # | Issue | Priority | Module |
|---|-------|----------|--------|
| 1 | Must be in ~/gt to run commands | 🔴 Blocker | README + M1 |
| 2 | `--notify --human` flag wrong | 🔴 Blocker | M1, M3, M4 |
| 3 | `--rig` flag doesn't exist for polecat list | 🔴 Blocker | M1, M3, M6 |
| 4 | `gt peek` needs full address | 🔴 Blocker | M1, M3, M6 |
| 5 | `bd migrate` / Dolt fingerprint issue | 🔴 Blocker | Before M1 |
| 6 | Convoy 0/0 display quirk | 🟡 Confusing | M1 |
| 7 | `YOUR_RIG_NAME` not explained | 🟡 Confusing | M1 |
| 8 | `gt feed` vs `bd activity` | 🟡 Confusing | M1 |
| 9 | `bd ready` shows unrelated beads | 🟡 Confusing | M1 |
| 10 | `mol-polecat-work` auto-apply unexplained | 🟡 Confusing | M1 |
| 13 | `beads.role not configured` warning | 🟢 Missing | Prereqs |
| 14 | `gt up` not in Quick Start | 🟢 Missing | README |
| 17 | Workshop needs a rig | 🟢 Missing | Setup |
