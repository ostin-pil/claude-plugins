# Issues verify/search A/B (skill vs no-skill)

The `issues add` A/B (`../issues-ab/`) tied because the tracker is self-documenting. These two scenarios target the `issues` commands whose procedure is not visible in a single entry: `verify` (re-check fixes against the referenced files and transition status) and `search` (look across the tracker and the session logs, not just the tracker).

## verify

`setup-verify.sh` plants four "Resolved (verify)" issues, each naming a Fix marker and a referenced file. Two markers are still in their file (the fix held), two are gone (reverted). Two non-target issues (Open, Resolved) must not change. The skill's procedure is to find the Resolved (verify) issues, check the referenced files, and transition each to Resolved or Regressed. `assert-verify.py` scores the exact transitions, and breaks out two signals on the reverted pair: `detected` (did the agent notice the fix was gone at all, whatever word it used) and `regressed` (did it use the project's canonical status word). The gap between those two is where the skill's value turns out to live.

## search

`setup-search.sh` plants an issue whose only link to the query "thermal throttling" lives in a session log, not its tracker entry. The skill's search greps the tracker and the session logs; a tracker-only search misses it. `assert-search.py` scores the agent's report: did it cite the log-only match (ISS-207)?

## Isolation

Both arms run a fresh `claude -p --safe-mode` agent (no host CLAUDE.md, plugin, skills, or hooks; auth and tools intact). The skill arm inlines the `issues` SKILL.md; the control gets the goal but not the procedure (no "check the referenced files", no "Regressed" vocabulary, no "search the logs too"). The single variable is the skill.

## Run

```
sh run-ab.sh <verify|search> <skill|control> <model> [trial]
sh run-matrix.sh 3
python3 tally.py
```

`assert-verify.py <repo>` scores the tracker file; `assert-search.py <agent-log>` scores the agent's report. Per-trial transcripts land in `runs/` (git-ignored).

## Results

See `RESULTS.md`.
