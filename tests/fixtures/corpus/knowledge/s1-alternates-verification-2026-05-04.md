# S.1: Apple Speech alternates popover verification (5-min smoke)

**Status:** Queued for next time at the Mac. Sat ~12 days since session 53.
**Why now:** It's the only SoR (Branches S/O/R) verification item that doesn't need the Ubuntu inference host; closing it retires one of the three deferred items.
**Source runbook:** `knowledge/branches-sor-verification-runbook-2026-04-30.md` §S.1 (full context).
**Source plan:** `knowledge/follow-up-brief-2026-05-01.md` Task 3.

---

## Pre-flight (~2 min)

1. `./bin/build.sh && open Build/Untype.app`
2. Confirm menu-bar icon appears, no Dock icon.
3. System Settings to Privacy & Security: Microphone, Speech Recognition, Accessibility all granted to `Build/Untype.app`. Re-signed bundle preserves TCC via the stable `Untype Dev` identity.
4. Optional log terminal: `log stream --predicate 'process == "Untype"' --info --debug`

## Steps (~3 min)

1. Settings to Transcription Engine to **"Apple Speech (on-device)"**.
2. Hotkey (fn) to speak: *"I would like to test the alternate suggestions"* (or any phrase with a homophone candidate, e.g. *"I need a cup of coffin"*, Apple Speech reliably scores "coffee" as an alternate).
3. Confirm: text appears in Original view; polishing runs; insertion works into the focused app.
4. **Tap a word in the Original view** of the reviewing toast. Candidates popover should appear with ≥ 2 alternatives for at least one word.
5. Tap an alternate to confirm it replaces the segment in-place.
6. Insert to confirm the replaced text reaches the target app.

## Pass / Fail

- **PASS:** popover renders with alternates and tap-replace works end-to-end.
- **FAIL:** empty popover, no popover, or tap-replace doesn't propagate.

## After

- **On PASS:** append a one-line dated PASS entry to `knowledge/branches-sor-verification-runbook-2026-04-30.md` §S.1. Then this file can be deleted.
- **On FAIL:** file findings inline in that runbook + open an issue in `knowledge/issues.md`. Do NOT attempt a fix in this run, alternates code is a known fragile area; investigation needs its own scoped session.

## Why this exists as a standalone

The full SoR runbook covers Branches O and R as well, which both need an Ubuntu inference host that isn't currently up. S.1 is the orphan that only needs a Mac and a working microphone. Splitting it out makes it discoverable as a "do today" action separate from "wait for inference host."
