# Issues add A/B (skill vs no-skill)

The `issues` skill is a pure agent procedure (no backing script), so this is the cleanest "does the procedure help the agent" A/B of the three knowledge-kit skills. It targets the core `add` command against an already-populated tracker.

## What it measures

`setup.sh` builds a throwaway repo with a manifest (`issues_file` set) and a tracker holding ISS-001..005 in the skill's canonical format, plus two session logs. Both arms are asked to add the same new bug. `assert.py` checks three disciplines the skill encodes:

- `preserved`: all five planted entries survive (no data loss, the skill's "read the current file before writing" guideline).
- `seq`: exactly one new entry at the next sequential id (ISS-006), with no duplicate or skipped number.
- `schema`: the new entry carries the canonical fields (Status, Symptom, Root Cause, Fix).

## Isolation

Both arms run a fresh `claude -p --safe-mode` agent (no host CLAUDE.md, plugin, skills, or hooks; auth and tools intact). The skill arm gets the `issues` SKILL.md inlined; the control gets only the bare task. Both are given the same structured bug details, so the single variable is the skill's procedure. The entry format is discoverable from the existing tracker, which turns out to be central to the result.

## Run

```
sh run-ab.sh <skill|control> <model> [trial]
sh run-matrix.sh 3
python3 tally.py
```

`assert.py <repo>` scores the tracker file directly, never the agent's self-report. Per-trial transcripts land in `runs/` (git-ignored).

## Results

See `RESULTS.md`.
